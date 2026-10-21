"""Fill participant 5's slides (7, 9, 11, 15), Rus's 4 and 8, and Erik's 2, 3, 12, 13 in the shared deck from the race results.

    python scripts/build_deck.py [results_dir] [out.pptx]

Reads results/*.csv written by run_all.py and slides/deck_template_artemiy.pptx (slides 1-6, 8, 10, 12-14 belong
to other participants and are left untouched).
"""
import sys
from pathlib import Path

import pandas as pd
from pptx import Presentation
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Pt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import paper_numbers as paper
from pptx_helpers import (CARD, FAINT, INK, LEFT, MUTED, NAVY, PURPLE, WIDTH, WIN, add_card, add_chart,
                          add_text, remove_placeholder_text, set_notes, style_cell)

RES = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "slides" / "deck_final.pptx"
TEMPLATE = ROOT / "slides" / "deck_template_artemiy.pptx"
LABEL = {"roll": "Roll", "eff_tick": "Effective Tick", "eff_tick2": "Effective Tick2", "holden": "Holden",
         "gibbs": "Gibbs", "lot_mixed": "LOT Mixed", "lot_ysplit": "LOT Y-split", "zeros": "Zeros", "zeros2": "Zeros2"}
ROWS = ["roll", "eff_tick", "eff_tick2", "holden", "gibbs", "lot_mixed", "lot_ysplit", "zeros", "zeros2"]
PAPER_WIN = {"cs_corr": {"holden", "gibbs"}, "ts_corr": {"holden", "eff_tick", "eff_tick2", "lot_ysplit"},
             "mean_bias": {"roll"}, "rmse": {"holden", "gibbs"}}
Y0, FOOT = 1234430, 6238280


def fmt(v, d=3):
    if v is None or pd.isna(v):
        return "–"
    return f"{0.0 if round(v, d) == 0 else v:.{d}f}"


def slide_by_number(prs, n):
    return prs.slides[n - 1]


def slide7(s):
    remove_placeholder_text(s)
    gap, cw, ch, y = 190000, 2499100, 2830000, Y0
    cards = [
        ("Cross-sectional correlation", "Each month: correlate proxy and benchmark across the stocks, then average over months (Fama–MacBeth).",
         "Does the proxy rank stocks right?"),
        ("Time-series correlation", "Equally weighted portfolio of all stocks: correlate proxy and benchmark over time.",
         "Does it track market liquidity?"),
        ("Mean bias", "Average of (proxy − benchmark) over all stock-months.",
         "Is the level right? Only for proxies in spread units."),
        ("RMSE", "Root mean squared error computed each month, then averaged.",
         "Level and noise together. Not for Zeros, Amihud."),
    ]
    for i, (title, what, ask) in enumerate(cards):
        x = LEFT + i * (cw + gap)
        add_card(s, x, y, cw, ch)
        add_text(s, x + 190000, y + 200000, cw - 380000, 420000, title, size=17, bold=True, color=NAVY)
        add_text(s, x + 190000, y + 900000, cw - 380000, 1000000, what, size=13, color=INK)
        add_text(s, x + 190000, y + 1980000, cw - 380000, 230000, "QUESTION", size=11, bold=True, color=PURPLE)
        add_text(s, x + 190000, y + 2190000, cw - 380000, 560000, ask, size=13, color=INK)
    y2 = y + ch + 200000
    add_text(s, LEFT, y2, 6700000, 1300000, [
        [("Tests. ", True, NAVY), ("Difference of two correlations: t-test on the monthly series of differences, Newey–West with 4 lags (3 for annual).", False, INK)],
        [("Time-series correlations: Fisher's Z. RMSE: paired t-test. Theil's U² (U² = 1: no better than the mean).", False, INK)],
    ], size=13)
    add_text(s, LEFT + 6900000, y2, WIDTH - 6900000, 1160000, [
        [("“Winning” = the best value ", True, NAVY), ("plus every proxy statistically indistinguishable from it.", False, INK)],
        [("Our addition: Meng–Rosenthal–Rubin test, because all proxies share one benchmark.", False, MUTED)],
    ], size=13, fill=CARD)
    set_notes(s, "Four metrics, four different questions. Cross-sectional correlation is what matters if you sort stocks by liquidity. "
                 "Time-series correlation of the equally weighted portfolio is what matters for market-wide liquidity over time. "
                 "Bias and RMSE check the level, so only for proxies that are measured in the same units as the spread; Zeros, Amihud, "
                 "Gamma and Amivest are excluded. Differences of correlations are tested with a t-test on the monthly series of differences with "
                 "Newey-West errors, four lags monthly, three annual. Time-series correlations are compared with Fisher's Z. The paper never "
                 "says what 'winning' means statistically: it boxes the best measure and everything not significantly different from it, so the "
                 "winners are often a group. One technical point: Fisher's Z assumes independent correlations, but two proxies are correlated "
                 "with the same benchmark, so we also run the Meng-Rosenthal-Rubin test. In a Monte-Carlo check it has the right 5 percent size "
                 "while Fisher's test rejects too rarely. That is also the answer to the likely question why both correlation and RMSE: "
                 "correlation says whether the ranking is right, RMSE says whether the level is right; a proxy can have one without the other.")


