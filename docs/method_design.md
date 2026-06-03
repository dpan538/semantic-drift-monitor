# Method Design

## Scope

The first pilot studies sunscreen and SPF skincare products. The category is deliberately narrow because the research design needs clear functional expectations, dense promotional discourse, and enough consumer reviews to build a product-month panel.

The pipeline is designed for two layers of evidence:

1. Retrospective review analysis: timestamped reviews, ratings, and price/rating proxies from the past 12-24 months.
2. Prospective promotional snapshots: product pages, image OCR, titles, bullets, descriptions, price, ratings, and visible platform tags captured at regular intervals.

The strongest longitudinal design uses both layers. If historical product pages are not available, claims about causal timing should be framed cautiously.

## Constructs

### Commercial Semantic Drift

Commercial semantic drift is operationalized as a divergence between promotional meaning and consumer meaning over time.

Predictors include:

- Promotional density
- Natural/clean claim density
- Clinical/premium claim density
- Abstractness ratio
- Coarse semantic gap
- Aspect-level claim-review mismatch

### Commodity Potential Attenuation

Commodity potential attenuation is not treated as current sales decline. It is measured through observable consumer-side outcomes:

- skepticism ratio
- value complaint ratio
- clarity issue ratio
- negative repurchase ratio
- scenario entropy decline

The project keeps these outcomes separate in the first stage. A composite attenuation index is exploratory until validated.

## Identification Logic

The preferred panel model is:

```text
Y_it = alpha_i + gamma_t + beta * Drift_i,t-1 + theta * Controls_it + epsilon_it
```

Where:

- `i` is product.
- `t` is month.
- `alpha_i` is a product fixed effect.
- `gamma_t` is a month fixed effect.
- `Drift_i,t-1` is a lagged drift or promotional-intensity measure.
- `Y_it` is an attenuation outcome.

This design asks whether promotional drift indicators precede later consumer-side weakening signals after controlling for product and time effects.

## Falsification Criteria

The main hypothesis is not supported if high promotional density or high abstractness does not predict higher skepticism, value complaints, clarity issues, repeatability weakness, or scenario narrowing after reasonable controls.

The keyword fatigue hypothesis is not supported if increasing use of terms such as `natural`, `clean`, or `gentle` does not coincide with worsening review sentiment, skeptical co-occurrence, or lower downstream product evaluation.

Alternative explanations must be checked, especially:

- price changes
- discount changes
- formula or packaging changes
- platform review policy changes
- seasonality
- fake or incentivized reviews

## Minimum Feasibility Pilot

Start with 50-80 SKUs before scaling.

Feasibility criteria:

- At least 60% of SKUs have timestamped reviews across multiple months.
- Most active product-month cells have enough text to compute ratios.
- Promotional and consumer-side keywords appear with non-trivial frequency.
- Skepticism/value/repurchase/scenario metrics are not all zero or dominated by one product.

