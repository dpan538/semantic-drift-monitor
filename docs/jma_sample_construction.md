# JMA Sample Construction

## Data Source

The first manuscript version uses Amazon Reviews 2023, a public research dataset produced by McAuley Lab.

Dataset pages:

- https://amazon-reviews-2023.github.io/
- https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023

Dataset citation requested by the dataset maintainers:

> Hou, Y., Li, J., He, Z., Yan, A., Chen, X. and McAuley, J. (2024) Bridging Language and Items for Retrieval and Recommendation. arXiv:2403.03952.

## Sample Construction Logic

The feasibility study began with a smaller category and then moved to a larger category to preserve strict inclusion rules while obtaining a viable product-month panel.

| Step | Dataset / Filter | Products | Reviews | Notes |
|---:|---|---:|---:|---|
| 1 | Amazon Reviews 2023 / All_Beauty | 53 qualified SKUs | not retained as final | Strict SPF filter produced too few qualified products. |
| 2 | Amazon Reviews 2023 / Beauty_and_Personal_Care | 100 qualified SKUs | 50,000 | Final sample under strict SPF inclusion criteria. |
| 3 | Static metadata expanded to review months | 100 | 50,000 | Static product descriptors repeated only for feasibility modelling. |
| 4 | Product-month panel | 100 | 9,124 product-month rows | Review date span: 2005-03-18 to 2023-05-12. |
| 5 | SPF extraction | 96/100 products | — | SPF values extracted by regex from product title/metadata. |

## Inclusion Criteria

Final inclusion required:

- product title or category contains a primary SPF/sunscreen indicator;
- product has non-empty metadata title;
- at least 20 reviews;
- at least 12 months between first and last observed review;
- review text and timestamp are available;
- product appears to be sunscreen, sunblock, SPF moisturizer, SPF lip product, or SPF skincare.

Primary SPF/sunscreen indicators:

- `sunscreen`
- `sun screen`
- `sunblock`
- `spf`
- `broad spectrum`
- `sun protection`

Auxiliary indicators are recorded but cannot by themselves qualify a product:

- `uva`
- `uvb`
- `zinc oxide`
- `titanium dioxide`
- `reef safe`

## Why Beauty_and_Personal_Care Replaced All_Beauty

The initial `All_Beauty` subset produced only 53 qualified SPF SKUs under strict inclusion criteria. To obtain a feasible product-month panel while preserving strict sunscreen relevance, the analysis was rerun on `Beauty_and_Personal_Care`, yielding 100 qualified SPF SKUs and 50,000 reviews.

This should be reported as a sample-construction decision, not as opportunistic tuning.

## Static Metadata Constraint

Product metadata are treated as **static product-semantic descriptors** and expanded to product-month observations only for feasibility modelling.

They are **not** interpreted as historical changes in Amazon product pages.

Suggested manuscript sentence:

> Product metadata are treated as static product-semantic descriptors and expanded to product-month observations only for feasibility modelling. They are not interpreted as historical changes in Amazon product pages.

## Public Outputs

Public, non-raw outputs:

- `reports/phase1/source_selection_summary.csv`
- `reports/phase1/product_metric_summary.csv`
- `reports/phase1/phase1_run_summary.md`
- `reports/phase1/analysis/phase1_analysis_report.md`
- `reports/phase1/deep_dive/phase1_deep_dive_report.md`

Raw review text is not committed to the public repository.

