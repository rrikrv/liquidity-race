# Do liquidity measures measure liquidity? A replication on synthetic data

Team replication of Goyenko, Holden & Trzcinka (2009), *Do liquidity measures measure liquidity?*, JFE 92, 153–181.
The paper compares 24 daily ("low-frequency") liquidity proxies with spread and price-impact benchmarks built from
intraday TAQ data. TAQ/CRSP are paid, so we run the same "horse race" on **synthetic stocks whose true effective
spread is known**: every proxy is judged against the truth, with the paper's four metrics and tests.

## Run everything

```bash
pip install -r requirements.txt
make test      # 44 tests, ~25 s
make proxies   # simulate + compute all proxies, ~30 min on 2 cores, cached in results/cache
make impact    # price-impact race (participant 4); uses the cached spread panel, seconds
make tables    # horse race -> results/*.csv, results/summary.md, figures/*.png   (~1 min once cached)
make real ARGS="binance --tickers SOLUSDT XRPUSDT --start 2024-01-01 --end 2024-03-31"   # real data (network), Erik
make deck      # fill the shared slide deck -> slides/deck_final.pptx
```

`python scripts/run_all.py` does the same as `make tables` (it builds the cache first if it is missing).
All seeds are fixed, so a re-run gives identical numbers.

## What is where

