# Results of the synthetic horse race

## table2_monthly  (12000 stock-windows)

|                 | cs_corr   | ts_corr   | mean_bias   | rmse    |
|:----------------|:----------|:----------|:------------|:--------|
| Roll            | 0.766     | 0.710     | 0.003       | 0.015   |
| Effective Tick  | 0.967 *   | 0.985 *   | 0.001       | 0.006 * |
| Effective Tick2 | 0.945     | 0.987 *   | -0.000 *    | 0.007 * |
| Zeros           | 0.363     | 0.934     | na          | na      |
| Zeros2          | 0.271     | 0.933     | na          | na      |
| LOT Mixed       | 0.860     | 0.906     | 0.020       | 0.027   |
| LOT Y-split     | 0.769     | 0.970     | 0.001       | 0.014   |
| Gibbs           | 0.868     | 0.834     | 0.004       | 0.010   |

`*` = best or statistically indistinguishable from the best (5 %).

Winners: cross-sectional corr: Effective Tick; time-series corr (Fisher, paper): Effective Tick, Effective Tick2; time-series corr (Meng-Rosenthal-Rubin): Effective Tick, Effective Tick2

## table3_annual  (2600 stock-windows)

|                 | cs_corr   | ts_corr   | mean_bias   | rmse    |
|:----------------|:----------|:----------|:------------|:--------|
| Roll            | 0.974 *   | 0.995     | 0.003       | 0.007   |
| Effective Tick  | 0.993 *   | 1.000 *   | 0.000 *     | 0.004 * |
| Effective Tick2 | 0.988 *   | 0.999 *   | -0.002      | 0.006   |
| Zeros           | 0.492     | 0.966     | na          | na      |
| Zeros2          | 0.427     | 0.966     | na          | na      |
| LOT Mixed       | 0.983     | 0.998 *   | 0.024       | 0.030   |
| LOT Y-split     | 0.964     | 0.998     | 0.001 *     | 0.008   |
| Gibbs           | 0.982 *   | 0.996     | 0.003       | 0.006   |

`*` = best or statistically indistinguishable from the best (5 %).

Winners: cross-sectional corr: Roll, Effective Tick, Effective Tick2, Gibbs; time-series corr (Fisher, paper): Effective Tick, Effective Tick2, LOT Mixed; time-series corr (Meng-Rosenthal-Rubin): Effective Tick, Effective Tick2

## Time-series correlation by size decile (1 = smallest; size = average daily dollar volume)

|    |   Roll |   Effective Tick |   Effective Tick2 |   Zeros |   Zeros2 |   LOT Mixed |   LOT Y-split |   Gibbs |
|---:|-------:|-----------------:|------------------:|--------:|---------:|------------:|--------------:|--------:|
|  1 |  0.809 |            0.889 |             0.873 |   0.634 |    0.606 |       0.842 |         0.835 |   0.789 |
|  2 |  0.729 |            0.977 |             0.978 |   0.802 |    0.806 |       0.893 |         0.902 |   0.859 |
|  3 |  0.716 |            0.978 |             0.975 |   0.773 |    0.766 |       0.83  |         0.881 |   0.872 |
|  4 |  0.736 |            0.977 |             0.973 |   0.778 |    0.772 |       0.868 |         0.882 |   0.87  |
|  5 |  0.809 |            0.928 |             0.927 |   0.72  |    0.706 |       0.857 |         0.864 |   0.869 |
|  6 |  0.537 |            0.97  |             0.974 |   0.873 |    0.873 |       0.863 |         0.892 |   0.764 |
|  7 |  0.487 |            0.979 |             0.981 |   0.817 |    0.819 |       0.878 |         0.911 |   0.704 |
|  8 |  0.401 |            0.925 |             0.923 |   0.684 |    0.684 |       0.76  |         0.763 |   0.497 |
|  9 |  0.141 |            0.95  |             0.951 |   0.736 |    0.735 |       0.726 |         0.831 |   0.224 |
| 10 |  0.179 |            0.91  |             0.919 |   0.648 |    0.647 |       0.613 |         0.735 |   0.153 |

