# Phase 1 Source Selection

## Recommended First Source

The safest first feasibility source is the McAuley Lab Amazon Reviews 2023 dataset.

Why it fits Phase 1:

- It is a public research dataset rather than a live scraping target.
- It includes review text, ratings, helpful votes, verified-purchase flags, and timestamps.
- It includes item metadata such as title, description, features, price, images, and average rating where available.
- The Beauty and Personal Care category is large enough to sample sunscreen and SPF skincare products.

Primary source pages:

- `https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023`
- `https://amazon-reviews-2023.github.io/`

Record the chosen dataset files in `data/raw/source_registry.csv` before running the pilot.

## Candidate Product Criteria

Phase 1 should select 80-100 products after a 50-80 product feasibility dry run.

Recommended inclusion criteria:

- product metadata contains at least one sunscreen/SPF keyword;
- product has a non-empty title;
- product has description, features, or category metadata;
- at least 20 reviews;
- preferably at least 12 months between first and last review;
- review text is present and timestamped;
- the product appears to be sunscreen, sunblock, SPF moisturizer, or SPF skincare.

Suggested sunscreen/SPF query terms:

- `sunscreen`
- `sun screen`
- `sunblock`
- `spf`
- `broad spectrum`
- `uva`
- `uvb`
- `zinc oxide`
- `titanium dioxide`
- `reef safe`

## Sampling Strategy

The first sample should not simply take the most-reviewed items. It should preserve variation.

Suggested strategy:

1. Filter by sunscreen/SPF query terms.
2. Keep products above minimum review-count and time-span thresholds.
3. Rank by review count and metadata completeness.
4. Select 80-100 products, but avoid letting one brand dominate.
5. Preserve a smaller 50-80 product dry-run subset for feasibility testing.

The provided sampler uses deterministic sorting and can be rerun with different thresholds.

## Output Tables

Run:

```bash
python3 scripts/04_sample_amazon_reviews_2023.py \
  --metadata-jsonl data/raw/meta_Beauty_and_Personal_Care.jsonl.gz \
  --reviews-jsonl data/raw/Beauty_and_Personal_Care.jsonl.gz \
  --target-products 100 \
  --min-reviews 20 \
  --min-review-months 12
```

Expected outputs:

```text
data/raw/products.csv
data/raw/snapshots.csv
data/raw/reviews.csv
data/raw/source_registry.csv
data/raw/collection_targets.csv
reports/phase1/source_selection_summary.csv
```

Then validate and run the pipeline:

```bash
python3 scripts/03_validate_phase1_inputs.py --strict

python3 run_pipeline.py \
  --products data/raw/products.csv \
  --snapshots data/raw/snapshots.csv \
  --reviews data/raw/reviews.csv
```

## Interpretation Limits

Amazon Reviews 2023 is excellent for a feasibility pilot, but it is still a historical public dataset. It does not provide a monthly sequence of live product-page copy changes. For a stronger longitudinal study, pair it with prospective page snapshots collected from permitted sources.

