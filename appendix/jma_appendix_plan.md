# JMA Appendix Plan

## Appendix A: Sample Construction

Include:

- sample construction flow;
- SPF inclusion criteria;
- All_Beauty insufficiency note;
- Beauty_and_Personal_Care final sample;
- source registry summary;
- static metadata expansion caveat.

Primary files:

- `docs/jma_sample_construction.md`
- `reports/phase1/source_selection_summary.csv`

## Appendix B: Variable Dictionary

Include:

- semantic gap;
- skepticism ratio;
- trust response index;
- theory trust decline index;
- scenario entropy;
- lock-in index;
- SPF group;
- brand type;
- experiential complaint shares;
- quasi-historical reported claim terms.

Primary file:

- `docs/jma_variable_definition_table.md`

## Appendix C: Lexicons and Regex

Include:

- promotional lexicon;
- skepticism lexicon;
- value complaint lexicon;
- scenario lexicon;
- concreteness dictionary;
- reported-claim regex patterns;
- experience complaint regex patterns.

Primary files:

- `dictionaries/`
- `scripts/08_phase1_deep_dive.py`

## Appendix D: Model Specifications

Include:

- main product-month fixed effects models;
- split-index models;
- segmented models by SPF, time period, brand type, and natural-promo frequency;
- outcome definitions;
- weighting scheme.

Primary files:

- `reports/phase1/analysis/fixed_effect_models.csv`
- `reports/phase1/deep_dive/split_index_fixed_effect_models.csv`
- `reports/phase1/deep_dive/segmented_fixed_effect_models.csv`

## Appendix E: Keyword Drift

Include:

- keyword drift slopes;
- mention counts;
- normal-approx p-values;
- multiple-testing correction in the next analysis version.

Primary file:

- `reports/phase1/analysis/keyword_sentiment_drift.csv`

## Appendix F: Reported Promotional Claim Terms

Include:

- relay keyword summary;
- yearly relay counts;
- explanation that these are quasi-historical proxies, not page snapshots.

Primary files:

- `reports/phase1/deep_dive/promo_relay_keyword_summary.csv`
- `reports/phase1/deep_dive/promo_relay_keyword_yearly.csv`

## Appendix G: Manual Validation

To be added:

- annotation codebook;
- sampled review sentences;
- coder agreement;
- precision/recall/F1 for skepticism, value complaint, scenario, and reported claim extraction.

Local working file:

- `data/interim/annotations/phase1_review_annotation_sample.csv`

This file contains review text and is not committed to the public repository.