def slide9(s, n_note):
    remove_placeholder_text(s)
    ours = pd.read_csv(RES / "table2_monthly.csv", index_col=0)
    winc = {"cs_corr": "win_cs", "ts_corr": "win_ts", "mean_bias": "win_bias", "rmse": "win_rmse"}
    metrics = [("cs_corr", "Cross-sect. corr", 3), ("ts_corr", "Time-series corr", 3),
               ("mean_bias", "Mean bias", 3), ("rmse", "RMSE", 3)]
    nr, nc = 2 + len(ROWS), 1 + 2 * len(metrics)
    top, rh = Y0 + 300000, 300000
    gt = s.shapes.add_table(nr, nc, LEFT, top, WIDTH, rh * nr)
    tbl = gt.table
    tblPr = gt._element.graphic.graphicData.tbl.tblPr
    tblPr.set("firstRow", "0")
    tblPr.set("bandRow", "0")
    style_id = tblPr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}tableStyleId")
    if style_id is not None:
        style_id.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"
    tbl.columns[0].width = 2150000
    for j in range(1, nc):
        tbl.columns[j].width = int((WIDTH - 2150000) / (nc - 1))
    for r in tbl.rows:
        r.height = rh
    style_cell(tbl.cell(0, 0), "", fill=NAVY)
    style_cell(tbl.cell(1, 0), "Proxy", size=12, bold=True, color=NAVY, align=PP_ALIGN.LEFT, fill=CARD)
    for k, (m, name, _) in enumerate(metrics):
        c0 = 1 + 2 * k
        tbl.cell(0, c0).merge(tbl.cell(0, c0 + 1))
        style_cell(tbl.cell(0, c0), name, size=13, bold=True, color="FFFFFF", fill=NAVY)
        style_cell(tbl.cell(1, c0), "Paper", size=12, bold=True, color=MUTED, fill=CARD)
        style_cell(tbl.cell(1, c0 + 1), "Ours", size=12, bold=True, color=NAVY, fill=CARD)
    for i, key in enumerate(ROWS):
        r = 2 + i
        style_cell(tbl.cell(r, 0), LABEL[key], size=13, bold=True, color=INK, align=PP_ALIGN.LEFT)
        for k, (m, _, d) in enumerate(metrics):
            c0 = 1 + 2 * k
            pv = paper.MONTHLY.loc[key, m]
            pw = key in PAPER_WIN[m]
            style_cell(tbl.cell(r, c0), fmt(pv, d), size=13, bold=pw, color=MUTED, fill=WIN if pw else None)
            if key in ours.index:
                ov = ours.loc[key, m]
                ow = bool(ours.loc[key, winc[m]]) if not pd.isna(ours.loc[key, winc[m]]) else False
                style_cell(tbl.cell(r, c0 + 1), fmt(ov, d), size=13, bold=ow, color=INK, fill=WIN if ow else None)
            else:
                style_cell(tbl.cell(r, c0 + 1), "not computed", size=10, color=FAINT)
    add_text(s, LEFT, Y0, WIDTH, 280000,
             "Benchmark: effective spread. Shaded bold = winner (best, or not significantly different from the best, 5 %).",
             size=12, color=MUTED)
    ytk = top + rh * nr + 110000
    add_text(s, LEFT, ytk, WIDTH, 860000, n_note["takeaway"], size=12, color=INK, fill=CARD)
    add_text(s, LEFT, ytk + 930000, WIDTH, 300000, n_note["footnote"], size=10, color=FAINT)
    set_notes(s, n_note["notes"])


