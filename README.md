# Semantic Drift Monitor

**A computational pipeline to detect when promotional language erodes commodity potential**

This repository hosts the data pipeline, corpus schemas, lexical dictionaries, metric scripts, and audit tools for the research project:

**"Commercial Semantic Drift and Commodity Potential Attenuation."**

The project studies when promotional meaning construction stops clarifying a commodity and starts weakening its future commercial potential. It focuses on the divergence between **promotional language** produced by sellers, platforms, and creators and **consumer response language** expressed in reviews, Q&A, and public comments.

Primary pilot domain:

> Skincare and sunscreen products, especially promotional claims around `natural`, `clean`, `gentle`, `sensitive skin`, `dermatologist tested`, `reef safe`, `invisible`, and `no white cast`.

## Research Object

This project does not ask whether a product is objectively good or bad. It studies whether the meanings built around a commodity begin to drift away from consumer experience.

The central premise is methodological:

> `promo_language` and `consumer_language` must be stored separately before their divergence can be measured.

The project therefore separates:

- seller-generated product titles, bullet points, descriptions, badges, and packaging OCR;
- platform-generated tags, rankings, and visibility proxies;
- creator-generated captions, scripts, and disclosure markers;
- consumer-generated reviews, Q&A, complaints, repeat-purchase signals, and use-case descriptions.

## Core Constructs

**Commercial semantic drift** is a measurable divergence between the meaning structure created by promotional language and the meaning structure expressed in consumer responses over time.

**Commodity potential attenuation** is a decline in latent commercial capacity, not necessarily a decline in immediate sales. It is measured through separate consumer-side outcomes:

- trust erosion;
- clarity loss;
- usefulness mismatch;
- value-for-money skepticism;
- repeat-purchase weakness;
- use-case narrowing.

The repository treats attenuation as a multi-dimensional construct. A composite score is included only as an exploratory monitoring aid until validated.

## Core Design Principles

- **Separate evidence layers**: promotional snapshots, consumer reviews, Q&A, creator content, and market proxies are stored separately before being linked.
- **Longitudinal first**: semantic drift is a temporal process, so product-month panels are preferred over one-off cross-sectional comparisons.
- **Derived tables never overwrite originals**: cleaning, matching, scoring, and aggregation create new tables or output files.
- **Phrase-level matching**: multi-word expressions such as `not worth it`, `white cast`, and `dermatologist tested` are matched as phrases, not broken by whitespace.
- **Outcome separation**: semantic gap indicators are predictors; skepticism, value complaints, repurchase weakness, and scenario narrowing are outcomes.
- **Health-based gatekeeping**: corpus health checks decide which claims are permitted at each stage.
- **Compliance by design**: the repository does not include code for bypassing CAPTCHAs, login walls, rate limits, anti-bot systems, or platform access controls.
- **Transparent uncertainty**: absent data, short time windows, sparse reviews, and weak source coverage should be logged rather than hidden.

## Repository Structure

```text
dictionaries/       Lexicons for promotional claims, skepticism, value complaints, scenarios, and concreteness
docs/               Method design, data schema, indicators, and compliance notes
examples/           Small demo input files for products, snapshots, and reviews
semantic_drift_monitor/
  data_collection/  API/import adapters and collection utilities
  text_processing/  Cleaning, phrase matching, abstractness, and claim extraction
  metrics/          Overload, semantic gap, skepticism, lock-in, and attenuation indicators
  detection/        Drift alerts, logging, and evaluation helpers
outputs/            Generated product-month panels and reports, excluded from version control
logs/               Runtime alert logs, excluded from version control
```

Raw captures, platform credentials, private exports, and restricted source artifacts are intentionally excluded from version control.

## Key Tables

Expected input tables:

- `data/raw/products.csv`: product master table with SKU-level metadata.
- `data/raw/snapshots.csv`: product-page snapshots with titles, descriptions, bullets, image OCR, price, rating, and capture date.
- `data/raw/reviews.csv`: timestamped consumer reviews with rating, verified-purchase flag, and review text.

Bundled demo tables:

- `examples/demo_products.csv`
- `examples/demo_snapshots.csv`
- `examples/demo_reviews.csv`

Expected generated tables:

- `outputs/product_month_panel.csv`: product-month metric panel.
- `logs/alerts.log`: local drift-alert log.

Canonical future tables:

- `promo_snapshot`
- `promo_claim`
- `review`
- `review_sentence`
- `review_flags`
- `qa_thread`
- `creator_post`
- `market_panel`
- `keyword_panel`

See `docs/data_schema.md`.

## Key Outputs

The first-stage pipeline produces:

- product-month metric panels;
- promotional-density summaries;
- abstractness ratios;
- semantic-gap estimates;
- skepticism and value-complaint ratios;
- negative repurchase signals;
- scenario entropy scores;
- lock-in risk flags;
- exploratory attenuation index;
- local alert logs.

Publication-stage outputs should also include:

- human annotation samples;
- inter-annotator agreement;
- precision/recall/F1 for lexical or model-based flags;
- fixed-effects regression tables;
- event-study plots where copy changes are observable;
- corpus health and claim-permission reports.

## Scripts

Main entry point:

- `run_pipeline.py`: load product, snapshot, and review CSVs; compute product-month metrics; write outputs.

Data collection:

