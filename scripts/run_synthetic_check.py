"""
Participant 2: test Roll, Effective Tick(2), Zeros(2) on synthetic data where
the true effective spread is known.

Experiments
  A. Baseline "horse race" on an 1/8 grid with full price clustering
     (monthly and annual windows)                 -> results/race_baseline.csv
  B. Clustering strength on a decimal grid (what decimalization did)
                                                   -> figures/fig_clustering.png
  C. Roll by spread decile and the share of months where the default 0 kicks in
                                                   -> figures/fig_roll_deciles.png
  D. Window length: how many days each proxy needs -> figures/fig_window.png
  E. Price clustering picture for the method slide -> figures/fig_cluster_hist.png
  F. Scatter proxy vs truth (baseline)             -> figures/fig_scatter.png

Run from the participant2 folder:   python scripts/run_synthetic_check.py
Runtime about 3-4 minutes.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
import matplotlib.ticker

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from liquidity_sim import SimConfig, benchmark, simulate
from race_metrics import avg_cs_corr, race_table, ts_corr
from spread_proxies import compute_panel, price_cluster

FIG, RES = ROOT / "figures", ROOT / "results"
FIG.mkdir(exist_ok=True)
RES.mkdir(exist_ok=True)

C = {"roll": "#2a78d6", "eff_tick": "#eb6834", "eff_tick2": "#1baf7a",
     "zeros": "#eda100", "zeros2": "#e87ba4"}
NAME = {"roll": "Roll", "eff_tick": "Effective Tick", "eff_tick2": "Effective Tick2",
        "zeros": "Zeros", "zeros2": "Zeros2"}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update({
    "font.size": 12, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.8, "lines.linewidth": 2, "figure.dpi": 150, "savefig.dpi": 220,
    "savefig.bbox": "tight", "axes.titleweight": "bold", "axes.titlesize": 13,
})

PAPER = pd.DataFrame({
    "cs_corr": [0.560, 0.626, 0.614, 0.427, 0.308],
    "ts_corr": [0.925, 0.941, 0.939, 0.874, 0.860],
    "mean_bias": [-0.002, -0.012, -0.013, np.nan, np.nan],
    "rmse": [0.032, 0.031, 0.032, np.nan, np.nan],
}, index=["roll", "eff_tick", "eff_tick2", "zeros", "zeros2"])


def run(cfg, windows=("month",)):
    daily, stocks = simulate(cfg)
    out = {}
    for w in windows:
        out[w] = (compute_panel(daily, w, cfg.grid), benchmark(daily, w))
    return daily, stocks, out


print("A. baseline race ...")
base_cfg = SimConfig(n_stocks=400, n_months=60, grid="eighths", cluster_strength=1.0, seed=1)
daily, stocks, res = run(base_cfg, windows=("month", "year"))
P_m, B_m = res["month"]
P_y, B_y = res["year"]
tab_m = race_table(P_m, B_m)
tab_y = race_table(P_y, B_y)
summary = pd.concat({"synthetic_monthly": tab_m, "synthetic_annual": tab_y,
                     "paper_monthly_TAQ": PAPER}, axis=1).round(3)
summary.to_csv(RES / "race_baseline.csv")
print(summary)
print("benchmark mean/median:", round(B_m.mean(), 4), round(B_m.median(), 4))

fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharex=True, sharey=True)
d = pd.concat([P_m, B_m], axis=1).dropna()
d = d.sample(4000, random_state=0)
for ax, c in zip(axes, ["roll", "eff_tick", "eff_tick2"]):
    ax.scatter(d["eff_spread"], d[c], s=8, alpha=0.35, color=C[c], edgecolor="none")
    lim = [0.002, 0.2]
    ax.plot(lim, lim, color=MUTED, lw=1, ls="--")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(lim); ax.set_ylim(0.0008, 0.3)
    r = tab_m.loc[c, "cs_corr"]
    ax.set_title(f"{NAME[c]}\navg. cross-sectional corr. {r:.2f}", color=INK)
    ax.set_xlabel("true effective spread")
axes[0].set_ylabel("proxy (one stock-month)")
fig.suptitle("Synthetic 1/8 grid, full clustering: proxy vs truth (4,000 random stock-months; "
             "Roll = 0 months are off the log scale)", x=0.01, y=1.06, ha="left", fontsize=12, color=MUTED)
fig.savefig(FIG / "fig_scatter.png")
plt.close(fig)

print("C. deciles ...")
d = pd.concat([P_m, B_m], axis=1).dropna().reset_index()
d["dec"] = d.groupby("win")["eff_spread"].transform(lambda x: pd.qcut(x, 10, labels=False)) + 1
rows = []
for k, g in d.groupby("dec"):
    port = g.groupby("win")[["roll", "eff_tick", "eff_tick2", "zeros", "eff_spread"]].mean()
    rows.append({"decile": k,
                 "roll": port["roll"].corr(port["eff_spread"]),
                 "eff_tick": port["eff_tick"].corr(port["eff_spread"]),
                 "eff_tick2": port["eff_tick2"].corr(port["eff_spread"]),
                 "zeros": port["zeros"].corr(port["eff_spread"]),
                 "roll_zero_share": (g["roll"] == 0).mean(),
                 "true_spread": g["eff_spread"].median()})
dec = pd.DataFrame(rows).set_index("decile")
dec.to_csv(RES / "deciles.csv")
print(dec.round(3))

fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.2))
for c in ["roll", "eff_tick", "eff_tick2"]:
    a1.plot(dec.index, dec[c], marker="o", ms=5, color=C[c], label=NAME[c])
a1.set_ylim(0, 1.05)
a1.set_xticks(range(1, 11))
a1.set_xlabel("decile of true spread (1 = most liquid)")
a1.set_ylabel("time-series corr., decile portfolio")
a1.set_title("Roll fails exactly where spreads are small", color=INK, loc="left")
a1.legend(frameon=False, loc="lower right")
a2.bar(dec.index, dec["roll_zero_share"] * 100, color=C["roll"], width=0.7)
for x, v in zip(dec.index, dec["roll_zero_share"] * 100):
    a2.text(x, v + 1, f"{v:.0f}", ha="center", fontsize=9, color=MUTED)
a2.set_xticks(range(1, 11))
a2.set_xlabel("decile of true spread (1 = most liquid)")
a2.set_ylabel("% of stock-months with Roll = 0")
a2.set_title("…because the autocovariance comes out positive", color=INK, loc="left")
fig.savefig(FIG / "fig_roll_deciles.png")
plt.close(fig)

print("D. window length ...")
wins = [1, 2, 3, 6, 12]
rows = []
for w in wins:
    P = compute_panel(daily, w, "eighths")
    B = benchmark(daily, w)
    rows.append({"months": w, **{c: avg_cs_corr(P[c], B) for c in ["roll", "eff_tick", "eff_tick2", "zeros"]}})
win = pd.DataFrame(rows).set_index("months")
win.to_csv(RES / "window_length.csv")
print(win.round(3))

fig, ax = plt.subplots(figsize=(7, 4.2))
offs = {"roll": -0.03, "eff_tick": 0.02, "zeros": 0}
for c in ["roll", "eff_tick", "zeros"]:
    ax.plot(win.index * 21, win[c], marker="o", ms=5, color=C[c])
    ax.text(win.index[-1] * 21 + 12, win[c].iloc[-1] + offs[c], NAME[c], color=INK, va="center", fontsize=11)
ax.set_xscale("log")
ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
ax.set_xticks(win.index * 21)
ax.set_xticklabels([f"{d}" for d in win.index * 21])
ax.set_xlim(18, 520)
ax.set_xlabel("trading days in the estimation window")
ax.set_ylabel("avg. cross-sectional corr. with truth")
ax.set_ylim(0, 1.02)
ax.set_title("Roll needs long windows, Effective Tick does not", color=INK, loc="left")
fig.savefig(FIG / "fig_window.png")
plt.close(fig)

print("B. clustering strength ...")
kappas = [1.0, 0.8, 0.6, 0.4, 0.2, 0.0]
rows = []
for k in kappas:
    cfg = SimConfig(n_stocks=300, n_months=36, grid="decimal", cluster_strength=k, seed=2)
    _, _, r = run(cfg)
    P, B = r["month"]
    t = race_table(P, B)
    rows.append({"kappa": k, **{f"{c}_cs": t.loc[c, "cs_corr"] for c in t.index},
                 **{f"{c}_bias": t.loc[c, "mean_bias"] for c in ["roll", "eff_tick", "eff_tick2"]}})
    print(f"  kappa={k}: " + ", ".join(f"{c}={t.loc[c, 'cs_corr']:.2f}" for c in t.index))
clus = pd.DataFrame(rows).set_index("kappa")
clus.to_csv(RES / "clustering_strength.csv")

fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.2))
x = clus.index * 100
for c in ["roll", "eff_tick", "eff_tick2", "zeros"]:
    a1.plot(x, clus[f"{c}_cs"], marker="o", ms=5, color=C[c])
    a1.text(x[0] + 3, clus[f"{c}_cs"].iloc[0], NAME[c], color=INK, va="center", fontsize=11)
a1.set_xlim(-5, 135)
a1.set_xticks([0, 20, 40, 60, 80, 100])
a1.set_ylim(0, 1.02)
a1.set_xlabel("% of quotes placed on round prices (κ)")
a1.set_ylabel("avg. cross-sectional corr. with truth")
a1.set_title("Decimal grid: clustering measures need clustering", color=INK, loc="left")
for c in ["roll", "eff_tick", "eff_tick2"]:
    a2.plot(x, clus[f"{c}_bias"] * 100, marker="o", ms=5, color=C[c])
    a2.text(x[0] + 3, clus[f"{c}_bias"].iloc[0] * 100, NAME[c], color=INK, va="center", fontsize=11)
a2.axhline(0, color=MUTED, lw=1)
a2.set_xlim(-5, 135)
a2.set_xticks([0, 20, 40, 60, 80, 100])
a2.set_xlabel("% of quotes placed on round prices (κ)")
a2.set_ylabel("mean bias, percentage points")
a2.set_title("…and underestimate the spread without it", color=INK, loc="left")
fig.savefig(FIG / "fig_clustering.png")
plt.close(fig)

print("E. cluster histogram ...")
tr = daily[daily["traded"]].merge(stocks[["sbar"]], left_on="stock", right_index=True)
liquid = tr[tr["sbar"] < tr["sbar"].quantile(0.1)]
illiq = tr[tr["sbar"] > tr["sbar"].quantile(0.9)]
labels = ["odd 1/8", "odd 1/4", "odd 1/2", "whole $"]
fig, ax = plt.subplots(figsize=(7, 4.2))
w = 0.38
for i, (g, lab, col) in enumerate([(liquid, "10% most liquid stocks", C["roll"]),
                                    (illiq, "10% least liquid stocks", C["eff_tick"])]):
    f = np.bincount(price_cluster(g["price"], "eighths"), minlength=4) / len(g)
    ax.bar(np.arange(4) + (i - 0.5) * w, f * 100, width=w - 0.03, color=col, label=lab)
    for j, v in enumerate(f * 100):
        ax.text(j + (i - 0.5) * w, v + 1, f"{v:.0f}%", ha="center", fontsize=9, color=MUTED)
uniform = [50, 25, 12.5, 12.5]
for j, u in enumerate(uniform):
    ax.plot([j - 0.42, j + 0.42], [u, u], color=INK, lw=1.2, ls=(0, (3, 2)))
ax.text(0.45, 51, "no clustering", fontsize=9, color=INK, va="bottom")
ax.set_xticks(range(4)); ax.set_xticklabels(labels)
ax.set_ylabel("% of closing prices")
ax.set_title("Wide spreads leave a footprint: round prices", color=INK, loc="left")
ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.02, 0.98))
fig.savefig(FIG / "fig_cluster_hist.png")
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 4.2))
order = ["roll", "eff_tick", "eff_tick2", "zeros", "zeros2"]
xs = np.arange(len(order))
ax.bar(xs - 0.2, PAPER.loc[order, "cs_corr"], width=0.38, color="#b9b8b2", label="paper (real data, TAQ)")
ax.bar(xs + 0.2, tab_m.loc[order, "cs_corr"], width=0.38, color=C["roll"],
       label="ours (synthetic)")
for x, v in zip(xs - 0.2, PAPER.loc[order, "cs_corr"]):
    ax.text(x, v + 0.015, f"{v:.2f}", ha="center", fontsize=9, color=MUTED)
for x, v in zip(xs + 0.2, tab_m.loc[order, "cs_corr"]):
    ax.text(x, v + 0.015, f"{v:.2f}", ha="center", fontsize=9, color=INK)
ax.set_xticks(xs); ax.set_xticklabels([NAME[c] for c in order])
ax.set_ylim(0, 1.08)
ax.set_ylabel("avg. cross-sectional corr.")
ax.set_title("Same ranking as Table 2, Panel A: Eff. Tick > Roll > Zeros", color=INK, loc="left")
ax.legend(frameon=False, loc="upper right")
fig.savefig(FIG / "fig_vs_paper.png")
plt.close(fig)

from PIL import Image

for src, dst in [("fig_clustering.png", "panel_clustering_corr.png"),
                 ("fig_roll_deciles.png", "panel_roll_deciles.png")]:
    im = Image.open(FIG / src)
    im.crop((0, 0, int(im.size[0] * 0.505), im.size[1])).save(FIG / dst)

print("done")