def slide11(s, n_note):
    remove_placeholder_text(s)
    cs = pd.read_csv(RES / "tick_regimes_cs.csv", index_col=0)
    dow = pd.read_csv(RES / "dow.csv", index_col=0)
    half = (WIDTH - 300000) // 2
    xl, xr = LEFT, LEFT + half + 300000
    add_text(s, xl, Y0, half, 300000, "Decimalization: cross-sectional corr, synthetic",
             size=13, bold=True, color=NAVY)
    show = [("roll", "Roll"), ("eff_tick", "Effective Tick"), ("lot_ysplit", "LOT Y-split"), ("gibbs", "Gibbs"), ("zeros", "Zeros")]
    add_chart(s, xl, Y0 + 330000, half, 2900000, ["$1/8", "$1/16", "$0.01"],
              {n: [float(cs.loc[r, k]) for r in cs.index] for k, n in show}, kind="line",
              colors=["2A78D6", "EB6834", "4A3AA7", "52514E", "EDA100"], vmin=0, vmax=1, font=11)
    add_text(s, xr, Y0, half, 300000, "Dow stocks: time-series corr, annual", size=13, bold=True, color=NAVY)
    dshow = [("roll", "Roll"), ("eff_tick", "Eff. Tick"), ("lot_ysplit", "LOT Y"), ("gibbs", "Gibbs"), ("zeros", "Zeros")]
    add_chart(s, xr, Y0 + 330000, half, 2900000, [n for _, n in dshow],
              {"Paper (Table 9)": [float(dow.loc[k, "paper_ts_corr"]) for k, _ in dshow],
               "Synthetic Dow-like": [float(dow.loc[k, "ours_ts_corr"]) for k, _ in dshow]},
              kind="bar", colors=["EB6834", "2A78D6"], vmin=-1, vmax=1, font=11)
    add_text(s, xl, Y0 + 3300000, half, 560000, n_note["left"], size=12, color=INK)
    add_text(s, xr, Y0 + 3300000, half, 560000, n_note["right"], size=12, color=INK)
    add_text(s, LEFT, Y0 + 3950000, WIDTH, FOOT - (Y0 + 3950000) - 120000, n_note["takeaway"], size=13, color=INK, fill=CARD)
    set_notes(s, n_note["notes"])


def slide15(s, n_note):
    for sh in list(s.shapes):
        if sh.has_text_frame and sh.text_frame.text.startswith("[Filled in"):
            sh._element.getparent().remove(sh._element)
        elif sh.has_text_frame and sh.text_frame.text.startswith("[Repository link"):
            sh.text_frame.paragraphs[0].runs[0].text = n_note["repo"]
            sh.top = 5750000
        elif sh.shape_type == 14:
            sh.top = 700000
        elif sh.shape_type == 13:
            sh.top = 1450000
    add_text(s, LEFT, 1750000, 10883392, 3800000, n_note["bullets"], size=18, color="D9DFEC", space_after=14)
    set_notes(s, n_note["notes"])


