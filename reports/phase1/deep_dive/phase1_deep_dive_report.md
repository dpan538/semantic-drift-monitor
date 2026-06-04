# Phase 1 Deep-Dive Report

## Rebuilt Attenuation Measures

- `trust_response_index` = 0.55 * skepticism + 0.30 * value complaint + 0.15 * rating decline.
- `trust_decline_index_theory` = 0.40 * skepticism + 0.25 * value complaint + 0.20 * semantic gap + 0.15 * rating decline.
- `lockin_index` = 1 - scenario entropy.

The response-only trust index is the preferred dependent variable for lagged semantic-gap models because it does not mechanically include semantic gap.

## Lagged Semantic Gap Models

| outcome | beta | se | t | p_normal_approx | n | status |
| --- | --- | --- | --- | --- | --- | --- |
| trust_response_index | 0.00347205 | 0.00473063 | 0.733951 | 0.462979 | 9024 | ok |
| trust_decline_index_theory | 0.00790616 | 0.0038029 | 2.07898 | 0.037619 | 9024 | ok |
| lockin_index | 0.0868185 | 0.036962 | 2.34886 | 0.0188312 | 9024 | ok |
| scenario_entropy | -0.0868185 | 0.036962 | -2.34886 | 0.0188312 | 9024 | ok |

## Time-Period Summary

| time_period | product_month_rows | review_count | skepticism_ratio_weighted | trust_response_index_weighted | lockin_index_weighted | scenario_entropy_weighted | semantic_gap_weighted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2005_2010 | 52 | 60 | 0.0330269 | 0.0625398 | 0.90786 | 0.0921403 | 0.804747 |
| 2011_2016 | 2586 | 9612 | 0.0420847 | 0.0476913 | 0.753038 | 0.246962 | 0.743376 |
| 2017_2023 | 6486 | 40328 | 0.0445239 | 0.0571211 | 0.706253 | 0.293747 | 0.73416 |

## SPF Group Deep Comparison

| group | product_count | mean_price | mean_promo_density_total | mean_promo_density_natural_clean | mean_promo_density_sensorial | mean_promo_density_efficacy | mean_abstractness_ratio | mean_semantic_gap_coarse | mean_trust_response_index | mean_lockin_index | mean_scenario_entropy | mean_skepticism_ratio | mean_white_cast_review_share | mean_greasy_texture_review_share | mean_burn_failure_review_share | mean_price_value_review_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| high_spf_50_plus | 28 | 21.1342 | 6.42615 | 2.36749 | 0.754572 | 3.18215 | 0.169067 | 0.77666 | 0.0647174 | 0.75458 | 0.24542 | 0.0608073 | 0.0805 | 0.2005 | 0.0713571 | 0.0330714 |
| low_spf_30_or_less | 60 | 14.2088 | 5.89118 | 2.13987 | 0.813006 | 2.80119 | 0.159356 | 0.767034 | 0.0525301 | 0.837136 | 0.162864 | 0.0389381 | 0.0241333 | 0.1681 | 0.0311333 | 0.0269667 |
| mid_spf_31_49 | 12 | 24.1518 | 3.5746 | 1.43522 | 1.26564 | 0.746519 | 0.164815 | 0.775469 | 0.0454575 | 0.821162 | 0.178838 | 0.0301058 | 0.0245 | 0.15 | 0.0108333 | 0.0391667 |

## Brand-Type Comparison

| group | product_count | mean_price | mean_promo_density_total | mean_promo_density_natural_clean | mean_promo_density_sensorial | mean_promo_density_efficacy | mean_abstractness_ratio | mean_semantic_gap_coarse | mean_trust_response_index | mean_lockin_index | mean_scenario_entropy | mean_skepticism_ratio | mean_white_cast_review_share | mean_greasy_texture_review_share | mean_burn_failure_review_share | mean_price_value_review_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| drugstore_derm | 30 | 16.0161 | 6.79238 | 2.03376 | 1.10903 | 3.48959 | 0.107977 | 0.757878 | 0.0657836 | 0.791149 | 0.208851 | 0.0591794 | 0.045 | 0.212733 | 0.0342667 | 0.0277333 |
| mass_sun_care | 18 | 11.8931 | 5.84583 | 1.12046 | 0.712399 | 3.97357 | 0.0517066 | 0.746429 | 0.05564 | 0.809791 | 0.190209 | 0.0489133 | 0.0348889 | 0.162889 | 0.0717778 | 0.0198889 |
| other_or_niche | 50 | 20.625 | 5.17138 | 2.54204 | 0.741329 | 1.73484 | 0.234423 | 0.787862 | 0.0473332 | 0.833596 | 0.166404 | 0.0310859 | 0.0332 | 0.14992 | 0.03228 | 0.03332 |
| premium_import_beauty | 2 | 15 | 4.36636 | 1.81068 | 0.967742 | 1.58794 | 0.190909 | 0.754479 | 0.0838456 | 0.60992 | 0.39008 | 0.0950256 | 0.179 | 0.345 | 0.031 | 0.079 |

## Natural-Promo Frequency Comparison

| group | product_count | mean_price | mean_promo_density_total | mean_promo_density_natural_clean | mean_promo_density_sensorial | mean_promo_density_efficacy | mean_abstractness_ratio | mean_semantic_gap_coarse | mean_trust_response_index | mean_lockin_index | mean_scenario_entropy | mean_skepticism_ratio | mean_white_cast_review_share | mean_greasy_texture_review_share | mean_burn_failure_review_share | mean_price_value_review_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| high_natural_promo | 50 | 20.2863 | 7.49691 | 3.82859 | 0.815269 | 2.71333 | 0.22798 | 0.767222 | 0.0590795 | 0.768786 | 0.231214 | 0.046712 | 0.0604 | 0.18224 | 0.03928 | 0.03232 |
| low_natural_promo | 50 | 14.9642 | 4.02905 | 0.409497 | 0.886651 | 2.60927 | 0.0974801 | 0.77426 | 0.0511081 | 0.855421 | 0.144579 | 0.0412913 | 0.01952 | 0.16776 | 0.04064 | 0.02796 |

