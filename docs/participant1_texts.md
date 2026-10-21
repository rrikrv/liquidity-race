# Slides 2, 3, 12, 13 (Erik)

## Slide 2. Why we need daily liquidity proxies

- Liquidity enters asset pricing (liquidity premium and liquidity risk), market efficiency (is a strategy profitable net of costs?) and corporate finance.
- Intraday data are short and expensive: US transaction data start in 1983, TAQ in 1993, many countries have none. Daily data go back to 1926 (CRSP) and cover 60+ countries (Datastream).
- Earlier tests: few proxies, annual or quarterly windows. The literature uses them monthly.
- The paper: 12 spread and 12 price-impact proxies from daily data vs. intraday benchmarks (TAQ, Rule 605); 400 random stocks, 1993–2005, monthly and annual.

**Takeaway:** if daily proxies track intraday costs, liquidity research can go back in time and around the world.

**Notes:** Liquidity matters in three literatures: in asset pricing it is priced as a characteristic and as a risk, in market-efficiency tests we must subtract trading costs before calling a strategy profitable, and in corporate finance events change liquidity. The problem is data. Intraday trades and quotes exist in the US only since the eighties and in many markets not at all, while daily prices and volumes exist almost everywhere. So researchers use daily proxies, but rarely check that they measure actual trading costs, and when they do, on annual data with a handful of measures. This paper runs the horse race: 24 contestants, intraday benchmarks, monthly and annual windows.

## Slide 3. Benchmarks: effective and realized spread, price impact

| Benchmark | Formula | Meaning |
|---|---|---|
| Effective spread (TAQ), eq. 1 | 2·\|ln P − ln M\|, $-volume weighted | full cost vs. the midpoint; no trade sign needed |
| Realized spread (TAQ), eq. 2 | 2·q·(ln P_k − ln P_k+5min) | temporary part, what the liquidity provider keeps; sign q by Lee–Ready |
| Effective spread (605), eq. 3 | same, from orders; midpoint at order receipt | no sign errors, crossed orders counted twice |
| Lambda, eq. 5 | r_n = λ·Σ sign·√$vol, 5-min intervals, no constant | price move per unit of order flow |
| 5-minute price impact, eq. 6 | 2·q·(ln M_k+5min − ln M_k) | permanent part of the spread |
| Static price impact (605), eq. 4 | (spread big − spread small) / (size big − size small) | slope of cost in order size |

**Takeaway:** effective ≈ realized + price impact. In the paper's sample: effective 2.9%, realized 1.5%.

**Notes:** Three spread benchmarks and three price-impact benchmarks. The effective spread is the cost of a trade relative to the midpoint, and it does not need the trade direction. The realized spread subtracts how the price moved in the next five minutes; it is what the liquidity provider earns, and it needs the direction, which TAQ does not report, so the authors infer it with Lee–Ready. Rule 605 data come from market centers: the midpoint is taken when the order arrives and the direction is known, but they start only in late 2001. Price impact is the permanent part: the regression slope Lambda, the five-minute midpoint move, and the static slope from Rule 605. Likely question: effective vs. realized. Effective is the total cost, realized is the temporary part, the difference is the information the trade revealed.

## Slide 12. Critique

- **The benchmark is noisy.** Lee–Ready misclassifies 24% of trades inside the spread; 40% of TORQ trades have no initiator. Ours: with 10% of trades at the midpoint, Lee–Ready is right on 95% of trades but only 49% at the midpoint, so the realized spread is overstated by 14% and the 5-minute price impact understated by 15%. The effective spread, which needs no sign, is exact.
- **The benchmark choice changes the answer.** Time-series correlation 0.95 with TAQ, 0.53 with Rule 605; with 605, Amihud is best cross-sectionally.
- **Defaults are hidden.** Roll = 0 when the autocovariance is positive; the share of such zeros is never reported. On the Dow, Roll correlates −0.64 with the spread.
- **Tick regimes.** Clustering measures need a coarse grid. Paper: cross-sectional correlation falls in the decimal era (Table 8). Ours: Effective Tick falls from 0.98 to 0.55 when clustering weakens.
- **Sample.** 68% NASDAQ, equal weights: small stocks drive the results. For the largest decile all proxies are weak; ours: Roll 0.18, Gibbs 0.15 vs. Effective Tick 0.91.
- **Common trend.** Spreads fell throughout 1993–2005, which inflates time-series correlations; first differences would be a fairer test.
- **The test is too lenient.** Fisher's Z treats two correlations with the same benchmark as independent and rejects too rarely, so the winner groups are too wide. Our annual race: Fisher puts LOT Mixed among the winners, Meng–Rosenthal–Rubin does not.

**Takeaway:** the ranking depends on the benchmark, the tick regime and the stock universe, and the test inflates the winner groups.

**Notes:** Seven issues. First, the yardstick itself is noisy: the realized spread and price impact need trade direction, and Lee–Ready gets a quarter of inside-spread trades wrong. In our intraday simulation the tick test is a coin flip at the midpoint, and that alone moves about 15% of the spread from price impact into the realized spread, while the effective spread is reproduced exactly. Second, change the benchmark to Rule 605 and the time-series correlation drops from 0.95 to 0.53, and Amihud, which loses on TAQ, wins cross-sectionally. Third, every measure must always produce a number, so Roll is set to zero when the formula is undefined; the authors say this does not matter but do not show how often it happens. Fourth, Effective Tick reads price clustering, which electronic trading and the one-cent tick remove; we see the same collapse in our simulation. Fifth, the sample is two-thirds NASDAQ and equally weighted, and all proxies fail on large stocks. Sixth, time-series correlations of 0.95 partly reflect the common decline in spreads. Seventh, the Fisher test ignores that the two proxies are correlated with the same benchmark and with each other; with the correct test our annual winner group shrinks.

## Slide 13. How this could have overfit

- Proxies are not fitted to the benchmark, so the risk is **selection**, not parameter fitting.
- **Multiple comparisons.** 24 contestants × 6 benchmarks × 4 metrics × 2 frequencies × subsamples: hundreds of races, no correction (Holm, model confidence set).
- **Researcher degrees of freedom.** Four new spread measures and nine new impact measures are the authors' own and are tested on the same data; LOT Y-split is a new way to split the regions; "winning" is defined by the authors.
- **Nesting.** Holden contains Roll and Effective Tick as special cases: more flexibility, built-in advantage.
- **Thin out-of-sample evidence.** One test: Dow 1962–2000, 39 annual points, quoted spread instead of effective.
- **Our own version of the problem.** In our simulation Effective Tick wins everything (0.97) because the simulator clusters prices exactly as it assumes; in the paper it is fifth. A test that matches the model's assumptions picks that model.
- **How to check:** choose winners on 1993–1999, test on 2000–2005; block bootstrap of correlation differences; independent data (MOEX, crypto).

**Takeaway:** nothing is fitted, but measures, metrics and the definition of winning were chosen on the same data.

**Notes:** Overfitting here does not mean that parameters were tuned to the benchmark; no proxy sees the benchmark. The risk is in the choices around it. There are hundreds of races and no correction, so some wins are luck. Most of the winners were designed by the authors, and they also define what winning means. Holden nests two other contestants, so it starts with an advantage. The only real out-of-sample test is the Dow sample, 39 numbers with a different benchmark, and there Roll and Gibbs turn negative. Our replication shows the mechanism directly: our simulator follows Effective Tick's assumptions, and Effective Tick wins everything; on real data it is only fifth. The fix is standard: pick winners on one period and test on another, bootstrap the differences, and run the race on data the authors never saw.
