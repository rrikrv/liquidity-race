import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import intraday_benchmarks as ib
import participant1_data as d
import pipeline as P
import portable
import race_engine as eng
from participant3_proxies import compute_participant3_panel
from spread_proxies import compute_panel


def proxies_for(daily, grid, n_jobs):
    p2 = compute_panel(daily, "month", grid)
    f = pd.DataFrame({"ticker": daily["stock"], "date": daily["date"], "ret": daily["ret"], "market_ret": daily["mkt_ret"],
                      "price": daily["price"], "volume_shares": daily["volume"]})
    p3 = compute_participant3_panel(f, freq="M", n_jobs=n_jobs, gibbs_kwargs=P.SCENARIOS["main"].gibbs)
    return p2.join(P._p3_to_index(p3, "M")[["lot_mixed", "lot_ysplit", "gibbs"]], how="left")[P.PROXIES]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", choices=["moex", "yahoo", "binance"])
    ap.add_argument("--tickers", nargs="+", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--market", default="BTCUSDT")
    ap.add_argument("--grid", default="decimal")
    ap.add_argument("--quote-resample", default="100ms")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--out", default=str(ROOT / "results" / "real"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    bench = None

    if a.source == "moex":
        raw = d.load_moex_daily(a.tickers, a.start, a.end)
        panel = d.build_daily_panel(raw, d.load_moex_index(a.start, a.end), d.load_moex_ticksize())
    elif a.source == "yahoo":
        raw, mkt = d.load_yahoo_daily(a.tickers, a.start, a.end)
        panel = d.build_daily_panel(raw, mkt)
    else:
        months = [p.strftime("%Y-%m") for p in pd.period_range(a.start, a.end, freq="M")]
        days = [x.strftime("%Y-%m-%d") for x in pd.date_range(a.start, a.end, freq="D")]
        syms = list(dict.fromkeys(a.tickers + [a.market]))
        trades = {s: d.load_binance_trades(s, months) for s in syms}
        m = d.daily_from_trades(trades[a.market]).sort_values("date")
        mkt = pd.DataFrame({"date": m["date"], "mkt_ret": m["price"].pct_change()})
        raw = pd.concat([d.daily_from_trades(trades[s]) for s in a.tickers], ignore_index=True)
        panel = d.build_daily_panel(raw, mkt)
        bm, acc = [], []
        for s in a.tickers:
            q = d.load_binance_quotes(s, days, resample=a.quote_resample)
            bm.append(ib.monthly_benchmarks(trades[s], q))
            acc.append(ib.lee_ready_accuracy(trades[s], q).rename(s))
        bm = pd.concat(bm, ignore_index=True)
        bm.to_csv(out / "benchmarks_monthly.csv", index=False)
        pd.concat(acc, axis=1).T.to_csv(out / "lee_ready_accuracy.csv")
        bench = ib.to_engine(bm)

    panel.to_csv(out / "daily_panel.csv", index=False)
    daily = d.to_repo_daily(panel)
    proxies = proxies_for(daily, a.grid, a.jobs)
    proxies.to_csv(out / "proxies_monthly.csv")
    portable.dump({"proxies": proxies, "bench": bench}, out / "real.pkl")
    if bench is not None:
        idx = proxies.index.intersection(bench.index)
        t = eng.Race(proxies.loc[idx], bench.loc[idx], units=P.UNITS).table()
        t.to_csv(out / "race_real.csv")
        print(eng.format_table(t, P.LABEL).to_string())


if __name__ == "__main__":
    main()
