# JMA Variable Definition Table

This table translates the exploratory pipeline into manuscript-ready variables.

| Construct | Variable | Definition | Level | Formula / Operationalization | Source Columns | Notes / Limitations |
|---|---|---|---|---|---|---|
| Consumer skepticism | `skepticism_ratio` | Share of review sentences containing skepticism, doubt, overclaim, authenticity, or failure language. | Product-month | skeptical sentences / total review sentences | `review_text`, skepticism lexicon | Lexicon-based; requires human validation. |
| Value complaint | `value_complaint_ratio` | Share of review sentences mentioning price/value dissatisfaction. | Product-month | value complaint sentences / total review sentences | `review_text`, value lexicon | Captures explicit value terms only. |
| Trust response | `trust_response_index` | Response-only index of distrust/skepticism/value/rating decline. | Product-month | 0.55 * skepticism + 0.30 * value complaint + 0.15 * rating decline | `skepticism_ratio`, `value_complaint_ratio`, `avg_rating_month` | Preferred trust outcome because it does not include semantic gap. |
| Theory trust decline | `trust_decline_index_theory` | Theory-weighted trust decline measure including semantic gap as contradiction proxy. | Product-month | 0.40 * skepticism + 0.25 * value complaint + 0.20 * semantic gap + 0.15 * rating decline | `skepticism_ratio`, `value_complaint_ratio`, `semantic_gap_coarse`, `avg_rating_month` | Use as robustness/appendix only because it mechanically includes the main predictor. |
| Scenario diversity | `scenario_entropy` | Diversity of detected use-case categories in reviews. | Product-month | normalized Shannon entropy over scenario categories | `review_text`, scenario lexicon | Low values can mean narrow use, sparse reviews, or lexicon undercoverage. |
| Scenario lock-in | `lockin_index` | Inverse of scenario diversity. Higher values indicate narrower detected use-case framing. | Product-month | 1 - `scenario_entropy` | `scenario_entropy` | Main lock-in outcome. |
| Semantic mismatch | `semantic_gap_coarse` | Distance between static product metadata language and review discourse in the same product-month. | Product-month | 1 - cosine similarity using unigram/bigram count vectors | `title`, `description`, `bullet_points`, `review_text` | Feasibility proxy; not a historical copy-change measure. |
| Promotional density | `promo_density_total` | Promotional keyword/phrase density in product metadata. | Product-month | matched promo phrases / token count * 100 | metadata text, promo lexicon | Static metadata repeated across review months. |
| Natural/clean density | `promo_density_natural_clean` | Density of natural, clean, mineral, gentle, reef-safe, fragrance-free, vegan, and similar terms. | Product-month | matched natural-clean phrases / token count * 100 | metadata text, promo lexicon | Used for natural-promo grouping. |
| Abstractness | `abstractness_ratio` | Share of matched concrete/abstract terms below concreteness threshold. | Product-month | low-concreteness matched terms / scored matched terms | metadata text, concreteness dictionary | Dictionary is domain-specific and preliminary. |
| SPF group | `spf_group` | SPF intensity category. | Product | high = SPF 50+, mid = 31-49, low = <=30 | extracted SPF value | Four products lack SPF extraction. |
| Brand type | `brand_type` | Heuristic brand-positioning category. | Product | drugstore derm / mass sun care / premium import beauty / other | brand name | Rule-based; should be validated before publication. |
| Experiential complaint | `white_cast_review_share` | Share of reviews mentioning white cast or related residue terms. | Product | matching reviews / all reviews for product | `review_text` | Product-level descriptive signal. |
| Experiential complaint | `greasy_texture_review_share` | Share of reviews mentioning greasy, oily, shiny, sticky, or heavy texture. | Product | matching reviews / all reviews for product | `review_text` | Product-level descriptive signal. |
| Experiential complaint | `burn_failure_review_share` | Share of reviews mentioning sunburn or perceived protection failure. | Product | matching reviews / all reviews for product | `review_text` | Product-level descriptive signal. |
| Reported claim terms | `promo_relay_keyword_*` | Review language that appears to relay product claims using words such as says, claimed, advertised, or bought because. | Review/year/product | regex match on relay pattern + target keyword | `review_text` | Quasi-historical proxy; not a substitute for page snapshots. |
| Keyword drift | `rating_slope_per_month` | Monthly rating trend among reviews mentioning a keyword. | Keyword-month | OLS slope of mean rating by month index | `review_text`, `rating`, `review_date` | Star rating is a rough sentiment proxy; p-values exploratory. |

## Preferred Dependent Variables

Main models should use:

- `trust_response_index`
- `scenario_entropy`
- `lockin_index`
- `skepticism_ratio`

Use `trust_decline_index_theory` only as an appendix/robustness measure.

