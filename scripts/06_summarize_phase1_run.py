#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize a Phase 1 semantic drift run.")
    parser.add_argument("--products", type=Path, default=Path("data/raw/products.csv"))
    parser.add_argument("--reviews", type=Path, default=Path("data/raw/reviews.csv"))
    parser.add_argument("--panel", type=Path, default=Path("outputs/product_month_panel.csv"))
    parser.add_argument("--selection-summary", type=Path, default=Path("reports/phase1/source_selection_summary.csv"))
    parser.add_argument("--out-md", type=Path, default=Path("reports/phase1/phase1_run_summary.md"))
    parser.add_argument("--out-csv", type=Path, default=Path("reports/phase1/product_metric_summary.csv"))
    parser.add_argument("--annotation-sample", type=Path, default=Path("data/interim/annotations/phase1_review_annotation_sample.csv"))
    parser.add_argument("--annotation-sample-size", type=int, default=300)
    return parser.parse_args()


def describe_series(series: pd.Series) -> dict[str, float]:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return {"mean": 0.0, "p25": 0.0, "median": 0.0, "p75": 0.0, "max": 0.0}
    return {
        "mean": float(clean.mean()),
        "p25": float(clean.quantile(0.25)),
        "median": float(clean.quantile(0.50)),
        "p75": float(clean.quantile(0.75)),
        "max": float(clean.max()),
    }


def main() -> int:
    args = parse_args()
    products = pd.read_csv(args.products)
    reviews = pd.read_csv(args.reviews)
    panel = pd.read_csv(args.panel)
    selection = pd.read_csv(args.selection_summary) if args.selection_summary.exists() else pd.DataFrame()

    metric_columns = [
        "promo_density_total",
        "promo_density_natural_clean",
        "promo_density_clinical_premium",
        "abstractness_ratio",
        "semantic_gap_coarse",
        "skepticism_ratio",
        "value_complaint_ratio",
        "negative_repurchase_ratio",
        "scenario_entropy",
        "attenuation_index_exploratory",
    ]

    product_metrics = (
        panel.groupby("product_id")[metric_columns + ["review_count_month"]]
        .mean(numeric_only=True)
        .reset_index()
        .rename(columns={"review_count_month": "mean_reviews_per_active_month"})
    )
    product_metrics = product_metrics.merge(
        products[["product_id", "brand", "product_name", "spf_value", "mineral_or_chemical"]],
        on="product_id",
        how="left",
    )
    if not selection.empty:
        product_metrics = product_metrics.merge(
            selection[["product_id", "review_count", "first_review_date", "last_review_date", "review_span_months", "matched_terms"]],
            on="product_id",
            how="left",
        )
    product_metrics = product_metrics.sort_values("attenuation_index_exploratory", ascending=False)

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    product_metrics.to_csv(args.out_csv, index=False)

    reviews["review_date"] = pd.to_datetime(reviews["review_date"], errors="coerce")
    review_span = ""
    if not reviews["review_date"].dropna().empty:
        review_span = f"{reviews['review_date'].min().date()} to {reviews['review_date'].max().date()}"

    annotation = reviews.sample(
        n=min(args.annotation_sample_size, len(reviews)),
        random_state=538,
    )[
        ["review_id", "product_id", "review_date", "rating", "verified_purchase", "review_title", "review_text"]
    ].copy()
    for column in [
        "skepticism_label",
        "value_complaint_label",
        "clarity_issue_label",
        "repurchase_label",
        "scenario_label",
        "annotator_notes",
    ]:
        annotation[column] = ""
    args.annotation_sample.parent.mkdir(parents=True, exist_ok=True)
    annotation.to_csv(args.annotation_sample, index=False)

    lines: list[str] = []
    lines.append("# Phase 1 Run Summary")
    lines.append("")
    lines.append("## Corpus")
    lines.append("")
    lines.append(f"- Products: {len(products):,}")
    lines.append(f"- Reviews: {len(reviews):,}")
    lines.append(f"- Product-month rows: {len(panel):,}")
    lines.append(f"- Review date span: {review_span or 'unknown'}")
    lines.append(f"- Products with SPF value extracted: {(products['spf_value'].fillna('').astype(str) != '').sum():,}")
    lines.append("")
    lines.append("## Metric Distributions")
    lines.append("")
    lines.append("| metric | mean | p25 | median | p75 | max |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for column in metric_columns:
        stats = describe_series(panel[column])
        lines.append(
            f"| `{column}` | {stats['mean']:.4f} | {stats['p25']:.4f} | {stats['median']:.4f} | {stats['p75']:.4f} | {stats['max']:.4f} |"
        )
    lines.append("")
    lines.append("## Top Products by Exploratory Attenuation Index")
    lines.append("")
    lines.append("| product_id | brand | review_count | attenuation | skepticism | value_complaint | scenario_entropy | matched_terms |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---|")
    for _, row in product_metrics.head(15).iterrows():
        lines.append(
            "| {product_id} | {brand} | {review_count} | {attenuation:.4f} | {skepticism:.4f} | {value:.4f} | {entropy:.4f} | {terms} |".format(
                product_id=row.get("product_id", ""),
                brand=str(row.get("brand", "")).replace("|", "/"),
                review_count=int(row.get("review_count", 0)) if pd.notna(row.get("review_count", 0)) else 0,
                attenuation=float(row.get("attenuation_index_exploratory", 0)),
                skepticism=float(row.get("skepticism_ratio", 0)),
                value=float(row.get("value_complaint_ratio", 0)),
                entropy=float(row.get("scenario_entropy", 0)),
                terms=str(row.get("matched_terms", "")).replace("|", "/"),
            )
        )
    lines.append("")
    lines.append("## Interpretation Notes")
    lines.append("")
    lines.append("- This is a feasibility run using static product metadata repeated across observed review months.")
    lines.append("- It should not be interpreted as evidence of historical product-page copy changes.")
    lines.append("- The exploratory attenuation index is a monitoring aid, not a validated latent construct.")
    lines.append("- The next validation step is human annotation of the review sample written to `data/interim/annotations/phase1_review_annotation_sample.csv`.")
    lines.append("")

    args.out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {args.out_md}")
    print(f"wrote {args.out_csv}")
    print(f"wrote {args.annotation_sample}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

