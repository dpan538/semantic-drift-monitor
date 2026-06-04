# Phase 1 Collection Protocol

## Goal

Phase 1 prepares a small feasibility pilot for sunscreen and SPF skincare products. The target is not scale. The target is to verify that the project can produce a trustworthy product-month panel from permitted data.

Recommended pilot size:

- 50-80 SKUs.
- timestamped reviews where available.
- current product-page snapshots.
- at least one source registry row for every data source.

## Compliance Gate

Before collecting from any platform, record:

- platform name;
- source URL or API endpoint;
- access method;
- Terms of Service review status;
- robots.txt review status where applicable;
- whether collection is allowed;
- collection date;
- collector name;
- notes on rate limits, privacy constraints, and redistribution limits.

Use `templates/source_registry_template.csv` as the starting point.

This repository does not include tools for bypassing CAPTCHAs, login walls, access controls, rate limits, or anti-bot systems.

## Preferred Data Sources

Preferred, in order:

1. Official APIs, such as product advertising or approved review APIs.
2. Licensed or public research datasets.
3. Manually exported data where platform terms allow it.
4. Static snapshots collected with permission.
5. Public pages only when Terms of Service and robots rules permit collection.

For the first sunscreen/SPF feasibility pilot, see `docs/phase1_source_selection.md`. The recommended starting point is a local import from Amazon Reviews 2023 rather than live platform scraping.

## Minimum Input Files

Create these local files. They are ignored by git by default:

```text
data/raw/products.csv
data/raw/snapshots.csv
data/raw/reviews.csv
```

Templates:

```text
templates/product_master_seed.csv
templates/snapshot_import_template.csv
templates/review_import_template.csv
```

## Phase 1 Commands

Check local environment:

```bash
python3 scripts/00_check_environment.py
```

Prepare local ignored work folders:

```bash
python3 scripts/01_prepare_phase1_workspace.py
```

Run the demo pipeline:

```bash
python3 run_pipeline.py --demo
```

Run on local Phase 1 data:

```bash
python3 scripts/03_validate_phase1_inputs.py

python3 run_pipeline.py \
  --products data/raw/products.csv \
  --snapshots data/raw/snapshots.csv \
  --reviews data/raw/reviews.csv

python3 scripts/06_summarize_phase1_run.py

python3 scripts/07_phase1_analysis.py

python3 scripts/08_phase1_deep_dive.py
```

Use strict validation when the feasibility pilot is expected to meet the minimum review-count and temporal-coverage gates:

```bash
python3 scripts/03_validate_phase1_inputs.py --strict
```

## Static Snapshot Experiment

If a target website permits collection, product-page URLs can be tested with:

```bash
python3 scripts/02_collect_static_snapshots.py \
  --targets data/raw/collection_targets.csv \
  --out data/raw/snapshots.csv \
  --confirm-compliance
```

The command refuses to run without `--confirm-compliance`.

For platforms with restrictive rules, do not use static page fetching. Use an official API, licensed dataset, or manual export instead.

## Success Criteria

The Phase 1 environment is ready when:

- the environment check passes for Python and core dependencies;
- the demo pipeline runs;
- `data/raw/products.csv`, `data/raw/snapshots.csv`, and `data/raw/reviews.csv` exist for the pilot source;
- every source has a source registry row;
- the generated `outputs/product_month_panel.csv` has non-empty rows;
- skepticism, value, repurchase, and scenario indicators are not all zero.
