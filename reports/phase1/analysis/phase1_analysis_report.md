# Phase 1 Analysis Report

## Descriptive Trends

- Weighted monthly skepticism slope: 0.000133 per observed month window (normal-approx p=0.0017).
- Weighted monthly scenario entropy slope: 0.001377 per observed month window (normal-approx p=0.0000).
- Trend charts are saved as SVG files in `reports/phase1/analysis/figures/`.

## SPF Group Comparison

| spf_group | product_count | product_month_rows | review_count | skepticism_ratio_weighted | scenario_entropy_weighted | semantic_gap_weighted |
| --- | --- | --- | --- | --- | --- | --- |
| high_spf_50_plus | 28 | 2477 | 14000 | 0.0609867 | 0.370569 | 0.741385 |
| low_spf_30_or_less | 60 | 5623 | 30000 | 0.038568 | 0.251164 | 0.731457 |
| mid_spf_31_49 | 12 | 1024 | 6000 | 0.0318676 | 0.250444 | 0.746288 |

## Fixed-Effects Panel Models

Model form: outcome_it ~ product fixed effects + month fixed effects + lagged semantic_gap_it + controls.

| outcome | n | product_fe | month_fe | beta_lag_semantic_gap | se_lag_semantic_gap | t_lag_semantic_gap | p_lag_semantic_gap_normal_approx | controls | weighted_by_review_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| skepticism_ratio | 9024 | 100 | 169 | 0.00605422 | 0.00853585 | 0.709269 | 0.478157 | promo_density_total, abstractness_ratio, avg_rating_month, log_reviews | True |
| scenario_entropy | 9024 | 100 | 169 | -0.0868185 | 0.036962 | -2.34886 | 0.0188312 | promo_density_total, abstractness_ratio, avg_rating_month, log_reviews | True |

## Keyword Sentiment Drift

Sentiment is proxied by star rating among reviews mentioning each keyword, aggregated by month.

| keyword | review_mentions | month_count | rating_slope_per_month | slope_se | t_stat | p_value_normal_approx | interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| white cast | 1382 | 105 | -0.00846411 | 0.00140702 | -6.01565 | 1.79163e-09 | negative_drift |
| reef safe | 212 | 69 | -0.00257912 | 0.00566211 | -0.455504 | 0.648746 | negative_drift |
| non-greasy | 274 | 108 | -0.00177873 | 0.00146872 | -1.21108 | 0.225866 | negative_drift |
| mineral | 1531 | 136 | -0.00049827 | 0.0014254 | -0.349564 | 0.726666 | negative_drift |
| clean | 703 | 127 | -9.15234e-05 | 0.0016841 | -0.0543457 | 0.95666 | negative_drift |
| dermatologist | 880 | 128 | 0.00116829 | 0.00146571 | 0.797084 | 0.425402 | non_negative_or_insufficient |
| natural | 1868 | 147 | 0.00148508 | 0.000815065 | 1.82203 | 0.0684497 | non_negative_or_insufficient |
| sensitive | 3161 | 153 | 0.00298572 | 0.00120719 | 2.47327 | 0.0133883 | non_negative_or_insufficient |
| gentle | 235 | 100 | 0.00525601 | 0.00223929 | 2.34718 | 0.0189163 | non_negative_or_insufficient |
| chemical-free | 7 | 7 | 0.0326711 | 0.0172257 | 1.89665 | 0.0578745 | non_negative_or_insufficient |

## High vs Low Attenuation Product Contrast

| group | product_count | mean_promo_density_total | mean_promo_density_natural_clean | mean_abstractness_ratio | mean_semantic_gap_coarse | mean_skepticism_ratio | mean_scenario_entropy | mean_attenuation_index_exploratory |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| high_attenuation_top_quartile | 25 | 4.51638 | 0.89262 | 0.111823 | 0.774268 | 0.0404036 | 0.0756975 | 0.197379 |
| low_attenuation_bottom_quartile | 25 | 6.78308 | 3.31976 | 0.207517 | 0.716962 | 0.0560534 | 0.35442 | 0.146649 |

## Cautions

- This Phase 1 run uses static product metadata repeated across review months; it is a feasibility model, not direct evidence of historical copy changes.
- Star rating is a rough sentiment proxy for keyword drift.
- Product-page metadata and reviews come from a public research dataset and may not represent live Amazon pages.
- The exploratory attenuation index still requires human annotation validation.
