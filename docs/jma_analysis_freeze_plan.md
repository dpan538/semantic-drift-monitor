# JMA Analysis Freeze Plan

Freeze ID: `phase1_jma_feasibility_v0_1`  
Date: 2026-06-04  
Target journal: Journal of Marketing Analytics

## Freeze Purpose

This freeze marks the first manuscript-oriented analysis package for the sunscreen/SPF consumer review feasibility study.

It is not a final publication dataset. It is a stable base for drafting a Journal of Marketing Analytics manuscript.

## Frozen Public Inputs

Public, committed inputs:

- lexical dictionaries in `dictionaries/`;
- analysis scripts in `scripts/`;
- demo fixtures in `examples/`;
- non-raw aggregate reports in `reports/phase1/`.

Ignored local inputs:

- `data/raw/products.csv`
- `data/raw/snapshots.csv`
- `data/raw/reviews.csv`
- `data/raw/source_registry.csv`
- raw Amazon Reviews 2023 JSONL/JSONL.GZ files, if downloaded locally.

## Frozen Sample

Current Phase 1 sample:

- 100 products;
- 50,000 reviews;
- 9,124 product-month rows;
- review date span: 2005-03-18 to 2023-05-12;
- 96 products with extracted SPF value;
- static metadata expanded to review months for feasibility modelling only.

## Frozen Public Outputs

Sample and run summaries:

- `reports/phase1/source_selection_summary.csv`
- `reports/phase1/product_metric_summary.csv`
- `reports/phase1/phase1_run_summary.md`

Analysis outputs:

- `reports/phase1/analysis/phase1_analysis_report.md`
- `reports/phase1/analysis/fixed_effect_models.csv`
- `reports/phase1/analysis/keyword_sentiment_drift.csv`
- `reports/phase1/analysis/spf_group_comparison.csv`
- `reports/phase1/analysis/attenuation_group_contrast.csv`
- `reports/phase1/analysis/monthly_trends.csv`
- `reports/phase1/analysis/figures/`

Deep-dive outputs:

- `reports/phase1/deep_dive/phase1_deep_dive_report.md`
- `reports/phase1/deep_dive/split_index_fixed_effect_models.csv`
- `reports/phase1/deep_dive/segmented_fixed_effect_models.csv`
- `reports/phase1/deep_dive/time_period_summary.csv`
- `reports/phase1/deep_dive/spf_group_comparison.csv`
- `reports/phase1/deep_dive/brand_type_comparison.csv`
- `reports/phase1/deep_dive/natural_frequency_group_comparison.csv`
- `reports/phase1/deep_dive/promo_relay_keyword_summary.csv`
- `reports/phase1/deep_dive/product_month_panel_with_split_indices.csv`

## Reproducibility Commands

Assuming permitted local or streamed access to Amazon Reviews 2023:

```bash
python3 scripts/04_sample_amazon_reviews_2023.py \
  --metadata-jsonl https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main/raw/meta_categories/meta_Beauty_and_Personal_Care.jsonl \
  --reviews-jsonl https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main/raw/review_categories/Beauty_and_Personal_Care.jsonl \
  --target-products 100 \
  --min-reviews 20 \
  --min-review-months 12 \
  --max-reviews-per-product 500 \
  --out-dir data/raw \
  --report-dir reports/phase1

python3 scripts/05_expand_static_snapshots_to_review_months.py
python3 scripts/03_validate_phase1_inputs.py --strict

python3 run_pipeline.py \
  --products data/raw/products.csv \
  --snapshots data/raw/snapshots.csv \
  --reviews data/raw/reviews.csv

python3 scripts/06_summarize_phase1_run.py
python3 scripts/07_phase1_analysis.py
python3 scripts/08_phase1_deep_dive.py
```

## Freeze Rules

After this freeze:

1. Do not modify current Phase 1 result files without creating a new freeze ID.
2. New robustness checks should write to a new folder such as `reports/phase1_jma_v0_2/`.
3. Manuscript claims should cite the freeze ID and exact result file.
4. If new data or page snapshots are added, treat them as Phase 2, not as silent edits to Phase 1.

