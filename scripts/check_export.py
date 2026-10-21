"""Independent check of team_data/ from the CSV files alone, the way participant 1 will use them:
effective spread from trades + quotes must equal true_eff_spread; Lee-Ready accuracy; daily consistency.
Run:  python scripts/check_export.py"""
from pathlib import Path

import numpy as np
import pandas as pd

D = Path(__file__).resolve().parents[1] / "team_data"
tr = pd.read_csv(D / "trades.csv.gz", parse_dates=["ts"])
q = pd.read_csv(D / "quotes.csv.gz", parse_dates=["ts"])
daily = pd.read_csv(D / "daily.csv.gz", parse_dates=["date"])
sm = pd.read_csv(D / "stock_month.csv")

q["mid"] = (q["bid"] + q["ask"]) / 2
q["date"] = q["ts"].dt.normalize()
tr["date"] = tr["ts"].dt.normalize()
t = pd.merge_asof(tr.sort_values("ts"), q[["ts", "permno", "date", "mid"]].sort_values("ts"),
                  on="ts", by=["permno", "date"], direction="backward")

t["dv"] = t["price"] * t["size"]
t["eff"] = 2 * np.abs(np.log(t["price"]) - np.log(t["mid"]))
t["yyyymm"] = t["ts"].dt.year * 100 + t["ts"].dt.month
eff = t.groupby(["permno", "yyyymm"]).apply(lambda g: np.average(g["eff"], weights=g["dv"]),
                                            include_groups=False).rename("mine").reset_index()
m = eff.merge(sm, on=["permno", "yyyymm"])
print(f"effective spread: {len(m)} stock-months, max |mine - true_eff_spread| = "
      f"{(m['mine'] - m['true_eff_spread']).abs().max():.2e}")

t = t.sort_values(["permno", "ts"])
dp = t.groupby(["permno", "date"])["price"].diff()
tick = np.sign(dp).replace(0, np.nan)
tick = tick.groupby([t["permno"], t["date"]]).ffill()
lr = np.where(t["price"] > t["mid"], 1, np.where(t["price"] < t["mid"], -1, tick))
ok = ~np.isnan(lr)
print(f"Lee-Ready: classified {ok.mean():.1%} of trades, accuracy {np.mean(lr[ok] == t['side'][ok]):.1%} "
      f"(midpoint trades only: {np.mean(lr[ok & (t['price'] == t['mid'])] == t['side'][ok & (t['price'] == t['mid'])]):.1%})")

last = t.groupby(["permno", "date"]).agg(close=("price", "last"), shares=("size", "sum")).reset_index()
c = last.merge(daily, on=["permno", "date"])
print(f"daily close = last trade: {np.allclose(c['close'], c['prc'])}; "
      f"volume = sum of sizes: {(c['shares'] == c['vol']).all()}")
print(f"no-trade days have negative prc: {(daily.loc[daily['vol'] == 0, 'prc'] < 0).all()}")

t["ts5"] = t["ts"] + pd.Timedelta(minutes=5)
t = pd.merge_asof(t.sort_values("ts5"), q[["ts", "permno", "date", "mid"]]
                  .rename(columns={"ts": "ts5", "mid": "mid5"}).sort_values("ts5"),
                  on="ts5", by=["permno", "date"], direction="backward")
t = t.sort_values(["permno", "ts"])
t["lr"] = np.where(t["price"] > t["mid"], 1, np.where(t["price"] < t["mid"], -1, np.nan))
tk = np.sign(t.groupby(["permno", "date"])["price"].diff()).replace(0, np.nan)
t["lr"] = t["lr"].fillna(tk.groupby([t["permno"], t["date"]]).ffill()).fillna(1)
t["real_lr"] = 2 * t["lr"] * (np.log(t["price"]) - np.log(t["mid5"]))
rs = t.groupby(["permno", "yyyymm"]).apply(lambda g: np.average(g["real_lr"], weights=g["dv"]),
                                           include_groups=False).rename("real_lr").reset_index()
r = rs.merge(sm, on=["permno", "yyyymm"])
print(f"realized spread with Lee-Ready: mean {r['real_lr'].mean():.4f} vs true {r['true_realized_spread'].mean():.4f}, "
      f"corr {r['real_lr'].corr(r['true_realized_spread']):.3f}")