- `semantic_drift_monitor/data_collection/amazon_collector.py`: placeholder adapter for official APIs or permitted datasets.
- `semantic_drift_monitor/data_collection/utils.py`: polite retry helper.

Text processing:

- `semantic_drift_monitor/text_processing/cleaner.py`: normalize and split review text.
- `semantic_drift_monitor/text_processing/phrase_matcher.py`: phrase-level lexical matching.
- `semantic_drift_monitor/text_processing/abstractness.py`: concreteness/abstractness scoring.
- `semantic_drift_monitor/text_processing/claim_extractor.py`: promotional claim extraction.

Metrics:

- `semantic_drift_monitor/metrics/overload.py`: promotional density by category.
- `semantic_drift_monitor/metrics/gap.py`: lightweight n-gram semantic gap.
- `semantic_drift_monitor/metrics/skepticism.py`: skepticism and keyword sentiment drift helpers.
- `semantic_drift_monitor/metrics/lockin.py`: scenario entropy and use-case narrowing.
- `semantic_drift_monitor/metrics/attenuation.py`: exploratory attenuation index.
- `semantic_drift_monitor/metrics/panel_builder.py`: product-month panel construction.

Detection and evaluation:

- `semantic_drift_monitor/detection/drift_detector.py`: simple threshold alerts.
- `semantic_drift_monitor/detection/alert.py`: local alert logging.
- `semantic_drift_monitor/detection/evaluation.py`: kappa, binary classifier metrics, and permutation tests.

## Quick Start

Check the local environment and prepare ignored working folders:

```bash
git clone https://github.com/dpan538/semantic-drift-monitor.git
cd semantic-drift-monitor
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/00_check_environment.py
python3 scripts/01_prepare_phase1_workspace.py
```

Run the bundled demo:

```bash
python3 run_pipeline.py --demo
```

Expected outputs:

```text
outputs/product_month_panel.csv
logs/alerts.log
```

Run with your own permitted data:

```bash
python3 scripts/03_validate_phase1_inputs.py \
  --products data/raw/products.csv \
  --snapshots data/raw/snapshots.csv \
  --reviews data/raw/reviews.csv

python3 run_pipeline.py \
  --products data/raw/products.csv \
  --snapshots data/raw/snapshots.csv \
  --reviews data/raw/reviews.csv
```

If a target website explicitly permits static page collection, use the guarded Phase 1 snapshot experiment:

```bash
python3 scripts/02_collect_static_snapshots.py \
  --targets data/raw/collection_targets.csv \
  --out data/raw/snapshots.csv \
  --confirm-compliance
```

The snapshot command refuses to run without `--confirm-compliance`. For restrictive platforms, use an official API, licensed dataset, or permitted manual export instead.

## Current Repository Status

The current repository is a methods-and-pipeline baseline, not an inference-ready empirical corpus.

At this stage:

- demo data are synthetic and only verify that the pipeline runs;
- product-page collection adapters are placeholders until a permitted data source is selected;
- the semantic gap metric is intentionally lightweight and should be upgraded or validated before publication;
- the attenuation index is exploratory and should not be treated as a validated latent construct;
- human annotation and corpus health gates must be added before strong empirical claims.

This is intentional: the project uses explicit measurement and corpus-health gates to prevent premature claims.

## Research Roadmap

Immediate next steps:

1. Run `scripts/00_check_environment.py`.
2. Run `scripts/01_prepare_phase1_workspace.py`.
3. Select a permitted data source for sunscreen/SPF skincare products.
4. Build `product_master` for 50-80 pilot SKUs.
5. Import timestamped reviews and current product snapshots.
6. Validate phrase dictionaries against hand-labeled sentences.
7. Build the first product-month panel.
8. Run descriptive plots for promotional density, skepticism, value complaints, and scenario entropy.
9. Add fixed-effects and event-study scripts once longitudinal coverage is sufficient.

Scaling steps:

1. Expand to 200-300 SKUs.
2. Add Q&A and image OCR.
3. Add creator captions and disclosure markers.
4. Add aspect-level claim-review mismatch.
5. Add corpus health reports and claim-permission flags.
6. Publish frozen data snapshots and analysis-ready panels.

## Data Ethics and Access

Some platforms are API-governed, subscription-based, or restrictive about automated access. This repository does not include private cookies, login credentials, restricted raw captures, or prohibited platform exports.

For platform or review data:

- use official APIs, licensed datasets, static snapshots, or permitted manual exports where possible;
- store only fields needed for the research question;
- anonymize consumer identifiers before publication;
- preserve capture dates and source provenance;
- separate seller, platform, creator, and consumer fields;
- report platform-bias and access limitations.

See `docs/ethics_and_compliance.md`.

## License

Recommended licensing model:

- Code: MIT License.
- Dictionaries, documentation, and shareable annotations: CC BY-NC 4.0.
- Raw copyrighted source captures or platform-governed exports: not redistributed unless rights permit.

Final licensing should be confirmed before public release of any full corpus snapshot.

## Citation

If you use this corpus design or pipeline, please cite:

> Pan, Dai. *Semantic Drift Monitor: A Computational Pipeline for Commercial Semantic Drift and Commodity Potential Attenuation*. GitHub repository, 2026. https://github.com/dpan538/semantic-drift-monitor
