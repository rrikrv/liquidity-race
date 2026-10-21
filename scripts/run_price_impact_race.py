"""Price-impact race (participant 4's panel) through the common race engine: same numbers, plus the
Meng-Rosenthal-Rubin test for the time-series panel.   python scripts/run_price_impact_race.py
Needs results/price_impact/spread_panel_baseline_120x48_s1.pkl (made by run_price_impact_check.py)."""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import portable
import race_engine as eng
from impact_sim import ImpactSimConfig, impact_benchmarks, simulate_impact
from price_impact_proxies import IMPACT_ORDER, LABELS, add_extended_proxies, compute_impact_panel

RES = ROOT / "results" / "price_impact"
cfg = ImpactSimConfig(n_stocks=120, n_months=48, grid="eighths", cluster_strength=1.0, seed=1, impact_scale=0.3, impact_liq_link=1.0)
daily, _ = simulate_impact(cfg)
spread = portable.load(RES / "spread_panel_baseline_120x48_s1.pkl")
proxies = add_extended_proxies(compute_impact_panel(daily, "month"), spread)
bench = impact_benchmarks(daily, "month")
common = proxies.index.intersection(bench.index)
proxies, bench = proxies.loc[common], bench.loc[common]

rows = []
for b in ("lambda_true", "post_impact_true"):
    r = eng.Race(proxies, bench[b], window="month")
    a, t = r.panel_a(), r.panel_b()
    for c in proxies.columns:
        rows.append({"benchmark": b, "proxy": c, "A_cs_corr": a.loc[c, "cs_corr"], "A_winner": bool(a.loc[c, "winner"]),
                     "B_ts_corr": t.loc[c, "ts_corr"], "B_winner_fisher": bool(t.loc[c, "winner"]), "B_winner_mrr": bool(t.loc[c, "winner_mrr"])})
out = pd.DataFrame(rows)
out.round(4).to_csv(RES / "table4_engine_check.csv", index=False)

old = pd.read_csv(RES / "table4_synthetic_baseline.csv", index_col=0)
for b in ("lambda_true", "post_impact_true"):
    for panel, col in (("A", "A_cs_corr"), ("B", "B_ts_corr")):
        mine = out[out.benchmark == b].set_index("proxy")[col]
        theirs = old.loc[f"Panel {panel}: {b}"]
        print(f"{b} panel {panel}: max |engine - participant 4| = {(mine - theirs[mine.index]).abs().max():.2e}")
    w = out[out.benchmark == b].set_index("proxy")
    print("  leaders A:", [LABELS[c] for c in w.index if w.loc[c, "A_winner"]])
    print("  leaders B (Fisher):", [LABELS[c] for c in w.index if w.loc[c, "B_winner_fisher"]])
    print("  leaders B (MRR):   ", [LABELS[c] for c in w.index if w.loc[c, "B_winner_mrr"]])