## Segmented Lagged Semantic-Gap Models

| segment_type | segment | outcome | beta | se | t | p_normal_approx | n | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| spf_group | high_spf_50_plus | trust_response_index | 0.000375642 | 0.0117533 | 0.0319604 | 0.974504 | 2449 | ok |
| spf_group | high_spf_50_plus | lockin_index | 0.013918 | 0.0815128 | 0.170746 | 0.864423 | 2449 | ok |
| spf_group | low_spf_30_or_less | trust_response_index | 0.00670139 | 0.00554925 | 1.20762 | 0.227193 | 5563 | ok |
| spf_group | low_spf_30_or_less | lockin_index | 0.146846 | 0.044856 | 3.27372 | 0.00106142 | 5563 | ok |
| spf_group | mid_spf_31_49 | trust_response_index | -0.000669657 | 0.0123219 | -0.054347 | 0.956659 | 1012 | ok |
| spf_group | mid_spf_31_49 | lockin_index | -0.0784369 | 0.119034 | -0.658944 | 0.509932 | 1012 | ok |
| time_period | 2005_2010 | trust_response_index |  |  |  |  | 34 | insufficient_variation |
| time_period | 2005_2010 | lockin_index |  |  |  |  | 34 | insufficient_variation |
| time_period | 2011_2016 | trust_response_index | 0.0232661 | 0.00979319 | 2.37574 | 0.0175137 | 2528 | ok |
| time_period | 2011_2016 | lockin_index | 0.0354753 | 0.0625063 | 0.567548 | 0.570342 | 2528 | ok |
| time_period | 2017_2023 | trust_response_index | -0.00195486 | 0.00546988 | -0.357387 | 0.720802 | 6462 | ok |
| time_period | 2017_2023 | lockin_index | 0.0993242 | 0.0449258 | 2.21085 | 0.0270463 | 6462 | ok |
| brand_type | drugstore_derm | trust_response_index | 0.0061702 | 0.00987846 | 0.624611 | 0.532226 | 2688 | ok |
| brand_type | drugstore_derm | lockin_index | 0.0799662 | 0.0703378 | 1.13689 | 0.255585 | 2688 | ok |
| brand_type | mass_sun_care | trust_response_index | 0.00189507 | 0.0119252 | 0.158913 | 0.873737 | 1596 | ok |
| brand_type | mass_sun_care | lockin_index | 0.138648 | 0.0810715 | 1.7102 | 0.087229 | 1596 | ok |
| brand_type | other_or_niche | trust_response_index | -0.00116102 | 0.00600426 | -0.193365 | 0.846673 | 4633 | ok |
| brand_type | other_or_niche | lockin_index | 0.0629679 | 0.0538232 | 1.1699 | 0.24204 | 4633 | ok |
| brand_type | premium_import_beauty | trust_response_index | 0.0429028 | 0.1862 | 0.230412 | 0.817771 | 107 | ok |
| brand_type | premium_import_beauty | lockin_index | 0.68313 | 0.509669 | 1.34034 | 0.180135 | 107 | ok |
| natural_frequency_group | high_natural_promo | trust_response_index | 0.00111615 | 0.00723086 | 0.15436 | 0.877326 | 4329 | ok |
| natural_frequency_group | high_natural_promo | lockin_index | 0.117615 | 0.0597148 | 1.96961 | 0.0488827 | 4329 | ok |
| natural_frequency_group | low_natural_promo | trust_response_index | 0.00438106 | 0.00639521 | 0.685054 | 0.49331 | 4695 | ok |
| natural_frequency_group | low_natural_promo | lockin_index | 0.064123 | 0.0468564 | 1.3685 | 0.171156 | 4695 | ok |

## Quasi-Historical Promo Relay Counts

These counts capture reviews that both mention a target keyword and use language such as `it says`, `claimed`, `advertised`, or `bought because`.

| keyword | relay_review_count | product_count | first_year | last_year | mean_rating |
| --- | --- | --- | --- | --- | --- |
| sensitive | 120 | 56 | 2012 | 2023 | 3.79167 |
| natural | 77 | 49 | 2011 | 2023 | 3.83117 |
| white cast | 66 | 30 | 2012 | 2023 | 3.40909 |
| mineral | 56 | 31 | 2011 | 2022 | 3.30357 |
| clean | 41 | 31 | 2012 | 2023 | 3.29268 |
| dermatologist | 37 | 24 | 2012 | 2022 | 3.81081 |
| reef safe | 17 | 11 | 2017 | 2023 | 2.70588 |
| non-greasy | 15 | 13 | 2012 | 2022 | 4.06667 |
| broad spectrum | 12 | 11 | 2013 | 2022 | 3.66667 |
| gentle | 6 | 6 | 2014 | 2019 | 4 |
| chemical-free | 0 | 0 |  |  |  |

## Reading Notes

- The split-index design confirms whether semantic gap relates more to trust erosion or use-case lock-in.
- Promo-relay counts are exploratory proxies, not historical page snapshots.
- Group comparisons are descriptive and should guide follow-up hand annotation rather than stand alone as causal evidence.
