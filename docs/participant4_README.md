# Participant 4: price impact proxies

Part of the team replication of Goyenko, Holden & Trzcinka (2009), *Do liquidity measures measure liquidity?*, JFE 92, 153–181.
Covers section 5 (low-frequency price impact proxies), section 3.2 (price impact benchmarks) and Tables 4–5.

## What is here

| File | What it does | Paper |
|---|---|---|
| `src/price_impact_proxies.py` | `amihud`, `amivest`, `pastor_stambaugh_gamma`, `extended_impact`, `compute_impact_panel`, `add_extended_proxies` | sec. 5.1–5.4, eq. (27)–(34) |
| `src/impact_sim.py` | `simulate_impact()`: participant 2's simulator plus a known price impact; `impact_benchmarks()`: true and observed Lambda and 5-minute impact | sec. 3.2, eq. (4)–(6) |
| `src/impact_race.py` | Table 4 style leaderboards: Panel A (cross-section, Newey–West), Panel B (time series, Fisher z) | sec. 7.1–7.2 |
| `scripts/run_price_impact_check.py` | full pipeline on synthetic data, writes `results/` | — |
| `slides/build_slides.py` | fills slides 6 and 10 of the team deck | — |
| `tests/test_price_impact.py` | 14 tests | — |

## Run

```bash
pip install -r requirements.txt
python -m pytest tests -q
python scripts/run_price_impact_check.py --p2 ../participant2 --p3 ../participant3 --stocks 120 --months 48 --impact-scale 0.3 --tag baseline
python scripts/run_price_impact_check.py --p2 ../participant2 --p3 ../participant3 --stocks 120 --months 48 --skip-p3 --tag quick
python slides/build_slides.py --deck path/to/deck.pptx --tag baseline
```

`--p3` is the folder with `participant3_proxies.py`. The first command takes about 27 minutes because of the Gibbs sampler (2 cores);
the spread panel is cached in `results/spread_panel_*.pkl`, so a rerun takes seconds. `--skip-p3` drops LOT and Gibbs and runs in about 10 s.

## Definitions (say them on the slide if asked)

1. **Amihud**: mean of |r_t| / dollar volume_t over positive-volume days. **Amivest**: mean of dollar volume_t / |r_t| over days with non-zero return (so a zero-volume day with a midpoint return counts as 0).
2. **Gamma**: for every stock-month, OLS of r^e_{t+1} on a constant, r_t and sign(r^e_t)·dollar volume_t, where r^e = r − market return; gamma is the third coefficient, default 0 under 6 observations. Raw sign kept: gamma < 0 means reversal.
3. **Extended Amihud (eq. 31)**: spread proxy / average daily dollar volume, the average runs over all days of the window (no-trade days count as 0, the same convention as in participant 3's code). Eight versions: Roll, Effective Tick, Effective Tick2, Gibbs, LOT Mixed, LOT Y-split, Zeros, Zeros2. Holden Impact is missing because Holden was not implemented.
4. **Sign convention**: correlations are raw, as in the paper. Amivest is a liquidity measure, so its correlation with impact is negative and it ranks last even when its absolute value is large (−0.84 in Panel B of the baseline).
5. **Ranking tests** follow section 7.1: Panel A = mean over months of the cross-sectional correlation, difference of two proxies tested with a Newey–West t (4 lags); Panel B = correlation of equal-weighted portfolios over time, difference tested with Fisher z (n = number of months, treats the two correlations as independent, as in `race_metrics.fisher_z_test`).

## The synthetic benchmark

The shared simulator has no price impact, so `impact_sim.py` copies participant 2's loop and adds one thing: a trade of signed size `q·sqrt($ volume)` moves the efficient value on the next day by `lambda_t · q · sqrt($ volume)`.

* `lambda_i = scale · sigma_i / sqrt(avg $ volume_i) · exp(0.3 e)`, a Kyle-type slope. `scale = 0` reproduces participant 2's panel exactly (tested).
* `lambda_{i,m} = lambda_i · (target spread_{i,m} / sbar_i)^link`. With `link = 1` impact moves together with the spread, so there is common time variation; with `link = 0` Lambda is constant in time and Panel B is undefined.
* **True benchmarks** (what the slide uses): `lambda_true` = the simulated slope; `post_impact_true` = dollar-volume-weighted mean of 2·|move| over trades, which is eq. (6) with the efficient value in place of the midpoint.
* **Observed benchmarks** (kept in the CSV): `lambda_obs` is the regression (5) without constant of next-day midpoint return on signed sqrt dollar volume; `post_impact_obs` is eq. (6) with next-day midpoint. With one trade per day a month has 15–20 observations, so they are noisy: correlation with the truth is 0.50 for Lambda in the baseline (0.91 at `scale = 1`).

## Main numbers (monthly, 1/8 grid, 120 stocks × 48 months, `scale = 0.3`, `link = 1`)

Average cross-sectional correlation with the true benchmark (Panel A):

| | Roll Imp | Eff Tick Imp | Eff Tick2 Imp | Gibbs Imp | LOT Mix Imp | LOT Y Imp | Zeros Imp | Zeros2 Imp | Amihud | Gamma | Amivest |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Lambda | 0.678 | 0.766 | **0.775** | 0.736 | 0.757 | 0.712 | 0.712 | 0.704 | 0.765 | −0.060 | −0.404 |
| 5-min impact | 0.230 | 0.272 | **0.278** | 0.249 | 0.263 | 0.254 | 0.224 | 0.223 | 0.268 | −0.004 | −0.247 |

* In Panel A the top group is Effective Tick2 Impact with Amihud (5-min impact) or with Effective Tick Impact, LOT Mixed Impact and Amihud (Lambda). Gamma and Amivest are last, as in the paper.
* In Panel B (time series) spread-based proxies win and Amihud falls out of the top group (0.655 against 0.937). This is partly built in: Lambda is tied to the spread factor (`link = 1`). It is not evidence against Amihud.
* Sensitivity (`results/sensitivity_summary.csv`, without LOT and Gibbs): over `scale` 0.15 / 0.3 / 1.0 and `link` 0 / 1, Amihud is in the top group of Panel A in every configuration; it is the single best proxy when `link = 0` or `scale = 1`.
* The paper: Amihud is best cross-sectionally (0.317 Lambda, 0.516 5-min impact); Roll Impact is best over time (0.562, 0.517). Synthetic correlations are higher than real ones because the simulator obeys the models' assumptions.

## Limits

* One closing trade per day, so there is no intraday data and no Lee–Ready: signs come from the simulator.
* Monthly window only. The annual Table 5 needs about 10 years of data and Gibbs makes that slow.
* Holden is not implemented (team decision), so there are 8 extended proxies, not 9.
* The `results/spread_panel_*.pkl` cache must be deleted (`--no-cache`) if the simulator parameters change.
