"""
The four "horse race" metrics of Goyenko, Holden & Trzcinka (2009), section 7.1.
A small version for checking proxies on synthetic data; participant 5 owns
the full engine for all 24 proxies.

All functions take two Series indexed by (stock, win): a proxy and the benchmark.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def _align(proxy: pd.Series, bench: pd.Series) -> pd.DataFrame:
    d = pd.concat({"x": proxy, "y": bench}, axis=1).dropna()
    d.index = d.index.set_names(["stock", "win"])
    return d


def cs_corr_series(proxy, bench) -> pd.Series:
    """Cross-sectional correlation in every window (Table 2, Panel A, step 1)."""
    d = _align(proxy, bench)
    return d.groupby(level="win").apply(lambda g: g["x"].corr(g["y"]))


def avg_cs_corr(proxy, bench) -> float:
    """Average cross-sectional correlation (Fama-MacBeth style, Panel A)."""
    return float(cs_corr_series(proxy, bench).mean())


def ts_corr(proxy, bench) -> float:
    """Time-series correlation of the equally weighted portfolio (Panel B)."""
    d = _align(proxy, bench).groupby(level="win").mean()
    return float(d["x"].corr(d["y"]))


def mean_bias(proxy, bench) -> float:
    """Mean of (proxy - benchmark) over all stock-windows (Panel F)."""
    d = _align(proxy, bench)
    return float((d["x"] - d["y"]).mean())


def rmse(proxy, bench) -> float:
    """RMSE computed every window, then averaged over windows (Panel F)."""
    d = _align(proxy, bench)
    e2 = ((d["x"] - d["y"]) ** 2).groupby(level="win").mean()
    return float(np.sqrt(e2).mean())


def newey_west_t(x: pd.Series, lags: int = 4) -> float:
    """t-statistic of mean(x) with Newey-West standard errors.

    Used for the difference of two cross-sectional correlation series
    (4 lags for monthly data, 3 for annual in the paper)."""
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    n, e = len(x), x - x.mean()
    s = e @ e / n
    for k in range(1, lags + 1):
        s += 2 * (1 - k / (lags + 1)) * (e[k:] @ e[:-k]) / n
    return float(x.mean() / np.sqrt(s / n))


def fisher_z_test(r1: float, r2: float, n: int) -> float:
    """Two-sided p-value that two correlations (each from n obs.) differ.
    Simple version that treats them as independent."""
    z = (np.arctanh(r1) - np.arctanh(r2)) / np.sqrt(2 / (n - 3))
    return float(2 * stats.norm.sf(abs(z)))


def race_table(proxies: pd.DataFrame, bench: pd.Series, units_cols=None) -> pd.DataFrame:
    """One row per proxy with the four metrics. Bias and RMSE only for proxies
    measured in spread units (Zeros/Zeros2 are not, so they get NaN, as 'na'
    in the paper)."""
    units_cols = units_cols if units_cols is not None else ["roll", "eff_tick", "eff_tick2"]
    rows = {}
    for c in proxies.columns:
        rows[c] = {
            "cs_corr": avg_cs_corr(proxies[c], bench),
            "ts_corr": ts_corr(proxies[c], bench),
            "mean_bias": mean_bias(proxies[c], bench) if c in units_cols else np.nan,
            "rmse": rmse(proxies[c], bench) if c in units_cols else np.nan,
        }
    return pd.DataFrame(rows).T