def slide4(s):
    remove_placeholder_text(s)
    cards = [
        ("0.56", "Roll (1984)", "Bid–ask bounce makes price changes negatively autocorrelated.",
         ["S = 2·√(−Cov(Δpₜ, Δpₜ₋₁))", "0 if Cov ≥ 0"], "Liquid stocks, where volatility noise swamps S²/4."),
        ("0.63", "Effective Tick", "Wide spreads push trades onto round prices (Harris 1991).",
         ["cluster shares → γ̂ⱼ", "ET = Σ γ̂ⱼ sⱼ / P̄"], "No clustering, e.g. decimal prices and algorithmic quoting."),
        ("0.43", "Zeros (LOT 1999)", "Illiquid stocks often don’t trade, or trade without moving.",
         ["Zeros = #{rₜ = 0} / T", "Zeros2: volume > 0 only"], "Not in spread units: it ranks stocks but can’t give a level."),
    ]
    xs, cw, ch = [812800, 4402634, 7992517], 3386634, 3972322
    for x, (num, name, desc, formula, breaks) in zip(xs, cards):
        add_card(s, x, Y0, cw, ch)
        ix, iw = x + 228600, cw - 457200
        add_text(s, ix, Y0 + 170000, iw, 560000, num, size=34, bold=True, color=NAVY)
        add_text(s, ix, Y0 + 740000, iw, 230000, "avg. corr. with effective spread, paper", size=11, color=MUTED)
        add_text(s, ix, Y0 + 1060000, iw, 340000, name, size=20, bold=True, color=NAVY)
        add_text(s, ix, Y0 + 1450000, iw, 600000, desc, size=13, color=INK)
        add_text(s, ix, Y0 + 2150000, iw, 230000, "FORMULA", size=11, bold=True, color=PURPLE)
        add_text(s, ix, Y0 + 2380000, iw, 600000, formula, size=13, color=INK, font="Consolas")
        add_text(s, ix, Y0 + 3080000, iw, 230000, "BREAKS", size=11, bold=True, color=PURPLE)
        add_text(s, ix, Y0 + 3310000, iw, 560000, breaks, size=13, color=INK)
    add_text(s, LEFT, Y0 + ch + 170000, WIDTH, 300000,
             "Correlations: Table 2, Panel A (monthly, 400 stocks, 1993–2005, TAQ effective spread). Formulas: eq. (12), (13)–(16), (25)–(26).",
             size=11, color=MUTED)
    set_notes(s, "Three analytical proxies that need only daily prices. Roll: the bid-ask bounce makes consecutive price changes negatively "
                 "correlated, so the spread is twice the square root of minus the autocovariance, and zero when the covariance is positive. "
                 "Effective Tick: wide spreads push trades onto round prices (Harris), so the shares of prices on each round level give the "
                 "probability of each spread size, and the proxy is their weighted average divided by the average price. Zeros: the share of "
                 "zero-return days; Zeros2 counts only days with positive volume. The numbers on the cards are the paper's average cross-sectional "
                 "correlations with the effective spread. Each measure breaks somewhere: Roll on liquid stocks, because the spread is small next "
                 "to price noise (the paper's Dow sample, Table 9); Effective Tick when prices stop clustering, i.e. decimal prices and algorithmic "
                 "quoting; Zeros is not measured in spread units at all, so it can rank stocks but cannot give a level. (Speaker notes drafted from the slide.)")


def slide8(s):
    remove_placeholder_text(s)
    clus = pd.read_csv(RES / "clustering_strength.csv", index_col=0).sort_index()
    dec = pd.read_csv(RES / "deciles.csv", index_col=0)
    add_text(s, LEFT, Y0, WIDTH, 280000, "400 stocks × 60 months with a spread we set ourselves; one assumption changed at a time",
             size=13, color=MUTED)
    half = (WIDTH - 300000) // 2
    xl, xr, yc = LEFT, LEFT + half + 300000, Y0 + 420000
    add_text(s, xl, yc, half, 300000, "Decimal grid: clustering measures need clustering", size=13, bold=True, color=NAVY)
    add_chart(s, xl, yc + 300000, half, 3000000, [f"{int(round(k * 100))}" for k in clus.index],
              {"Roll": [float(v) for v in clus["roll_cs"]], "Effective Tick": [float(v) for v in clus["eff_tick_cs"]],
               "Effective Tick2": [float(v) for v in clus["eff_tick2_cs"]], "Zeros": [float(v) for v in clus["zeros_cs"]]},
              kind="line", colors=["2A78D6", "EB6834", "1BAF7A", "EDA100"], vmin=0, vmax=1, font=11)
    add_text(s, xl, yc + 3330000, half, 280000, "x: % of quotes on round prices (κ); y: avg. cross-sectional corr. with truth",
             size=11, color=MUTED)
    add_text(s, xr, yc, half, 300000, "Roll fails exactly where spreads are small", size=13, bold=True, color=NAVY)
    add_chart(s, xr, yc + 300000, half, 3000000, [str(i) for i in dec.index],
              {"Roll": [float(v) for v in dec["roll"]], "Effective Tick": [float(v) for v in dec["eff_tick"]],
               "Effective Tick2": [float(v) for v in dec["eff_tick2"]]},
              kind="line", colors=["2A78D6", "EB6834", "1BAF7A"], vmin=0, vmax=1, font=11)
    add_text(s, xr, yc + 3330000, half, 280000, "x: decile of true spread (1 = most liquid); y: time-series corr.",
             size=11, color=MUTED)
    add_text(s, LEFT, Y0 + 4400000, WIDTH, 420000,
             "Ours: scripts/run_synthetic_check.py. Same direction in the paper: Table 2 Panel C (decimal era), Panels D–E (large, low-spread "
             "stocks), Table 9 (Dow: Roll −0.64, a much stronger failure than here).", size=11, color=MUTED)
    set_notes(s, "We built stocks whose spread we set ourselves, so every proxy can be checked against the truth, and changed one assumption at a "
                 "time. Left: lower the share of quotes that sit on round prices, which is what decimalization and electronic quoting do. "
                 "Effective Tick falls from about 0.97 to 0.37, while Roll hardly moves and Zeros stays low. Right: sort stocks into deciles by the "
                 "true spread. Roll's time-series correlation rises from 0.39 in the lowest-spread decile to 0.92 in the highest, while Effective "
                 "Tick stays near 0.98. So each proxy breaks in its own place, which is also where the paper finds it breaking: the decimal era, "
                 "and large low-spread stocks. The paper's Dow result is a much stronger failure (Roll correlation of -0.64) than anything we get here. "
                 "(Speaker notes drafted from the slide.)")


