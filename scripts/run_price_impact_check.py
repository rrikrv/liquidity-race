from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results" / "price_impact"
RES.mkdir(parents=True, exist_ok=True)

ap = argparse.ArgumentParser()
ap.add_argument("--stocks", type=int, default=150)
ap.add_argument("--months", type=int, default=60)
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--impact-scale", type=float, default=0.15)
ap.add_argument("--jobs", type=int, default=2)
ap.add_argument("--tag", default="baseline")
ap.add_argument("--no-cache", action="store_true")
ap.add_argument("--skip-p3", action="store_true")
ap.add_argument("--link", type=float, default=1.0)
args = ap.parse_args()

sys.path.insert(0, str(ROOT / "src"))

import portable
from impact_race import impact_race_tables, summary_wide
from impact_sim import ImpactSimConfig, impact_benchmarks, simulate_impact
from participant3_proxies import compute_participant3_panel
from price_impact_proxies import IMPACT_ORDER, add_extended_proxies, compute_impact_panel
from spread_proxies import compute_panel

BASE = pd.Timestamp("2000-01-01")


def to_p3_format(daily):
    return pd.DataFrame({
        "ticker": daily["stock"],
        "date": [BASE + pd.DateOffset(months=int(m), days=int(d)) for m, d in zip(daily["month"], daily["day"])],
        "ret": daily["ret"],
        "market_ret": daily["mkt_ret"],
        "price": daily["price"],
        "volume_shares": daily["volume"],
    })


def p3_month_panel(daily):
    p3 = compute_participant3_panel(to_p3_format(daily), freq="M", gibbs_kwargs={"no_trade": "midpoint"}, n_jobs=args.jobs)
    per = pd.PeriodIndex(p3["period"], freq="M")
    win = (per.year - BASE.year) * 12 + (per.month - 1)
    out = p3.assign(stock=p3["ticker"].to_numpy(), win=np.asarray(win)).set_index(["stock", "win"]).sort_index()
    return out[["lot_mixed", "lot_ysplit", "gibbs"]]


cfg = ImpactSimConfig(n_stocks=args.stocks, n_months=args.months, grid="eighths", cluster_strength=1.0,
                      seed=args.seed, impact_scale=args.impact_scale, impact_liq_link=args.link)
t0 = time.time()
daily, stocks = simulate_impact(cfg)
print(f"simulated {args.stocks} stocks x {args.months} months in {time.time() - t0:.0f} s")

cache = RES / f"spread_panel_{args.tag}_{args.stocks}x{args.months}_s{args.seed}.pkl"
if cache.exists() and not args.no_cache:
    spread = portable.load(cache)
    print("spread proxies loaded from", cache.name)
else:
    t0 = time.time()
    p2 = compute_panel(daily, "month", cfg.grid)
    print(f"participant 2 proxies: {time.time() - t0:.0f} s")
    if args.skip_p3:
        spread = p2
    else:
        t0 = time.time()
        p3 = p3_month_panel(daily)
        print(f"participant 3 proxies: {time.time() - t0:.0f} s")
        spread = p2.join(p3)
        portable.dump(spread, cache)

impact = compute_impact_panel(daily, "month")
proxies = add_extended_proxies(impact, spread)
bench = impact_benchmarks(daily, "month")
print(bench.describe().loc[["count", "mean", "50%"]].to_string())
print("corr obs vs true:", bench.corr().loc[["lambda_obs", "post_impact_obs"], ["lambda_true", "post_impact_true"]].round(3).to_dict())

bench.corr().round(4).to_csv(RES / f"benchmark_corr_{args.tag}.csv")
bench.describe().to_csv(RES / f"benchmark_describe_{args.tag}.csv")
common = proxies.index.intersection(bench.index)
proxies, bench = proxies.loc[common], bench.loc[common]
tables = impact_race_tables(proxies, bench)
wide = summary_wide(tables)
wide = wide[[c for c in IMPACT_ORDER if c in wide.columns]]
print(wide.round(3).to_string())

wide.round(6).to_csv(RES / f"table4_synthetic_{args.tag}.csv")
rows = []
for (panel, name), t in tables.items():
    for proxy, r in t.iterrows():
        rows.append({"panel": panel, "benchmark": name, "proxy": proxy, "corr": r["corr"],
                     "best": r["best"], "in_leader_group": r["in_leader_group"],
                     "insignificantly_different_from": r["insignificantly_different_from"]})
pd.DataFrame(rows).to_csv(RES / f"table4_leaders_{args.tag}.csv", index=False)
print("saved results for", args.tag)
