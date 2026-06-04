# Phase 1 Run Summary

## Corpus

- Products: 100
- Reviews: 50,000
- Product-month rows: 9,124
- Review date span: 2005-03-18 to 2023-05-12
- Products with SPF value extracted: 96

## Metric Distributions

| metric | mean | p25 | median | p75 | max |
|---|---:|---:|---:|---:|---:|
| `promo_density_total` | 5.7869 | 3.1532 | 5.3846 | 8.0000 | 20.0000 |
| `promo_density_natural_clean` | 2.0162 | 0.3236 | 1.2780 | 3.3333 | 10.0000 |
| `promo_density_clinical_premium` | 0.1296 | 0.0000 | 0.0000 | 0.0000 | 2.0408 |
| `abstractness_ratio` | 0.1553 | 0.0000 | 0.0909 | 0.2500 | 1.0000 |
| `semantic_gap_coarse` | 0.7816 | 0.7045 | 0.7797 | 0.8643 | 1.0000 |
| `skepticism_ratio` | 0.0417 | 0.0000 | 0.0000 | 0.0625 | 1.0000 |
| `value_complaint_ratio` | 0.0013 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| `negative_repurchase_ratio` | 0.0007 | 0.0000 | 0.0000 | 0.0000 | 0.5000 |
| `scenario_entropy` | 0.1642 | 0.0000 | 0.0000 | 0.3955 | 1.0000 |
| `attenuation_index_exploratory` | 0.1802 | 0.1363 | 0.2000 | 0.2000 | 0.5000 |

## Top Products by Exploratory Attenuation Index

| product_id | brand | review_count | attenuation | skepticism | value_complaint | scenario_entropy | matched_terms |
|---|---|---:|---:|---:|---:|---:|---|
| B0C52N53Q3 | Neutrogena | 1165 | 0.2166 | 0.0625 | 0.0008 | 0.0120 | sunscreen; spf; broad spectrum; sun protection |
| B008KYYLPI | Hawaiian Tropic | 744 | 0.2126 | 0.0857 | 0.0020 | 0.0698 | sunscreen; spf; broad spectrum; sun protection; uva; uvb |
| B09JTF1KYX | L'Oreal Paris | 1316 | 0.2093 | 0.0444 | 0.0007 | 0.0210 | spf; broad spectrum; uva; uvb |
| B01MYQW5SM | Neutrogena | 3821 | 0.2053 | 0.0993 | 0.0002 | 0.1228 | sunscreen; spf; broad spectrum; sun protection; uva; uvb |
| B0874GFK2Z | Australian Gold | 1404 | 0.2010 | 0.0352 | 0.0000 | 0.0478 | sunscreen; sunblock; spf; broad spectrum; sun protection; uva; uvb |
| B0BF9M6QM7 | Hawaiian Tropic | 892 | 0.2010 | 0.0589 | 0.0002 | 0.0838 | sunscreen; spf; broad spectrum; sun protection; uva; uvb |
| B01LWUS3BA | REVLON | 1509 | 0.1992 | 0.0150 | 0.0000 | 0.0290 | spf; sun protection |
| B095FMX9LT | Sun Bum | 2182 | 0.1992 | 0.0298 | 0.0011 | 0.0513 | sunscreen; spf; broad spectrum; sun protection; uva; uvb |
| B09NN2726V | Palmer's | 968 | 0.1985 | 0.0152 | 0.0004 | 0.0309 | spf; sun protection |
| B0B3LHMSN2 | Natural Ice | 1482 | 0.1982 | 0.0087 | 0.0017 | 0.0287 | sunscreen; spf; broad spectrum; sun protection; uva; uvb |
| B002JAYMEE | Neutrogena | 2518 | 0.1981 | 0.0997 | 0.0003 | 0.1597 | sunscreen; spf; broad spectrum; sun protection; uva; uvb |
| B08748D8TF | Australian Gold | 1145 | 0.1969 | 0.0446 | 0.0000 | 0.0828 | sunscreen; sunblock; spf; broad spectrum; sun protection; uva; uvb |
| B00HB2JQNM | Olay | 1183 | 0.1957 | 0.0348 | 0.0000 | 0.0736 | spf; sun protection |
| B0BQX52B49 | Vive | 3209 | 0.1952 | 0.0015 | 0.0006 | 0.0269 | sunscreen |
| B004D2C57M | Neutrogena | 2065 | 0.1946 | 0.0292 | 0.0051 | 0.0777 | sunscreen; spf; broad spectrum |

## Interpretation Notes

- This is a feasibility run using static product metadata repeated across observed review months.
- It should not be interpreted as evidence of historical product-page copy changes.
- The exploratory attenuation index is a monitoring aid, not a validated latent construct.
- The next validation step is human annotation of the review sample written to `data/interim/annotations/phase1_review_annotation_sample.csv`.
