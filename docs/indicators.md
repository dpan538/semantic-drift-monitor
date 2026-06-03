# Indicator Definitions

## Promotional Density

Promotional density is the number of matched promotional keywords or phrases per 100 words of promotional text.

```text
promo_density = matched_promo_terms / token_count * 100
```

The pipeline computes category-specific densities such as natural/clean, clinical/premium, efficacy, and sensorial.

## Abstractness Ratio

Abstractness ratio is the share of matched words or phrases whose concreteness score is below the configured threshold.

Unknown words are excluded from the denominator by default. This avoids treating every unscored term as abstract.

## Coarse Semantic Gap

Coarse semantic gap compares product promotional text against review text using TF-IDF vectors in the baseline pipeline.

```text
semantic_gap = 1 - cosine_similarity(promo_vector, review_vector)
```

This is interpretable as a rough distance measure. It should be supplemented by aspect-level analysis in publication work.

## Skepticism Ratio

```text
skepticism_ratio = skeptical_sentences / total_review_sentences
```

Skepticism includes terms such as `overhyped`, `gimmick`, `just marketing`, `fake reviews`, and related phrases.

## Value Complaint Ratio

```text
value_complaint_ratio = value_complaint_sentences / total_review_sentences
```

Value complaints include `overpriced`, `not worth it`, `waste of money`, and similar phrases.

## Negative Repurchase Ratio

```text
negative_repurchase_ratio = negative_repurchase_sentences / total_review_sentences
```

This captures direct language such as `will not buy again`, `would not repurchase`, and `not buying again`.

## Scenario Entropy

Scenario entropy measures use-case diversity in reviews.

```text
scenario_entropy = -sum(p_s * log(p_s)) / log(number_of_scenarios)
```

Lower entropy suggests narrower use-case framing. In some categories, narrowness can be commercially healthy, so interpretation must be category-sensitive.

## Exploratory Attenuation Index

The exploratory index combines standardized consumer-side outcomes:

- skepticism ratio
- value complaint ratio
- negative repurchase ratio
- lock-in risk

It is included for monitoring and exploratory analysis, not as the primary publication outcome until validated.

