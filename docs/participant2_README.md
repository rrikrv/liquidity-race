# Participant 2: Roll, Effective Tick, Zeros + synthetic data

Part of the team replication of Goyenko, Holden & Trzcinka (2009),
*Do liquidity measures measure liquidity?*, JFE 92, 153–181.

## What is here

| File | What it does | Paper |
|---|---|---|
| `src/spread_proxies.py` | `roll`, `effective_tick`, `effective_tick2`, `zeros`, `zeros2`, `compute_panel` | sec. 4.1, 4.2, 4.6; eq. (7)–(16), (25)–(26) |
| `src/liquidity_sim.py` | `simulate()` — synthetic daily panel with a **known** spread; `benchmark()` — true effective spread per stock-month | eq. (1), (7), (8) |
| `src/race_metrics.py` | 4 race metrics: avg. cross-sectional corr., time-series corr. of EW portfolio, mean bias, RMSE; Newey–West t and Fisher z | sec. 7.1 |
| `scripts/run_synthetic_check.py` | all experiments and figures | — |
| `src/intraday_sim.py` | `simulate_intraday()` — intraday trades and quotes consistent with the daily panel; `truth_from_trades()` — oracle effective/realized spread and price impact | eq. (1), (2), (6) |
| `scripts/export_for_team.py` | writes `team_data/` in participant 1's format (CRSP column names) | — |
| `scripts/check_export.py` | re-computes the benchmarks from the exported CSVs as participant 1 would | — |
| `tests/` | 15 checks: proxies (8) and intraday/daily consistency (7) | — |

## Run

```bash
pip install -r requirements.txt
python -m pytest tests -q                 # ~1 s, 8 tests
python scripts/run_synthetic_check.py     # ~1.5 min, writes figures/ and results/
python scripts/seed_check.py              # ~1 min, results/seed_robustness.csv
python scripts/export_for_team.py         # ~1 min, team_data/ for participant 1
python scripts/check_export.py            # ~30 s, checks team_data/
```

## For the rest of the team

```python
import sys; sys.path.insert(0, "participant2/src")
from liquidity_sim import SimConfig, simulate, benchmark
daily, stocks = simulate(SimConfig(n_stocks=400, n_months=60, grid="eighths", seed=1))
true_spread = benchmark(daily)            # Series indexed by (stock, win)
```

`daily` columns: `stock, t, month, day, price, volume, dollar_volume, ret, mkt_ret,
bid, ask, mid, value, quoted_spread, eff_spread, traded`.

* **Participant 3 (LOT, Gibbs):** `ret` + `mkt_ret` are all LOT needs; the true betas are in `stocks["beta"]`.
* **Participant 4 (Amihud etc.):** `dollar_volume`, `ret`. Extended Amihud = our spread proxy / average dollar volume.
* **Participant 5 (race engine):** `race_metrics.race_table(proxies_df, benchmark)` gives Table 2–style rows; extend it.

Grids: `"eighths"` (1993–96), `"sixteenths"` (1997–2000), `"decimal"` (2001+).
`cluster_strength` (κ) = share of quotes on round prices; κ < 1 mimics the decimal era.

## Implementation choices (say them on the slide if asked)

1. **Roll on returns**, not dollar price changes, so it is a proportional spread like the benchmark.
   Default 0 when the autocovariance is ≥ 0 (eq. 12).
2. **Effective Tick** on the 1/8 grid uses eq. (14)–(15) literally. For the decimal grid
   ($0.01, 0.05, 0.10, 0.25, 1) the clusters are not nested, so eq. (14) does not apply;
   we solve `F = A·γ`, where `A[j,k]` = Pr(cluster j | spread k). On binary grids this gives
   exactly eq. (14) (checked in the tests).
3. **Effective Tick2** uses midpoints on zero-volume days; a midpoint that falls off the grid
   (e.g. a 1/16 on the 1/8 grid) is counted in the finest cluster.
4. **Benchmark** = dollar-volume-weighted mean of 2|ln P − ln M| over closing trades.
   TAQ uses every trade in the day; we simulate only the close.

## Main numbers (monthly, synthetic 1/8 grid, κ = 1, 400 stocks × 60 months)

| | CS corr | TS corr | Bias | RMSE | Paper CS | Paper TS |
|---|---|---|---|---|---|---|
| Roll | 0.73 | 0.85 | +0.003 | 0.014 | 0.56 | 0.93 |
| Effective Tick | 0.96 | 0.99 | +0.001 | 0.005 | 0.63 | 0.94 |
| Effective Tick2 | 0.93 | 0.99 | −0.000 | 0.006 | 0.61 | 0.94 |
| Zeros | 0.41 | 0.96 | — | — | 0.43 | 0.87 |
| Zeros2 | 0.34 | 0.96 | — | — | 0.31 | 0.86 |

Synthetic correlations are higher than real ones by construction: the simulator obeys the
models' assumptions. The point is not the level but **where each proxy breaks** — see `figures/`.

## Reproducibility check (done 21 Oct 2026)

* Fresh virtual environment from `requirements.txt` (numpy 2.5, pandas 3.0, scipy 1.18, matplotlib 3.11):
  8/8 tests pass, the full script runs in ~1.5 min, and every CSV in `results/` is byte-identical
  to the committed one (all seeds are fixed).
* Over 5 seeds the cross-sectional ranking never changes: Effective Tick 0.964 ± 0.012,
  Effective Tick2 0.941 ± 0.015, Roll 0.748 ± 0.035, Zeros 0.422 ± 0.019, Zeros2 0.363 ± 0.024.

## Data for participant 1 (`team_data/`, see its DATA_README.md)

Default export: 400 stocks × 60 months (1993-01 … 1997-12, weekdays), 1/8 grid; intraday trades and
quotes for the first 100 stocks × 12 months (≈ 0.7 M trades, ≈ 1 M quote changes).
Intraday model: Brownian bridge between daily values, quotes revised when the value leaves the
half-spread band, 30 % informed trades, permanent impact of half the half-spread per trade,
10 % midpoint trades. Checks from the CSV files alone (`check_export.py`):

* effective spread from trades + quotes equals `true_eff_spread` (max difference 5·10⁻¹²);
* last trade = daily close, sum of sizes = daily volume, no-trade days have negative `prc`;
* Lee–Ready classifies 95 % of trades correctly (49 % of midpoint trades — the tick test is a coin flip there);
* realized spread ≈ half of effective spread (0.0055 vs 0.0122), as in the paper's Table 1 (0.015 vs 0.029).

The slide results do not use the intraday layer and are unchanged (CSV files byte-identical).