| Path | What | Who |
|---|---|---|
| `src/liquidity_sim.py` | simulator with a known spread (`simulate`) and the benchmark (`benchmark`) | Rus |
| `src/intraday_sim.py` | intraday trades and quotes consistent with the daily panel (for Erik's benchmarks); `scripts/export_for_team.py` writes `team_data/` | Rus |
| `src/spread_proxies.py` | Roll, Effective Tick, Effective Tick2, Zeros, Zeros2 | Rus |
| `src/participant3_proxies.py` | LOT Mixed, LOT Y-split, Gibbs (Holden is not implemented) | Artemiy |
| `src/race_engine.py` | **the horse-race engine**: 4 metrics, all tests, winners, subsamples | Riri |
| `src/portable.py` | saves the cache independent of the pandas version | Riri |
| `src/pipeline.py` | scenarios -> daily panel -> all proxies + benchmark (cached) | Riri |
| `src/paper_numbers.py` | the authors' numbers (Tables 2, 3, 8, 9) typed in for comparison | Riri |
| `src/price_impact_proxies.py` | Amihud, Amivest, Gamma, extended Amihud (spread proxy / dollar volume) | Tokha |
| `src/impact_sim.py` | simulator with a known price impact, true and observed Lambda / 5-minute impact | Tokha |
| `src/impact_race.py` | price-impact leaderboards (Table 4 style) | Tokha |
| `scripts/run_price_impact_check.py` | price-impact pipeline -> `results/price_impact/` | Tokha |
| `scripts/run_price_impact_race.py` | the same race through the common engine (cross-check, plus the dependent-correlation test) | Riri |
| `src/participant1_data.py` | real data: MOEX ISS, Yahoo, Binance; daily panel in the repo format | Erik |
| `src/intraday_benchmarks.py` | effective and realized spread from trades and quotes (eq. 1, 2), Lee–Ready, `to_engine` | Erik |
| `scripts/check_team_data.py` | benchmarks on Rus's intraday export (`team_data/`) vs. the true values -> `results/participant1_*.csv` | Erik |
| `scripts/run_real.py` | real data -> panel -> all proxies (+ benchmark and race for Binance) -> `results/real/` | Erik |
| `scripts/run_all.py` | tables and figures | Riri |
| `scripts/build_deck.py` | fills slides 7, 9, 11, 15 from the results, builds slides 2, 3, 12, 13 from `docs/participant1_texts.md` and 4, 8, and inserts participant 4's slides 6 and 10 | Riri |
| `scripts/run_synthetic_check.py` | Rus's validation experiments of the proxies | Rus |
| `tests/` | proxy tests (Rus) and engine tests (Riri) | |
| `docs/` | participants' own notes and Artemiy's first race run | |

**Data format (all code uses it):** every table is indexed by `(stock, win)`, where `win` is the month number
(or the year number for annual windows). A proxy table has one column per proxy, the benchmark is a Series on the
same index.

## The engine in one screen

```python
import race_engine as eng
race = eng.Race(proxies, bench, units=["roll", "eff_tick", ...], window="month")   # "year" -> 3 NW lags
race.table()          # cs_corr, ts_corr, mean_bias, rmse, theil_u2 + winner flags (paper's Table 2, panels A, B, F)
race.diff_p_cs()      # p-values: do two proxies' cross-sectional correlations differ? (Newey-West, 4 lags)
race.diff_p_ts("fisher")   # Fisher Z, as in the paper
race.diff_p_ts("mrr")      # Meng-Rosenthal-Rubin: correct for two proxies sharing one benchmark
eng.ts_corr_by_group(proxies, bench, eng.decile_labels(size))   # panels D/E: size and spread deciles
eng.ts_corr_by_period(proxies, bench, {"1993-96": (0, 47), ...})  # panel C: tick regimes
```

* **Panel A:** correlation across stocks in each window, averaged over windows. Two proxies differ if the mean of
  the monthly difference of their correlations is non-zero (t-test, Newey–West, 4 lags monthly / 3 annual).
* **Panel B:** time-series correlation of the equally weighted portfolio; against zero via
  t = r√((n−2)/(1−r²)); between proxies via Fisher's Z.
* **Panel F:** mean bias (Newey–West t over windows), RMSE per window then averaged (paired t-test),
  Theil's U². Only for proxies in spread units, so not Zeros.
* **Winner:** the best value plus every proxy that is not significantly different from it (5 %).

Checked: Newey–West agrees with `statsmodels` HAC to machine precision; a Monte-Carlo test confirms the
Meng–Rosenthal–Rubin test has 5 % size when the proxies share the benchmark, while the independent-sample Fisher test
rejects far too rarely (it is conservative).

## Things to know (honest list)

1. **Everything is synthetic.** The simulator obeys the proxies' own assumptions (Roll's bid-ask bounce, price
   clustering, LOT's no-trade region), so correlations are higher than in real data. What carries over is
   *where each proxy breaks*, not the level.
2. **Holden is not computed** (too heavy), so the race has 8 of the paper's 10 spread proxies; Amihud, Gamma and
   Amivest belong to the price-impact race (Tokha).
3. **Size** in the decile tests is average daily dollar volume (the simulator has no market capitalisation).
   **Exchanges (NYSE vs Nasdaq)** are not modelled, so Table 7 is not replicated.
4. **Tick regimes:** 1/8, 1/16 and decimal grids are separate simulations; for the decimal era the share of
   clustered quotes is lowered to κ = 0.4 (our assumption for electronic trading).
5. **Dow:** the "Dow-like" sample is 30 large, low-spread stocks for 39 years with annual windows; the benchmark is
   the true effective spread (the paper uses the quoted spread of the real Dow portfolio).
6. **LOT and Gibbs were sped up** (about 5×) by replacing `scipy.stats` calls with `scipy.special` and a direct
   truncated-normal sampler; likelihood values are identical, Gibbs draws come from the same distribution.
   Gibbs uses 300 sweeps (100 burn-in) in the race.
7. The authors' numbers in `src/paper_numbers.py` were read from the scanned paper; check one against the PDF
   before putting it on a slide.

8. **Price impact** uses participant 4's own simulator (it adds a known price impact to Rus's), 120 stocks × 48 months,
   monthly windows only. The common engine reproduces his Table 4 correlations to 1e-6 and his leader groups
   exactly (Fisher test). With the dependent-correlation test the time-series leader groups shrink.
   See `docs/participant4_README.md` for his definitions and limits.

`team_data/` (CRSP-style daily panel, trades, quotes for the benchmark code) is not in the repository (22 MB); `python scripts/export_for_team.py` regenerates it. The simulator update that adds the intraday layer leaves all daily results unchanged (checked: identical panels and benchmarks).

9. **Realized spread in `team_data`** (`true_realized_spread`) uses the midpoint 5 minutes later (Huang–Stoll variant), not the paper's eq. (2), which uses the trade price 5 minutes later; the two correlate 0.92. In the simulator the trade side at the midpoint is independent of the previous price, so the tick test is a coin flip there (49 %); on real data it does clearly better, so our Lee–Ready errors are a worst case.

Results: see `results/summary.md` (spread race), `results/price_impact/` (price-impact race) and `figures/`.
