import numpy as np
import pandas as pd


def attach_quotes(trades, quotes, lag="0s"):
    t = trades.sort_values("ts").reset_index(drop=True)
    q = quotes.loc[(quotes["bid"] > 0) & (quotes["ask"] >= quotes["bid"]), ["ts", "ticker", "bid", "ask"]].copy()
    q["ts"] = q["ts"] + pd.Timedelta(lag)
    q = q.sort_values("ts")
    out = pd.merge_asof(t, q, on="ts", by="ticker", direction="backward", allow_exact_matches=True)
    out["mid"] = (out["bid"] + out["ask"]) / 2
    return out


def tick_test(df):
    d = df.groupby("ticker")["price"].diff()
    d = d.where(d != 0).groupby(df["ticker"]).ffill()
    return np.sign(d).fillna(0)


def lee_ready(df):
    s = np.sign(df["price"] - df["mid"]).fillna(0)
    return s.where(s != 0, tick_test(df)).astype(int)


def future_price(df, horizon="5min"):
    left = df[["ticker"]].assign(ts_f=df["ts"] + pd.Timedelta(horizon), day=df["ts"].dt.floor("D"), i=np.arange(len(df)))
    right = df[["ticker", "ts", "price"]].rename(columns={"ts": "ts_f", "price": "price_f"})
    right["day_f"] = right["ts_f"].dt.floor("D")
    m = pd.merge_asof(left.sort_values("ts_f"), right.sort_values("ts_f"), on="ts_f", by="ticker", direction="forward")
    m.loc[m["day"] != m["day_f"], "price_f"] = np.nan
    return m.sort_values("i")["price_f"].to_numpy()


def future_mid(df, quotes, horizon="5min"):
    left = df[["ticker"]].assign(ts=df["ts"] + pd.Timedelta(horizon), i=np.arange(len(df)))
    q = quotes[["ts", "ticker", "bid", "ask"]].sort_values("ts")
    m = pd.merge_asof(left.sort_values("ts"), q, on="ts", by="ticker", direction="backward").sort_values("i")
    return ((m["bid"] + m["ask"]) / 2).to_numpy()


def trade_level(trades, quotes, lag="0s", horizon="5min", sign="lee_ready"):
    df = attach_quotes(trades, quotes, lag)
    df["q"] = lee_ready(df) if sign == "lee_ready" else df[sign].astype(int)
    df["dv"] = df["price"] * df["size"]
    df["eff"] = 2 * np.abs(np.log(df["price"]) - np.log(df["mid"]))
    df["price_5"] = future_price(df, horizon)
    df["real"] = 2 * df["q"] * (np.log(df["price"]) - np.log(df["price_5"]))
    df["mid_5"] = future_mid(df, quotes, horizon)
    df["real_mid"] = 2 * df["q"] * (np.log(df["price"]) - np.log(df["mid_5"]))
    df["impact"] = 2 * df["q"] * (np.log(df["mid_5"]) - np.log(df["mid"]))
    df.loc[df["q"] == 0, ["real", "real_mid", "impact"]] = np.nan
    return df


def _wavg(x, w):
    m = x.notna() & w.notna()
    return np.average(x[m], weights=w[m]) if w[m].sum() > 0 else np.nan


def monthly_benchmarks(trades, quotes, lag="0s", horizon="5min", sign="lee_ready", freq="M"):
    df = trade_level(trades, quotes, lag, horizon, sign)
    df["month"] = df["ts"].dt.tz_localize(None).dt.to_period(freq) if df["ts"].dt.tz is not None else df["ts"].dt.to_period(freq)
    g = df.groupby(["ticker", "month"])
    return pd.DataFrame({
        "effective_spread": g.apply(lambda x: _wavg(x["eff"], x["dv"])),
        "realized_spread": g.apply(lambda x: _wavg(x["real"], x["dv"])),
        "realized_spread_mid": g.apply(lambda x: _wavg(x["real_mid"], x["dv"])),
        "price_impact_5min": g.apply(lambda x: _wavg(x["impact"], x["dv"])),
        "n_trades": g.size(),
    }).reset_index()


def lee_ready_accuracy(trades, quotes, true_col="side", lag="0s"):
    df = attach_quotes(trades, quotes, lag)
    df["q"] = lee_ready(df)
    inside = (df["price"] > df["bid"]) & (df["price"] < df["ask"])
    at_mid = df["price"] == df["mid"]
    hit = df["q"] == df[true_col]
    return pd.Series({
        "all": hit.mean(),
        "inside_spread": hit[inside].mean(),
        "at_mid": hit[at_mid].mean(),
        "share_inside": inside.mean(),
    })


def to_engine(monthly, col="effective_spread", base=pd.Timestamp("2000-01-01")):
    per = pd.PeriodIndex(monthly["month"], freq="M")
    win = (per.year - base.year) * 12 + (per.month - 1)
    s = pd.Series(monthly[col].to_numpy(), index=pd.MultiIndex.from_arrays([monthly["ticker"].to_numpy(), np.asarray(win)], names=["stock", "win"]))
    return s.sort_index()
