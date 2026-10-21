import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import intraday_benchmarks as ib

DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "team_data"
OUT = ROOT / "results"


def load():
    t = pd.read_csv(DATA / "trades.csv.gz", parse_dates=["ts"]).rename(columns={"permno": "ticker"})
    q = pd.read_csv(DATA / "quotes.csv.gz", parse_dates=["ts"]).rename(columns={"permno": "ticker"})
    sm = pd.read_csv(DATA / "stock_month.csv").rename(columns={"permno": "ticker"})
    sm = sm[sm["true_spread_source"] == "intraday"].copy()
    sm["month"] = pd.PeriodIndex(sm["yyyymm"].astype(str), freq="M")
    return t, q, sm


def main():
    t, q, sm = load()
    lr = ib.monthly_benchmarks(t, q)
    tr = ib.monthly_benchmarks(t, q, sign="side")
    m = sm.merge(lr, on=["ticker", "month"]).merge(tr, on=["ticker", "month"], suffixes=("_lr", "_true"))
    pairs = {
        "effective spread, eq. 1": ("effective_spread_lr", "true_eff_spread"),
        "realized spread (mid 5 min), true side": ("realized_spread_mid_true", "true_realized_spread"),
        "realized spread (mid 5 min), Lee-Ready": ("realized_spread_mid_lr", "true_realized_spread"),
        "realized spread (trade 5 min, paper eq. 2), true side": ("realized_spread_true", "true_realized_spread"),
        "realized spread (trade 5 min, paper eq. 2), Lee-Ready": ("realized_spread_lr", "true_realized_spread"),
        "5-min price impact, true side": ("price_impact_5min_true", "true_price_impact_5min"),
        "5-min price impact, Lee-Ready": ("price_impact_5min_lr", "true_price_impact_5min"),
    }
    rows = {k: {"max_abs_diff": np.abs(m[a] - m[b]).max(), "corr": np.corrcoef(m[a], m[b])[0, 1],
                "mean_ratio": (m[a] / m[b]).mean()} for k, (a, b) in pairs.items()}
    res = pd.DataFrame(rows).T
    acc = ib.lee_ready_accuracy(t, q)
    OUT.mkdir(exist_ok=True)
    res.to_csv(OUT / "participant1_benchmark_check.csv")
    acc.to_csv(OUT / "participant1_lee_ready.csv", header=["value"])
    print(f"{len(m)} stock-months")
    print(res.round(4).to_string())
    print(acc.round(4).to_string())


if __name__ == "__main__":
    main()
