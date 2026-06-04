# Anonymous Article File Outline

Working title:

**Semantic Gap, Scenario Lock-In, and Trust Response in Sunscreen Consumer Reviews: A Feasibility Study Using Amazon Reviews 2023**

This file is for the anonymous article manuscript. Do not include author names, affiliations, acknowledgements, identifiable repository ownership statements, or self-identifying notes.

## Abstract

Use the abstract in `manuscript/abstract_and_keywords.md`. Keep it under 200 words.

## Keywords

Use 3-6 keywords from `manuscript/abstract_and_keywords.md`.

## 1. Introduction

Purpose:

- Frame the problem as applied marketing analytics.
- Explain that consumer reviews capture product claim interpretation, usage scenarios, and concrete experiential failures.
- Introduce sunscreen/SPF products as a useful domain because claims combine functional protection, sensory experience, and semantic labels such as natural, mineral, sensitive, gentle, and reef safe.
- State that existing review analytics work often measures sentiment, topics, and satisfaction, but rarely separates semantic mismatch, trust response, and scenario lock-in.

Proposed contribution paragraph:

> This study develops and tests a reproducible marketing analytics pipeline for measuring how semantic mismatch in consumer-facing product discourse is associated with trust response, scenario lock-in, and experiential complaint signals in sunscreen reviews.

## 2. Literature Review

Keep this focused. Suggested subsections:

1. Marketing analytics and data-rich marketing.
2. Online reviews, eWOM, and consumer-generated data.
3. Review text mining and marketing meaning extraction.
4. Consumer skepticism, expectation-disconfirmation, and claim credibility.
5. Product semantics and semantic change.

## 3. Data and Sample

Must include:

- Amazon Reviews 2023 as the data source.
- Beauty_and_Personal_Care sample construction.
- Why All_Beauty was insufficient.
- Strict SPF inclusion criteria.
- 100 products, 50,000 reviews, 9,124 product-month rows.
- Review span: 2005-03-18 to 2023-05-12.
- 96 products with extracted SPF.
- Static metadata limitation.

Required sentence:

> Product metadata are treated as static product-semantic descriptors and expanded to product-month observations only for feasibility modelling. They are not interpreted as historical changes in Amazon product pages.

## 4. Measures

Key variables:

- `semantic_gap_coarse`
- `skepticism_ratio`
- `trust_response_index`
- `trust_decline_index_theory`
- `scenario_entropy`
- `lockin_index`
- `spf_group`
- experiential complaint shares
- reported promotional claim terms

The variable definition table should draw from `docs/jma_variable_definition_table.md`.

## 5. Empirical Strategy

Main panel model:

```text
Y_it = beta_1 lag_semantic_gap_i,t-1
     + beta_2 log(review_count_it)
     + beta_3 controls_it
     + product fixed effects
     + month fixed effects
     + error_it
```

Main outcomes:

1. `skepticism_ratio`
2. `trust_response_index`
3. `scenario_entropy`
4. `lockin_index`

Recommended emphasis:

- Treat `lockin_index` and `scenario_entropy` as the strongest outcomes.
- Report direct trust response as non-significant in the main model.
- Use `trust_decline_index_theory` as appendix/robustness, not the primary dependent variable.

## 6. Results

Suggested order:

1. Sample construction and descriptive overview.
2. Descriptive trends in skepticism and scenario entropy.
3. SPF group comparison.
4. Fixed-effects panel results.
5. Keyword drift.
6. Segmented and robustness analyses.
7. Quasi-historical reported claim terms.

Core result statements:

- Lagged semantic gap does not significantly predict response-only trust decline.
- Lagged semantic gap significantly predicts scenario lock-in.
- White cast shows strong negative keyword drift.
- Natural and mineral do not show comparable devaluation.
- High-SPF products show higher skepticism and more concrete experiential failure signals.

## 7. Discussion

Central discussion claim:

> Semantic mismatch does not directly translate into generalized distrust in this feasibility sample. It appears more strongly as scenario lock-in, while direct negative response is concentrated around concrete experiential failures.

Discuss why:

- sunscreen claims have functional grounding;
- natural/mineral may retain product diagnosticity;
- high-SPF products create stronger performance and sensory expectations;
- consumer distrust may be localized around experience attributes rather than broad claim skepticism.

## 8. Managerial Implications

Suggested points:

- Brands should monitor semantic gap, not only sentiment.
- High-SPF brands should monitor texture, white cast, greasiness, and burn-failure complaints.
- Natural/mineral claims are not necessarily devalued, but may still interact with scenario lock-in.
- Review analytics can function as an early-warning system for claim-performance mismatch.

## 9. Limitations and Future Research

Must include:

- Amazon Reviews 2023 is not complete market data.
- Public review data contain self-selection bias.
- Static metadata are not historical promotional copy.
- The study is a feasibility study, not a causal proof.
- Future work should collect historical page snapshots, brand pages, ads, platform search data, and multi-category replication.

## References

Use Harvard author-date style. Start from `manuscript/references_harvard_seed.md`.

