"""Run the whole project: simulate -> all proxies -> horse race -> tables, figures.

    python scripts/run_all.py            # uses cached proxies if present (results/cache), else builds them (~25 min)
    python scripts/run_all.py --rebuild  # rebuild the proxies from scratch

Outputs: results/*.csv, results/summary.md, figures/*.png
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import paper_numbers as paper
import race_engine as eng
from pipeline import LABEL, SCENARIOS, UNITS, build_scenario

RES, FIG = ROOT / "results", ROOT / "figures"
RES.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

OURS = ["roll", "eff_tick", "eff_tick2", "zeros", "zeros2", "lot_mixed", "lot_ysplit", "gibbs"]
COLOR = {"roll": "#2a78d6", "eff_tick": "#eb6834", "eff_tick2": "#1baf7a", "zeros": "#eda100",
         "zeros2": "#e87ba4", "lot_mixed": "#8b6bd9", "lot_ysplit": "#4a3aa7", "gibbs": "#52514e"}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 12, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "figure.dpi": 150, "savefig.dpi": 220,
                     "savefig.bbox": "tight", "axes.titleweight": "bold"})


def race_of(sc: dict, window: str) -> eng.Race:
    d = sc[window]
    return eng.Race(d["proxies"], d["bench"], units=UNITS, window=window)


def stars(t: pd.DataFrame, labels=LABEL) -> pd.DataFrame:
    return eng.format_table(t, labels)


def compare_with_paper(ours: pd.DataFrame, theirs: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in ours.columns if c in theirs.columns]
    keep = [p for p in ours.index if p in theirs.index]
    out = {}
    for c in cols:
        out[(c, "ours")] = ours.loc[keep, c]
        out[(c, "paper")] = theirs.loc[keep, c]
    return pd.DataFrame(out)


def main(rebuild: bool = False):
    data = {n: build_scenario(n, force=rebuild) for n in SCENARIOS}
    summary = ["# Results of the synthetic horse race\n"]

    for window, scen, name, pap in (("month", "main", "table2_monthly", paper.MONTHLY),
                                    ("year", "annual", "table3_annual", paper.ANNUAL)):
        r = race_of(data[scen], window)
        t = r.table()
        t.to_csv(RES / f"{name}.csv")
        stars(t).to_csv(RES / f"{name}_marked.csv")
        r.diff_p_cs().to_csv(RES / f"{name}_pvalues_cs.csv")
        r.diff_p_ts("fisher").to_csv(RES / f"{name}_pvalues_ts_fisher.csv")
        r.diff_p_ts("mrr").to_csv(RES / f"{name}_pvalues_ts_mrr.csv")
        pb = r.panel_b()
        pb.to_csv(RES / f"{name}_panelB.csv")
        compare_with_paper(t, pap).round(3).to_csv(RES / f"{name}_vs_paper.csv")
        summary.append(f"## {name}  ({len(data[scen][window]['proxies'])} stock-windows)\n")
        summary.append(stars(t).to_markdown() + "\n\n`*` = best or statistically indistinguishable from the best (5 %).\n")
        summary.append("Winners: cross-sectional corr: " + ", ".join(LABEL[c] for c in t.index if t.loc[c, "win_cs"] is True or t.loc[c, "win_cs"] == True)
                       + "; time-series corr (Fisher, paper): " + ", ".join(LABEL[c] for c in pb.index if pb.loc[c, "winner"] == True)
                       + "; time-series corr (Meng-Rosenthal-Rubin): " + ", ".join(LABEL[c] for c in pb.index if pb.loc[c, "winner_mrr"] == True) + "\n")

    d = data["main"]["month"]
    size_lab = eng.decile_labels(d["meta"]["size"])
    spr_lab = eng.decile_labels(d["bench"])
    dec_size = eng.ts_corr_by_group(d["proxies"], d["bench"], size_lab)
    dec_spr = eng.ts_corr_by_group(d["proxies"], d["bench"], spr_lab)
    dec_size.round(4).to_csv(RES / "deciles_size_ts.csv")
    dec_spr.round(4).to_csv(RES / "deciles_spread_ts.csv")
    summary.append("## Time-series correlation by size decile (1 = smallest; size = average daily dollar volume)\n")
    summary.append(dec_size.rename(columns=LABEL).round(3).to_markdown() + "\n")
    summary.append("## Time-series correlation by effective-spread decile (1 = lowest spread)\n")
    summary.append(dec_spr.rename(columns=LABEL).round(3).to_markdown() + "\n")

    regimes = {"1993-96 ($1/8)": "era_eighths", "1997-2000 ($1/16)": "era_sixteenths", "2001-05 ($0.01)": "era_decimal"}
    ts_reg, cs_reg = {}, {}
    for lab, nm in regimes.items():
        e = data[nm]["month"]
        r = eng.Race(e["proxies"], e["bench"], units=UNITS)
        ts_reg[lab] = r.panel_b()["ts_corr"]
        cs_reg[lab] = r.panel_a()["cs_corr"]
    ts_reg, cs_reg = pd.DataFrame(ts_reg).T, pd.DataFrame(cs_reg).T
    ts_reg.round(4).to_csv(RES / "tick_regimes_ts.csv")
    cs_reg.round(4).to_csv(RES / "tick_regimes_cs.csv")
    summary.append("## Tick regimes: average cross-sectional correlation\n")
    summary.append(cs_reg.rename(columns=LABEL).round(3).to_markdown() + "\n")
    summary.append("## Tick regimes: time-series correlation\n")
    summary.append(ts_reg.rename(columns=LABEL).round(3).to_markdown() + "\n")

    dw = data["dow"]["year"]
    rdw = eng.Race(dw["proxies"], dw["bench"], units=UNITS, window="year")
    pdw = rdw.panel_b()
    dow = pd.DataFrame({"ours_ts_corr": pdw["ts_corr"], "ours_t": pdw["t_vs_0"],
                        "paper_ts_corr": paper.DOW_TS.reindex(pdw.index)})
    dow.round(4).to_csv(RES / "dow.csv")
    summary.append("## Dow-like sample (30 stocks, 39 years, annual): time-series correlation\n")
    summary.append(dow.rename(index=LABEL).round(3).to_markdown() + "\n")

    (RES / "summary.md").write_text("\n".join(summary))
    make_figures(data, dec_size, ts_reg, cs_reg, dow)
    print("\n".join(summary))


def make_figures(data, dec_size, ts_reg, cs_reg, dow):
    show = ["roll", "eff_tick", "gibbs", "lot_ysplit", "zeros"]
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2), sharey=False)
    for c in show:
        ax[0].plot(range(3), cs_reg[c], marker="o", color=COLOR[c], label=LABEL[c])
    ax[0].set_xticks(range(3), ["$1/8", "$1/16", "$0.01"])
    ax[0].set_title("Synthetic: cross-sectional corr")
    ax[0].set_ylim(0, 1)
    for c in [s for s in show if s in paper.TICK_REGIMES_TS.columns]:
        ax[1].plot(range(3), paper.TICK_REGIMES_TS[c], marker="o", color=COLOR[c], label=LABEL[c])
    ax[1].set_xticks(range(3), ["$1/8", "$1/16", "$0.01"])
    ax[1].set_title("Paper: time-series corr (Table 2, C)")
    ax[1].set_ylim(0, 1)
    ax[1].legend(frameon=False, fontsize=10, loc="lower left")
    fig.savefig(FIG / "fig_tick_regimes.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.2))
    names = [c for c in OURS if c in dow.index]
    x = np.arange(len(names))
    ax.bar(x - 0.2, dow.loc[names, "ours_ts_corr"], 0.4, label="Synthetic Dow-like", color="#2a78d6")
    ax.bar(x + 0.2, dow.loc[names, "paper_ts_corr"], 0.4, label="Paper (Table 9)", color="#eb6834")
    ax.axhline(0, color=MUTED, lw=1)
    ax.set_xticks(x, [LABEL[c] for c in names], rotation=25, ha="right")
    ax.set_ylabel("time-series correlation, annual")
    ax.legend(frameon=False)
    fig.savefig(FIG / "fig_dow.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.2))
    for c in ["roll", "eff_tick", "gibbs", "lot_ysplit"]:
        ax.plot(dec_size.index, dec_size[c], marker="o", color=COLOR[c], label=LABEL[c])
    ax.set_xlabel("size decile (1 = smallest)")
    ax.set_ylabel("time-series correlation")
    ax.legend(frameon=False, fontsize=10)
    fig.savefig(FIG / "fig_size_deciles.png")
    plt.close(fig)


if __name__ == "__main__":
    main(rebuild="--rebuild" in sys.argv)