def _parse_p1():
    import re
    txt = (ROOT / "docs" / "participant1_texts.md").read_text(encoding="utf-8")
    out = {}
    for part in re.split(r"^## Slide ", txt, flags=re.M)[1:]:
        num = int(part.split(".", 1)[0])
        d = {"bullets": [], "rows": []}
        for line in part.splitlines():
            if line.startswith("- "):
                d["bullets"].append(line[2:].strip())
            elif line.startswith("|") and not line.startswith("|---") and not line.startswith("| Benchmark"):
                d["rows"].append([c.strip().replace("\x00", "|") for c in line.replace("\\|", "\x00").strip().strip("|").split("|")])
            elif line.startswith("**Takeaway:**"):
                d["takeaway"] = line[len("**Takeaway:**"):].strip()
            elif line.startswith("**Notes:**"):
                d["notes"] = line[len("**Notes:**"):].strip()
        out[num] = d
    return out


def _clean(t):
    return t.replace("**", "")


def _takeaway(s, d, y, h=520000):
    add_text(s, LEFT, y, WIDTH, h, [[("Takeaway: ", True, NAVY), (_clean(d["takeaway"]), False, INK)]],
             size=13, fill=CARD, anchor=MSO_ANCHOR.MIDDLE)


def _cards(s, items, grid, top, bottom, size=11.5, head_size=13, gap=150000):
    """items: [(head, body)]; grid: list of columns, each the number of cards in it (a column may end with a free slot)."""
    cw = (WIDTH - gap * (len(grid) - 1)) // len(grid)
    k = 0
    for c, n in enumerate(grid):
        ch = (bottom - top - gap * (max(grid) - 1)) // max(grid)
        for r in range(n):
            head, body = items[k]
            k += 1
            x, y = LEFT + c * (cw + gap), top + r * (ch + gap)
            add_card(s, x, y, cw, ch)
            add_text(s, x + 170000, y + 120000, cw - 340000, ch - 160000,
                     [[(head, True, NAVY)], [(body, False, INK)]], size=size, space_after=3)
            s.shapes[-1].text_frame.paragraphs[0].runs[0].font.size = Pt(head_size)
    return cw, (bottom - top - gap * (max(grid) - 1)) // max(grid), gap


def _split_bullets(bullets, fallback_head):
    import re
    items = []
    for b in bullets:
        m = re.match(r"\*\*(.+?)\*\*\s*(.*)$", b)
        if m and not m.group(2).startswith(("is ", "not ")) and len(m.group(1)) < 60 and b.startswith("**"):
            items.append((m.group(1).rstrip(".:"), _clean(m.group(2))))
        else:
            items.append((fallback_head, _clean(b)))
    return items


def slide2(s, d):
    remove_placeholder_text(s)
    heads = ["Why liquidity matters", "Intraday data are scarce", "Earlier tests were thin", "The paper's horse race"]
    items = list(zip(heads, [_clean(b) for b in d["bullets"]]))
    items = [items[0], items[2], items[1], items[3]]
    bottom = Y0 + 3700000
    _cards(s, items, [2, 2], Y0, bottom, size=14, head_size=16, gap=190000)
    _takeaway(s, d, bottom + 190000, 700000)
    set_notes(s, d["notes"])