## Time-series correlation by effective-spread decile (1 = lowest spread)

|    |   Roll |   Effective Tick |   Effective Tick2 |   Zeros |   Zeros2 |   LOT Mixed |   LOT Y-split |   Gibbs |
|---:|-------:|-----------------:|------------------:|--------:|---------:|------------:|--------------:|--------:|
|  1 | -0.178 |            0.953 |             0.952 |   0.626 |    0.628 |       0.469 |         0.638 |  -0.245 |
|  2 |  0.129 |            0.969 |             0.966 |   0.613 |    0.611 |       0.648 |         0.74  |   0.208 |
|  3 |  0.211 |            0.96  |             0.962 |   0.753 |    0.753 |       0.711 |         0.824 |   0.324 |
|  4 |  0.32  |            0.968 |             0.967 |   0.873 |    0.875 |       0.83  |         0.913 |   0.376 |
|  5 |  0.475 |            0.962 |             0.961 |   0.768 |    0.766 |       0.881 |         0.869 |   0.623 |
|  6 |  0.649 |            0.96  |             0.958 |   0.731 |    0.728 |       0.825 |         0.888 |   0.707 |
|  7 |  0.727 |            0.984 |             0.981 |   0.758 |    0.758 |       0.873 |         0.897 |   0.835 |
|  8 |  0.665 |            0.972 |             0.971 |   0.709 |    0.705 |       0.837 |         0.868 |   0.803 |
|  9 |  0.791 |            0.972 |             0.961 |   0.68  |    0.663 |       0.869 |         0.853 |   0.904 |
| 10 |  0.856 |            0.905 |             0.89  |   0.609 |    0.594 |       0.863 |         0.876 |   0.868 |

## Tick regimes: average cross-sectional correlation

|                   |   Roll |   Effective Tick |   Effective Tick2 |   Zeros |   Zeros2 |   LOT Mixed |   LOT Y-split |   Gibbs |
|:------------------|-------:|-----------------:|------------------:|--------:|---------:|------------:|--------------:|--------:|
| 1993-96 ($1/8)    |  0.793 |            0.983 |             0.968 |   0.393 |    0.354 |       0.864 |         0.782 |   0.902 |
| 1997-2000 ($1/16) |  0.723 |            0.964 |             0.941 |   0.507 |    0.463 |       0.855 |         0.775 |   0.843 |
| 2001-05 ($0.01)   |  0.768 |            0.548 |             0.521 |   0.525 |    0.489 |       0.866 |         0.777 |   0.9   |

## Tick regimes: time-series correlation

|                   |   Roll |   Effective Tick |   Effective Tick2 |   Zeros |   Zeros2 |   LOT Mixed |   LOT Y-split |   Gibbs |
|:------------------|-------:|-----------------:|------------------:|--------:|---------:|------------:|--------------:|--------:|
| 1993-96 ($1/8)    |  0.912 |            0.995 |             0.993 |   0.886 |    0.893 |       0.878 |         0.95  |   0.965 |
| 1997-2000 ($1/16) |  0.85  |            0.986 |             0.983 |   0.836 |    0.827 |       0.936 |         0.947 |   0.946 |
| 2001-05 ($0.01)   |  0.89  |            0.812 |             0.809 |   0.882 |    0.876 |       0.943 |         0.954 |   0.976 |

## Dow-like sample (30 stocks, 39 years, annual): time-series correlation

|                 |   ours_ts_corr |   ours_t |   paper_ts_corr |
|:----------------|---------------:|---------:|----------------:|
| Roll            |          0.697 |    5.913 |          -0.642 |
| Effective Tick  |          0.999 |  140.024 |           0.844 |
| Effective Tick2 |          0.999 |  142.084 |           0.844 |
| Zeros           |          0.993 |   50.78  |           0.741 |
| Zeros2          |          0.993 |   50.809 |           0.741 |
| LOT Mixed       |          0.991 |   44.872 |           0.427 |
| LOT Y-split     |          0.995 |   62.493 |           0.778 |
| Gibbs           |          0.803 |    8.201 |          -0.395 |
