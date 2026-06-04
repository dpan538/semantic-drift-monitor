#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd


EXPERIENCE_KEYWORDS = {
    "white_cast": ["white cast", "white residue", "chalky", "ashy"],
    "greasy_texture": ["greasy", "oily", "shiny", "sticky", "heavy"],
    "burn_failure": ["still burned", "got burned", "sunburn", "burned", "did not protect"],
    "price_value": ["expensive", "overpriced", "not worth", "waste of money", "pricey"],
    "makeup_pilling": ["pills", "pilling", "under makeup", "foundation"],
}

PROMO_RELAY_KEYWORDS = [
    "natural",
    "mineral",
    "chemical-free",
    "reef safe",
    "gentle",
    "sensitive",
    "dermatologist",
    "white cast",
    "non-greasy",
    "clean",
    "broad spectrum",
]

PROMO_RELAY_PATTERNS = [
    r"\b(?:bought|tried|chose|picked|ordered)\b.{0,80}\b(?:because|since)\b.{0,80}\b(?:said|says|claimed|claims|advertised)\b",
    r"\b(?:it|this|label|box|package|description|ad|listing)\b.{0,60}\b(?:said|says|claimed|claims|advertised|promised)\b",
    r"\b(?:as advertised|not as advertised|claims to|claimed to|supposed to)\b",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deeper Phase 1 mining and segmented analyses.")
    parser.add_argument("--panel", type=Path, default=Path("outputs/product_month_panel.csv"))
    parser.add_argument("--products", type=Path, default=Path("data/raw/products.csv"))
    parser.add_argument("--reviews", type=Path, default=Path("data/raw/reviews.csv"))
    parser.add_argument("--product-summary", type=Path, default=Path("reports/phase1/product_metric_summary.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("reports/phase1/deep_dive"))
    return parser.parse_args()


def normal_p_value(t_stat: float) -> float:
    return float(math.erfc(abs(t_stat) / math.sqrt(2))) if np.isfinite(t_stat) else float("nan")


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    frame = pd.DataFrame({"value": values, "weight": weights}).replace([np.inf, -np.inf], np.nan).dropna()
    frame = frame[frame["weight"] > 0]
    if frame.empty:
        return float("nan")
    return float(np.average(frame["value"], weights=frame["weight"]))


def zscore(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    std = numeric.std()
    if not std or pd.isna(std):
        return numeric * 0
    return (numeric - numeric.mean()) / std


def add_indices(panel: pd.DataFrame) -> pd.DataFrame:
    df = panel.copy()
    rating_norm = (pd.to_numeric(df["avg_rating_month"], errors="coerce") - 1) / 4
    rating_decline = (1 - rating_norm.clip(lower=0, upper=1)).fillna(0)
    df["rating_decline_component"] = rating_decline
    df["trust_response_index"] = (
        0.55 * df["skepticism_ratio"].fillna(0)
        + 0.30 * df["value_complaint_ratio"].fillna(0)
        + 0.15 * rating_decline
    )
    df["trust_decline_index_theory"] = (
        0.40 * df["skepticism_ratio"].fillna(0)
        + 0.25 * df["value_complaint_ratio"].fillna(0)
        + 0.20 * df["semantic_gap_coarse"].fillna(0)
        + 0.15 * rating_decline
    )
    df["lockin_index"] = 1 - df["scenario_entropy"].fillna(0).clip(lower=0, upper=1)
    df["attenuation_two_axis_composite"] = (
        0.50 * df["lockin_index"]
        + 0.35 * df["trust_response_index"]
        + 0.15 * df["negative_repurchase_ratio"].fillna(0)
    )
    return df


def spf_group(value) -> str:
    try:
        spf = float(value)
    except (TypeError, ValueError):
        return "unknown"
    if spf >= 50:
        return "high_spf_50_plus"
    if spf <= 30:
        return "low_spf_30_or_less"
    return "mid_spf_31_49"


def time_period(month: str) -> str:
    year = pd.to_datetime(month).year
    if year <= 2010:
        return "2005_2010"
    if year <= 2016:
        return "2011_2016"
    return "2017_2023"


def brand_type(brand: object) -> str:
    value = str(brand).lower()
    derm = [
        "neutrogena",
        "cerave",
        "eucerin",
        "aveeno",
        "cetaphil",
        "la roche",
        "elta",
        "olay",
        "l'oreal",
        "roc",
    ]
    mass_sun = ["coppertone", "hawaiian tropic", "banana boat", "australian gold", "sun bum", "bullfrog"]
    premium = ["shiseido", "anessa", "supergoop", "clarins", "lancome", "biore", "etude", "skin aqua"]
    if any(term in value for term in derm):
        return "drugstore_derm"
    if any(term in value for term in mass_sun):
        return "mass_sun_care"
    if any(term in value for term in premium):
        return "premium_import_beauty"
    return "other_or_niche"


def ols_with_fe(df: pd.DataFrame, outcome: str, predictor: str, controls: list[str]) -> dict[str, object]:
    cols = [outcome, predictor, "product_id", "month", "review_count_month"] + controls
    work = df[cols].replace([np.inf, -np.inf], np.nan).dropna()
    if len(work) < 50 or work[predictor].std() == 0:
        return {"outcome": outcome, "predictor": predictor, "n": len(work), "status": "insufficient_variation"}
    y = work[outcome].to_numpy(dtype=float)
    numeric_cols = [predictor] + controls
    numeric = work[numeric_cols].to_numpy(dtype=float)
    product_dummies = pd.get_dummies(work["product_id"], drop_first=True, dtype=float).to_numpy()
    month_dummies = pd.get_dummies(work["month"], drop_first=True, dtype=float).to_numpy()
    X = np.column_stack([np.ones(len(work)), numeric, product_dummies, month_dummies])
    weights = np.sqrt(np.maximum(pd.to_numeric(work["review_count_month"], errors="coerce").fillna(1).to_numpy(), 1))
    Xw = X * weights[:, None]
    yw = y * weights
    beta = np.linalg.lstsq(Xw, yw, rcond=None)[0]
    residuals = yw - Xw @ beta
    rank = np.linalg.matrix_rank(Xw)
    dof = max(len(yw) - rank, 1)
    sigma2 = float((residuals @ residuals) / dof)
    cov = sigma2 * np.linalg.pinv(Xw.T @ Xw)
    se = np.sqrt(np.maximum(np.diag(cov), 0))
    predictor_index = 1
    t_stat = float(beta[predictor_index] / se[predictor_index]) if se[predictor_index] else float("nan")
    return {
        "outcome": outcome,
        "predictor": predictor,
        "n": int(len(work)),
        "product_fe": int(work["product_id"].nunique()),
        "month_fe": int(work["month"].nunique()),
        "beta": float(beta[predictor_index]),
        "se": float(se[predictor_index]),
        "t": t_stat,
        "p_normal_approx": normal_p_value(t_stat),
        "controls": ", ".join(controls),
        "status": "ok",
    }


def run_regressions(panel: pd.DataFrame) -> pd.DataFrame:
    df = panel.copy()
    df["month"] = pd.to_datetime(df["month"], errors="coerce").dt.to_period("M").astype(str)
    df = df.sort_values(["product_id", "month"])
    df["lag_semantic_gap"] = df.groupby("product_id")["semantic_gap_coarse"].shift(1)
    df["log_reviews"] = np.log1p(df["review_count_month"].fillna(0))
    controls = ["promo_density_total", "abstractness_ratio", "avg_rating_month", "log_reviews"]
    rows = []
    for outcome in ["trust_response_index", "trust_decline_index_theory", "lockin_index", "scenario_entropy"]:
        rows.append(ols_with_fe(df, outcome, "lag_semantic_gap", controls))
    return pd.DataFrame(rows)


def run_segmented_regressions(panel: pd.DataFrame) -> pd.DataFrame:
    df = panel.copy()
    df["month"] = pd.to_datetime(df["month"], errors="coerce").dt.to_period("M").astype(str)
    df = df.sort_values(["product_id", "month"])
    df["lag_semantic_gap"] = df.groupby("product_id")["semantic_gap_coarse"].shift(1)
    df["log_reviews"] = np.log1p(df["review_count_month"].fillna(0))
    controls = ["promo_density_total", "abstractness_ratio", "avg_rating_month", "log_reviews"]
    rows = []
    for segment_col in ["spf_group", "time_period", "brand_type", "natural_frequency_group"]:
        for segment_value, group in df.groupby(segment_col):
            for outcome in ["trust_response_index", "lockin_index"]:
                result = ols_with_fe(group, outcome, "lag_semantic_gap", controls)
                result["segment_type"] = segment_col
                result["segment"] = segment_value
                rows.append(result)
    return pd.DataFrame(rows)


def keyword_mentions_by_product(reviews: pd.DataFrame, keyword: str) -> pd.DataFrame:
    pattern = re.compile(re.escape(keyword).replace(r"\ ", r"\s+"), flags=re.IGNORECASE)
    df = reviews.copy()
    df[f"{keyword}_mention"] = df["review_text"].fillna("").str.contains(pattern)
    grouped = df.groupby("product_id")[f"{keyword}_mention"].agg(["sum", "count"]).reset_index()
    grouped[f"{keyword}_review_share"] = grouped["sum"] / grouped["count"].replace(0, np.nan)
    return grouped[["product_id", f"{keyword}_review_share"]]


def review_feature_summary(reviews: pd.DataFrame) -> pd.DataFrame:
    df = reviews.copy()
    rows = []
    for product_id, group in df.groupby("product_id"):
        texts = group["review_text"].fillna("").str.lower()
        row = {"product_id": product_id, "review_count": len(group)}
        for feature, terms in EXPERIENCE_KEYWORDS.items():
            pattern = re.compile("|".join(re.escape(term) for term in terms), flags=re.IGNORECASE)
            row[f"{feature}_review_share"] = float(texts.str.contains(pattern).mean())
        rows.append(row)
    return pd.DataFrame(rows)


def group_comparison(panel: pd.DataFrame, products: pd.DataFrame, review_features: pd.DataFrame) -> dict[str, pd.DataFrame]:
    product_panel = panel.groupby("product_id").agg(
        promo_density_total=("promo_density_total", "mean"),
        promo_density_natural_clean=("promo_density_natural_clean", "mean"),
        promo_density_sensorial=("promo_density_sensorial", "mean"),
        promo_density_efficacy=("promo_density_efficacy", "mean"),
        abstractness_ratio=("abstractness_ratio", "mean"),
        semantic_gap_coarse=("semantic_gap_coarse", "mean"),
        trust_response_index=("trust_response_index", "mean"),
        lockin_index=("lockin_index", "mean"),
        scenario_entropy=("scenario_entropy", "mean"),
        skepticism_ratio=("skepticism_ratio", "mean"),
        price=("price", "mean"),
    ).reset_index()
    product_panel = product_panel.merge(products[["product_id", "brand", "spf_value"]], on="product_id", how="left")
    product_panel = product_panel.merge(review_features, on="product_id", how="left")
    product_panel["spf_group"] = product_panel["spf_value"].map(spf_group)
    product_panel["brand_type"] = product_panel["brand"].map(brand_type)
    median_natural = product_panel["promo_density_natural_clean"].median()
    product_panel["natural_frequency_group"] = np.where(
        product_panel["promo_density_natural_clean"] >= median_natural,
        "high_natural_promo",
        "low_natural_promo",
    )
    outputs = {"product_deep_summary": product_panel}
    for group_col in ["spf_group", "brand_type", "natural_frequency_group"]:
        rows = []
        for group_name, group in product_panel.groupby(group_col):
            row = {"group": group_name, "product_count": len(group)}
            for metric in [
                "price",
                "promo_density_total",
                "promo_density_natural_clean",
                "promo_density_sensorial",
                "promo_density_efficacy",
                "abstractness_ratio",
                "semantic_gap_coarse",
                "trust_response_index",
                "lockin_index",
                "scenario_entropy",
                "skepticism_ratio",
                "white_cast_review_share",
                "greasy_texture_review_share",
                "burn_failure_review_share",
                "price_value_review_share",
            ]:
                if metric in group:
                    row[f"mean_{metric}"] = float(group[metric].mean())
            rows.append(row)
        outputs[f"{group_col}_comparison"] = pd.DataFrame(rows)
    return outputs


def time_period_summary(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for period, group in panel.groupby("time_period"):
        weights = group["review_count_month"]
        rows.append(
            {
                "time_period": period,
                "product_month_rows": len(group),
                "review_count": int(weights.sum()),
                "skepticism_ratio_weighted": weighted_mean(group["skepticism_ratio"], weights),
                "trust_response_index_weighted": weighted_mean(group["trust_response_index"], weights),
                "lockin_index_weighted": weighted_mean(group["lockin_index"], weights),
                "scenario_entropy_weighted": weighted_mean(group["scenario_entropy"], weights),
                "semantic_gap_weighted": weighted_mean(group["semantic_gap_coarse"], weights),
            }
        )
    return pd.DataFrame(rows).sort_values("time_period")


def promo_relay_counts(reviews: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = reviews.copy()
    df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")
    df["year"] = df["review_date"].dt.year
    relay_pattern = re.compile("|".join(PROMO_RELAY_PATTERNS), flags=re.IGNORECASE)
    rows = []
    yearly_rows = []
    for keyword in PROMO_RELAY_KEYWORDS:
        keyword_pattern = re.compile(re.escape(keyword).replace(r"\ ", r"\s+"), flags=re.IGNORECASE)
        has_keyword = df["review_text"].fillna("").str.contains(keyword_pattern)
        has_relay = df["review_text"].fillna("").str.contains(relay_pattern)
        subset = df[has_keyword & has_relay]
        rows.append(
            {
                "keyword": keyword,
                "relay_review_count": int(len(subset)),
                "product_count": int(subset["product_id"].nunique()),
                "first_year": int(subset["year"].min()) if not subset.empty else "",
                "last_year": int(subset["year"].max()) if not subset.empty else "",
                "mean_rating": float(subset["rating"].mean()) if not subset.empty else float("nan"),
            }
        )
        yearly = subset.groupby("year").size().reset_index(name="relay_review_count")
        yearly["keyword"] = keyword
        yearly_rows.extend(yearly.to_dict("records"))
    return pd.DataFrame(rows).sort_values("relay_review_count", ascending=False), pd.DataFrame(yearly_rows)


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    display = df.copy()
    for column in display.columns:
        if pd.api.types.is_float_dtype(display[column]):
            display[column] = display[column].map(lambda value: "" if pd.isna(value) else f"{value:.6g}")
        else:
            display[column] = display[column].map(lambda value: "" if pd.isna(value) else str(value))
    header = "| " + " | ".join(display.columns) + " |"
    divider = "| " + " | ".join(["---"] * len(display.columns)) + " |"
    rows = []
    for _, row in display.iterrows():
        rows.append("| " + " | ".join(str(row[column]).replace("|", "/") for column in display.columns) + " |")
    return "\n".join([header, divider] + rows)


def write_report(
    path: Path,
    regressions: pd.DataFrame,
    segmented: pd.DataFrame,
    time_summary: pd.DataFrame,
    group_tables: dict[str, pd.DataFrame],
    relay_summary: pd.DataFrame,
) -> None:
    core = regressions[["outcome", "beta", "se", "t", "p_normal_approx", "n", "status"]]
    spf = group_tables["spf_group_comparison"]
    natural = group_tables["natural_frequency_group_comparison"]
    brand = group_tables["brand_type_comparison"]
    lines = [
        "# Phase 1 Deep-Dive Report",
        "",
        "## Rebuilt Attenuation Measures",
        "",
        "- `trust_response_index` = 0.55 * skepticism + 0.30 * value complaint + 0.15 * rating decline.",
        "- `trust_decline_index_theory` = 0.40 * skepticism + 0.25 * value complaint + 0.20 * semantic gap + 0.15 * rating decline.",
        "- `lockin_index` = 1 - scenario entropy.",
        "",
        "The response-only trust index is the preferred dependent variable for lagged semantic-gap models because it does not mechanically include semantic gap.",
        "",
        "## Lagged Semantic Gap Models",
        "",
        md_table(core),
        "",
        "## Time-Period Summary",
        "",
        md_table(time_summary),
        "",
        "## SPF Group Deep Comparison",
        "",
        md_table(spf),
        "",
        "## Brand-Type Comparison",
        "",
        md_table(brand),
        "",
        "## Natural-Promo Frequency Comparison",
        "",
        md_table(natural),
        "",
        "## Segmented Lagged Semantic-Gap Models",
        "",
        md_table(segmented[["segment_type", "segment", "outcome", "beta", "se", "t", "p_normal_approx", "n", "status"]]),
        "",
        "## Quasi-Historical Promo Relay Counts",
        "",
        "These counts capture reviews that both mention a target keyword and use language such as `it says`, `claimed`, `advertised`, or `bought because`.",
        "",
        md_table(relay_summary),
        "",
        "## Reading Notes",
        "",
        "- The split-index design confirms whether semantic gap relates more to trust erosion or use-case lock-in.",
        "- Promo-relay counts are exploratory proxies, not historical page snapshots.",
        "- Group comparisons are descriptive and should guide follow-up hand annotation rather than stand alone as causal evidence.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    panel = pd.read_csv(args.panel)
    products = pd.read_csv(args.products)
    reviews = pd.read_csv(args.reviews)

    panel = add_indices(panel)
    products["spf_group"] = products["spf_value"].map(spf_group)
    products["brand_type"] = products["brand"].map(brand_type)
    panel = panel.merge(products[["product_id", "spf_group", "brand_type"]], on="product_id", how="left")
    panel["time_period"] = panel["month"].map(time_period)
    natural_by_product = panel.groupby("product_id")["promo_density_natural_clean"].mean()
    natural_median = natural_by_product.median()
    panel["natural_frequency_group"] = panel["product_id"].map(
        lambda product_id: "high_natural_promo"
        if natural_by_product.get(product_id, 0) >= natural_median
        else "low_natural_promo"
    )

    panel.to_csv(out_dir / "product_month_panel_with_split_indices.csv", index=False)
    regressions = run_regressions(panel)
    regressions.to_csv(out_dir / "split_index_fixed_effect_models.csv", index=False)
    segmented = run_segmented_regressions(panel)
    segmented.to_csv(out_dir / "segmented_fixed_effect_models.csv", index=False)
    time_summary = time_period_summary(panel)
    time_summary.to_csv(out_dir / "time_period_summary.csv", index=False)

    review_features = review_feature_summary(reviews)
    group_tables = group_comparison(panel, products, review_features)
    for name, table in group_tables.items():
        table.to_csv(out_dir / f"{name}.csv", index=False)

    relay_summary, relay_yearly = promo_relay_counts(reviews)
    relay_summary.to_csv(out_dir / "promo_relay_keyword_summary.csv", index=False)
    relay_yearly.to_csv(out_dir / "promo_relay_keyword_yearly.csv", index=False)

    write_report(
        out_dir / "phase1_deep_dive_report.md",
        regressions,
        segmented,
        time_summary,
        group_tables,
        relay_summary,
    )
    print(f"wrote deep-dive outputs to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
