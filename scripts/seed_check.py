"""Robustness: baseline race (cross-sectional corr.) on 5 random seeds.
Run from the participant2 folder:  python scripts/seed_check.py   (~1 min)"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from liquidity_sim import SimConfig, benchmark, simulate
from race_metrics import race_table
from spread_proxies import compute_panel

cols = {}
for seed in [1, 2, 3, 4, 5]:
    d, _ = simulate(SimConfig(n_stocks=400, n_months=60, seed=seed))
    cols[f"seed_{seed}"] = race_table(compute_panel(d), benchmark(d))["cs_corr"]
r = pd.DataFrame(cols)
r["mean"] = r.mean(axis=1)
r["sd"] = r.iloc[:, :5].std(axis=1)
r.round(4).to_csv(ROOT / "results" / "seed_robustness.csv")
print(r.round(3))
