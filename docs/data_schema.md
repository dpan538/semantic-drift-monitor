# Data Schema

The pipeline accepts CSV files for a first-stage pilot. Later versions can write Parquet or database tables.

## products.csv

One row per SKU.

Required columns:

- `product_id`
- `brand`
- `product_name`
- `category`

Recommended columns:

- `platform`
- `asin_or_sku`
- `subcategory`
- `spf_value`
- `mineral_or_chemical`
- `size_ml_or_oz`
- `product_url`

## snapshots.csv

One row per product-page snapshot.

Required columns:

- `product_id`
- `snapshot_date`
- `title`
- `description`

Recommended columns:

- `bullet_points`
- `image_ocr_text`
- `price`
- `rating_avg`
- `rating_count`
- `review_count`
- `sales_rank_proxy`

## reviews.csv

One row per review.

Required columns:

- `review_id`
- `product_id`
- `review_date`
- `rating`
- `review_text`

Recommended columns:

- `verified_purchase`
- `review_title`
- `helpful_votes`

## product_month_panel.csv

Generated output. One row per product-month.

Core columns:

- `product_id`
- `month`
- `review_count_month`
- `avg_rating_month`
- `promo_density_total`
- `promo_density_natural_clean`
- `promo_density_clinical_premium`
- `abstractness_ratio`
- `semantic_gap_coarse`
- `skepticism_ratio`
- `value_complaint_ratio`
- `negative_repurchase_ratio`
- `scenario_entropy`
- `lockin_risk`
- `attenuation_index_exploratory`

