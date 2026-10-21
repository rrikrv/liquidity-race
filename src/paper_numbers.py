"""Numbers reported by Goyenko, Holden & Trzcinka (2009), JFE 92, 153-181, typed in from the paper.

Source: Table 2 (monthly, TAQ effective spread, 1993-2005, 156 months), Table 3 (annual), Table 8 (by year),
Table 9 (Dow Jones, 1962-2000, annual). Proxy keys are ours. Holden, Amihud, Pastor-Stambaugh and Amivest
are in the paper but not in our race (Holden is too heavy, the rest measure price impact).
Read from the scanned PDF - if a number looks odd on a slide, check it against the paper first.
"""
import pandas as pd

ORDER = ["roll", "eff_tick", "eff_tick2", "holden", "gibbs", "lot_mixed", "lot_ysplit", "zeros", "zeros2", "amihud"]

MONTHLY = pd.DataFrame({
    "cs_corr":   [0.560, 0.626, 0.614, 0.682, 0.667, 0.651, 0.644, 0.427, 0.308, 0.571],
    "ts_corr":   [0.925, 0.941, 0.939, 0.951, 0.905, 0.722, 0.931, 0.874, 0.860, 0.608],
    "mean_bias": [-0.002, -0.012, -0.013, -0.011, -0.010, 0.027, -0.005, None, None, None],
    "rmse":      [0.032, 0.031, 0.032, 0.029, 0.029, 0.061, 0.034, None, None, None],
}, index=ORDER)

ANNUAL = pd.DataFrame({
    "cs_corr": [0.623, 0.707, 0.650, 0.745, 0.779, 0.545, 0.535, 0.590, 0.481, 0.594],
    "ts_corr": [0.982, 0.945, 0.954, 0.966, 0.991, 0.821, 0.934, 0.919, 0.909, 0.797],
}, index=ORDER)

TICK_REGIMES_TS = pd.DataFrame({
    "1993-96 ($1/8)":  [0.801, 0.918, 0.930, 0.932, 0.936, 0.407, 0.909],
    "1997-2000 ($1/16)": [0.703, 0.886, 0.885, 0.882, 0.663, 0.306, 0.812],
    "2001-05 ($0.01)": [0.933, 0.887, 0.884, 0.904, 0.913, 0.896, 0.863],
}, index=ORDER[:7]).T

BY_YEAR_CS = pd.DataFrame({
    "1993": [0.711, 0.689, 0.638, 0.720, 0.838, 0.702, 0.700, 0.438, 0.182, 0.513],
    "2005": [0.350, 0.449, 0.437, 0.549, 0.324, 0.484, 0.456, 0.425, 0.404, 0.598],
}, index=ORDER).T

DOW_TS = pd.Series([-0.642, 0.844, 0.844, 0.847, -0.395, 0.427, 0.778, 0.741, 0.741, 0.596], index=ORDER)

ROLL_SIZE_P1, ROLL_SIZE_P10 = 0.924, 0.362