def slide3(s, d):
    remove_placeholder_text(s)
    rows = d["rows"]
    nr, rh = 1 + len(rows), 560000
    gt = s.shapes.add_table(nr, 3, LEFT, Y0, WIDTH, rh * nr)
    tbl = gt.table
    tblPr = gt._element.graphic.graphicData.tbl.tblPr
    tblPr.set("firstRow", "0")
    tblPr.set("bandRow", "0")
    sid = tblPr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}tableStyleId")
    if sid is not None:
        sid.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"
    for j, w in enumerate([2900000, 3700000, WIDTH - 6600000]):
        tbl.columns[j].width = w
    for r in tbl.rows:
        r.height = rh
    for j, h in enumerate(["Benchmark", "Formula", "Meaning"]):
        style_cell(tbl.cell(0, j), h, size=13, bold=True, color="FFFFFF", fill=NAVY, align=PP_ALIGN.LEFT)
    for i, row in enumerate(rows, start=1):
        fill = CARD if i % 2 == 0 else None
        for j, t in enumerate(row):
            style_cell(tbl.cell(i, j), _clean(t), size=12.5 if j else 13, bold=(j == 0), color=NAVY if j == 0 else INK,
                       fill=fill, align=PP_ALIGN.LEFT)
    _takeaway(s, d, Y0 + rh * nr + 170000, 520000)
    set_notes(s, d["notes"])


def _critique(s, d, fallback_head):
    remove_placeholder_text(s)
    items = _split_bullets(d["bullets"], fallback_head)
    bottom = FOOT - 200000
    cw, ch, gap = _cards(s, items, [4, 3], Y0, bottom, size=10, head_size=12, gap=100000)
    x, y = LEFT + cw + gap, Y0 + 3 * (ch + gap)
    add_text(s, x, y, cw, ch, [[("Takeaway", True, NAVY)], [(_clean(d["takeaway"]), False, INK)]],
             size=12, fill=WIN, anchor=MSO_ANCHOR.MIDDLE, space_after=3)
    set_notes(s, d["notes"])


def slide12(s, d):
    _critique(s, d, "Critique")


def slide13(s, d):
    _critique(s, d, "Selection, not fitting")


def fix_slide5(prs):
    s = prs.slides[4]
    for sh in s.shapes:
        if sh.has_text_frame and sh.text_frame.text.startswith("Y-split is consistent"):
            r = sh.text_frame.paragraphs[0].runs
            r[0].text = "Y-split is consistent with the model and among the winners; Mixed roughly doubles the spread in our simulation (mean 0.039 vs. true 0.018)"
            for x in r[1:]:
                x.text = ""
    if s.has_notes_slide:
        tf = s.notes_slide.notes_text_frame
        tf.text = tf.text.replace("Mixed overstates the spread, by about 20 to 25 percent in our simulation.",
                                  "Mixed overstates the spread: in our simulation its average is 0.039 against a true 0.018, about twice as large, while Y-split is within 5 percent.")


def merge_participant4(prs):
    """Slides 6 and 10 are participant 4's: copy their shapes and notes from his deck into ours."""
    import copy
    src = Presentation(ROOT / "slides" / "deck_tokha.pptx")
    keep = {"Text 0", "Image 0", "Text 2", "Text 3"}
    for n in (6, 10):
        dst, his = prs.slides[n - 1], src.slides[n - 1]
        for sh in list(dst.shapes):
            if sh.name not in keep:
                sh._element.getparent().remove(sh._element)
        for sh in his.shapes:
            if sh.name not in keep:
                dst.shapes._spTree.append(copy.deepcopy(sh._element))
        if his.has_notes_slide:
            set_notes(dst, his.notes_slide.notes_text_frame.text)
    from pptx.util import Pt
    for sh in prs.slides[5].shapes:
        if sh.name in ("TextBox 18", "TextBox 15"):
            for r in sh.text_frame.paragraphs[0].runs:
                r.font.size = Pt(18 if sh.name == "TextBox 18" else 11.5)


def main(texts):
    prs = Presentation(TEMPLATE)
    slide7(slide_by_number(prs, 7))
    slide9(slide_by_number(prs, 9), texts["s9"])
    slide11(slide_by_number(prs, 11), texts["s11"])
    slide15(slide_by_number(prs, 15), texts["s15"])
    slide4(slide_by_number(prs, 4))
    slide8(slide_by_number(prs, 8))
    fix_slide5(prs)
    p1 = _parse_p1()
    slide2(slide_by_number(prs, 2), p1[2])
    slide3(slide_by_number(prs, 3), p1[3])
    slide12(slide_by_number(prs, 12), p1[12])
    slide13(slide_by_number(prs, 13), p1[13])
    if (ROOT / "slides" / "deck_tokha.pptx").exists():
        merge_participant4(prs)
    prs.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    from deck_texts import TEXTS
    main(TEXTS)
