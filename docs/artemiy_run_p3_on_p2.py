"""Participant 3 proxies (LOT Mixed, LOT Y-split, Gibbs) on participant 2's simulator.

Uses Rus's simulate / benchmark / race_table, so the numbers sit next to his Roll, Effective Tick, Zeros.
Usage: python run_p3_on_p2.py <path to participant2 folder> [n_stocks] [n_months]
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

P2 = Path(sys.argv[1]).resolve()
N_STOCKS = int(sys.argv[2]) if len(sys.argv) > 2 else 100
N_MONTHS = int(sys.argv[3]) if len(sys.argv) > 3 else 36
sys.path.insert(0, str(P2 / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from liquidity_sim import SimConfig, benchmark, simulate
from race_metrics import race_table
from spread_proxies import compute_panel
from participant3_proxies import compute_participant3_panel

BASE = pd.Timestamp("2000-01-01")


def to_p3_format(daily):
    """Rus's columns -> ours. He has month/day numbers, we need dates."""
    d = pd.DataFrame({
        "ticker": daily["stock"],
        "date": [BASE + pd.DateOffset(months=int(m), days=int(dd)) for m, dd in zip(daily["month"], daily["day"])],
        "ret": daily["ret"],
        "market_ret": daily["mkt_ret"],
        "price": daily["price"],
        "volume_shares": daily["volume"],
    })
    return d


def to_p2_index(panel, freq):
    """Our (ticker, period) -> his (stock, win)."""
    per = pd.PeriodIndex(panel["period"], freq=freq)
    if freq == "M":
        win = (per.year - BASE.year) * 12 + (per.month - 1)
    else:
        win = per.year - BASE.year
    out = panel.assign(stock=panel["ticker"].to_numpy(), win=np.asarray(win))
    return out.set_index(["stock", "win"]).sort_index()


if __name__ == "__main__":
    cfg = SimConfig(n_stocks=N_STOCKS, n_months=N_MONTHS, grid="eighths", cluster_strength=1.0, seed=1)
    daily, stocks = simulate(cfg)
    ours = to_p3_format(daily)

    tables = {}
    for freq, window in (("M", "month"), ("Y", "year")):
        t0 = time.time()
        p3 = compute_participant3_panel(ours, freq=freq, gibbs_kwargs={"no_trade": "midpoint"}, n_jobs=2)
        p3 = to_p2_index(p3, freq)
        p2 = compute_panel(daily, window, cfg.grid)
        bench = benchmark(daily, window)

        proxies = p2.join(p3[["lot_mixed", "lot_ysplit", "gibbs"]])
        units = ["roll", "eff_tick", "eff_tick2", "lot_mixed", "lot_ysplit", "gibbs"]
        tab = race_table(proxies, bench, units_cols=units).round(3)
        tables[window] = tab

        fails = {c: f"{1 - p3[c + '_success'].mean():.1%}" for c in ("lot_mixed", "lot_ysplit", "gibbs")}
        print(f"\n== {window}: {len(p3)} stock-{window}s, {time.time() - t0:.0f} s, failed: {fails}")
        print(tab.to_string())

    out = pd.concat(tables, axis=1)
    out.to_csv(Path(__file__).resolve().parent / "race_with_p3.csv")
    print("\nsaved race_with_p3.csv")
