#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd


KEYWORDS = [
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
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 1 descriptive, regression, keyword, and contrast analyses.")
    parser.add_argument("--panel", type=Path, default=Path("outputs/product_month_panel.csv"))
    parser.add_argument("--products", type=Path, default=Path("data/raw/products.csv"))
    parser.add_argument("--reviews", type=Path, default=Path("data/raw/reviews.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("reports/phase1/analysis"))
    return parser.parse_args()


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    clean = pd.DataFrame({"value": values, "weight": weights}).dropna()
    clean = clean[clean["weight"] > 0]
    if clean.empty:
        return float("nan")
    return float(np.average(clean["value"], weights=clean["weight"]))


def normal_p_value(t_stat: float) -> float:
    return float(math.erfc(abs(t_stat) / math.sqrt(2)))


def ols_slope(y: np.ndarray, x: np.ndarray) -> dict[str, float]:
    mask = np.isfinite(y) & np.isfinite(x)
    y = y[mask]
    x = x[mask]
    if len(y) < 3 or np.std(x) == 0:
        return {"slope": float("nan"), "se": float("nan"), "t": float("nan"), "p": float("nan"), "n": len(y)}
    X = np.column_stack([np.ones(len(x)), x])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    residuals = y - X @ beta
    dof = max(len(y) - X.shape[1], 1)
    sigma2 = float((residuals @ residuals) / dof)
    cov = sigma2 * np.linalg.pinv(X.T @ X)
    se = math.sqrt(max(float(cov[1, 1]), 0.0))
    t_stat = float(beta[1] / se) if se else float("nan")
    return {"slope": float(beta[1]), "se": se, "t": t_stat, "p": normal_p_value(t_stat), "n": len(y)}


def svg_line_chart(
    rows: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    path: Path,
    width: int = 920,
    height: int = 420,
) -> None:
    rows = rows[[x_col, y_col]].dropna().sort_values(x_col)
    margin_left, margin_right, margin_top, margin_bottom = 70, 25, 45, 55
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    y_min = min(0.0, float(rows[y_col].min()) if not rows.empty else 0.0)
    y_max = float(rows[y_col].max()) if not rows.empty else 1.0
    if y_max == y_min:
        y_max = y_min + 1
    xs = list(range(len(rows)))

    def sx(index: int) -> float:
        return margin_left + (index / max(len(xs) - 1, 1)) * plot_w

    def sy(value: float) -> float:
        return margin_top + (1 - ((value - y_min) / (y_max - y_min))) * plot_h

    points = " ".join(f"{sx(index):.1f},{sy(float(value)):.1f}" for index, value in enumerate(rows[y_col]))
    y_ticks = [y_min + (y_max - y_min) * i / 4 for i in range(5)]
    x_labels = []
    if not rows.empty:
        for index in np.linspace(0, len(rows) - 1, num=min(6, len(rows)), dtype=int):
            x_labels.append((sx(int(index)), str(rows.iloc[int(index)][x_col])[:10]))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{margin_left}" y="28" font-family="Arial" font-size="20" font-weight="700">{html.escape(title)}</text>',
        f'<line x1="{margin_left}" y1="{margin_top + plot_h}" x2="{margin_left + plot_w}" y2="{margin_top + plot_h}" stroke="#333"/>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_h}" stroke="#333"/>',
    ]
    for tick in y_ticks:
        y = sy(tick)
        parts.append(f'<line x1="{margin_left-5}" y1="{y:.1f}" x2="{margin_left + plot_w}" y2="{y:.1f}" stroke="#e6e6e6"/>')
        parts.append(f'<text x="{margin_left-10}" y="{y+4:.1f}" text-anchor="end" font-family="Arial" font-size="11">{tick:.3f}</text>')
    for x, label in x_labels:
        parts.append(f'<text x="{x:.1f}" y="{height-22}" text-anchor="middle" font-family="Arial" font-size="11">{html.escape(label)}</text>')
    if points:
        parts.append(f'<polyline fill="none" stroke="#2b6cb0" stroke-width="2.5" points="{points}"/>')
    parts.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts), encoding="utf-8")


def weighted_monthly_trends(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for month, group in panel.groupby("month"):
        weight = group["review_count_month"].fillna(0)
        rows.append(
            {
                "month": month,
                "review_count_month": int(weight.sum()),
                "skepticism_ratio_weighted": weighted_mean(group["skepticism_ratio"], weight),
                "scenario_entropy_weighted": weighted_mean(group["scenario_entropy"], weight),
                "semantic_gap_weighted": weighted_mean(group["semantic_gap_coarse"], weight),
            }
        )
    return pd.DataFrame(rows).sort_values("month")


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


def spf_comparison(panel: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    merged = panel.merge(products[["product_id", "spf_value"]], on="product_id", how="left")
    merged["spf_group"] = merged["spf_value"].map(spf_group)
    rows = []
    for group_name, group in merged.groupby("spf_group"):
        rows.append(
            {
                "spf_group": group_name,
                "product_count": group["product_id"].nunique(),
                "product_month_rows": len(group),
                "review_count": int(group["review_count_month"].sum()),
                "skepticism_ratio_weighted": weighted_mean(group["skepticism_ratio"], group["review_count_month"]),
                "scenario_entropy_weighted": weighted_mean(group["scenario_entropy"], group["review_count_month"]),
                "semantic_gap_weighted": weighted_mean(group["semantic_gap_coarse"], group["review_count_month"]),
            }
        )
    return pd.DataFrame(rows).sort_values("spf_group")


def fixed_effect_regression(panel: pd.DataFrame, outcome: str) -> dict[str, float]:
    df = panel.copy()
    df["month"] = pd.to_datetime(df["month"], errors="coerce").dt.to_period("M").astype(str)
    df = df.sort_values(["product_id", "month"])
    df["lag_semantic_gap"] = df.groupby("product_id")["semantic_gap_coarse"].shift(1)
    df["log_reviews"] = np.log1p(pd.to_numeric(df["review_count_month"], errors="coerce").fillna(0))
    controls = ["lag_semantic_gap", "promo_density_total", "abstractness_ratio", "avg_rating_month", "log_reviews"]
    cols = [outcome, "product_id", "month"] + controls
    df = df[cols].replace([np.inf, -np.inf], np.nan).dropna()
    if len(df) < 20:
        return {"outcome": outcome, "n": len(df)}

    y = df[outcome].to_numpy(dtype=float)
    numeric_x = df[controls].to_numpy(dtype=float)
    product_dummies = pd.get_dummies(df["product_id"], drop_first=True, dtype=float).to_numpy()
    month_dummies = pd.get_dummies(df["month"], drop_first=True, dtype=float).to_numpy()
    X = np.column_stack([np.ones(len(df)), numeric_x, product_dummies, month_dummies])
    weights = np.sqrt(np.maximum(pd.to_numeric(panel.loc[df.index, "review_count_month"], errors="coerce").fillna(1).to_numpy(), 1))
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
        "n": int(len(df)),
        "product_fe": int(df["product_id"].nunique()),
        "month_fe": int(df["month"].nunique()),
        "beta_lag_semantic_gap": float(beta[predictor_index]),
        "se_lag_semantic_gap": float(se[predictor_index]),
        "t_lag_semantic_gap": t_stat,
        "p_lag_semantic_gap_normal_approx": normal_p_value(t_stat),
        "controls": ", ".join(controls[1:]),
        "weighted_by_review_count": True,
    }


def keyword_drift(reviews: pd.DataFrame, keywords: list[str]) -> pd.DataFrame:
    df = reviews.copy()
    df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")
    df = df.dropna(subset=["review_date"])
    df["month"] = df["review_date"].dt.to_period("M").dt.to_timestamp()
    df["month_index"] = (df["month"] - df["month"].min()).dt.days / 30.44
    rows = []
    for keyword in keywords:
        pattern = re.compile(re.escape(keyword).replace(r"\ ", r"\s+"), flags=re.IGNORECASE)
        subset = df[df["review_text"].fillna("").str.contains(pattern, na=False)]
        monthly = subset.groupby("month_index")["rating"].mean().reset_index()
        stats = ols_slope(monthly["rating"].to_numpy(dtype=float), monthly["month_index"].to_numpy(dtype=float))
        rows.append(
            {
                "keyword": keyword,
                "review_mentions": int(len(subset)),
                "month_count": int(len(monthly)),
                "rating_slope_per_month": stats["slope"],
                "slope_se": stats["se"],
                "t_stat": stats["t"],
                "p_value_normal_approx": stats["p"],
                "interpretation": "negative_drift" if pd.notna(stats["slope"]) and stats["slope"] < 0 else "non_negative_or_insufficient",
            }
        )
    return pd.DataFrame(rows).sort_values(["rating_slope_per_month", "review_mentions"], ascending=[True, False])


def high_low_attenuation_contrast(product_summary: pd.DataFrame) -> pd.DataFrame:
    q75 = product_summary["attenuation_index_exploratory"].quantile(0.75)
    q25 = product_summary["attenuation_index_exploratory"].quantile(0.25)
    high = product_summary[product_summary["attenuation_index_exploratory"] >= q75]
    low = product_summary[product_summary["attenuation_index_exploratory"] <= q25]
    rows = []
    for label, group in [("high_attenuation_top_quartile", high), ("low_attenuation_bottom_quartile", low)]:
        row = {"group": label, "product_count": len(group)}
        for metric in [
            "promo_density_total",
            "promo_density_natural_clean",
            "abstractness_ratio",
            "semantic_gap_coarse",
            "skepticism_ratio",
            "scenario_entropy",
            "attenuation_index_exploratory",
        ]:
            row[f"mean_{metric}"] = float(group[metric].mean()) if not group.empty else float("nan")
        rows.append(row)
    return pd.DataFrame(rows)


def write_markdown_report(
    out_path: Path,
    monthly: pd.DataFrame,
    spf: pd.DataFrame,
    regressions: pd.DataFrame,
    keywords: pd.DataFrame,
    contrast: pd.DataFrame,
) -> None:
    skepticism_slope = ols_slope(
        monthly["skepticism_ratio_weighted"].to_numpy(dtype=float),
        np.arange(len(monthly), dtype=float),
    )
    entropy_slope = ols_slope(
        monthly["scenario_entropy_weighted"].to_numpy(dtype=float),
        np.arange(len(monthly), dtype=float),
    )
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

    lines = [
        "# Phase 1 Analysis Report",
        "",
        "## Descriptive Trends",
        "",
        f"- Weighted monthly skepticism slope: {skepticism_slope['slope']:.6f} per observed month window (normal-approx p={skepticism_slope['p']:.4f}).",
        f"- Weighted monthly scenario entropy slope: {entropy_slope['slope']:.6f} per observed month window (normal-approx p={entropy_slope['p']:.4f}).",
        "- Trend charts are saved as SVG files in `reports/phase1/analysis/figures/`.",
        "",
        "## SPF Group Comparison",
        "",
        md_table(spf),
        "",
        "## Fixed-Effects Panel Models",
        "",
        "Model form: outcome_it ~ product fixed effects + month fixed effects + lagged semantic_gap_it + controls.",
        "",
        md_table(regressions),
        "",
        "## Keyword Sentiment Drift",
        "",
        "Sentiment is proxied by star rating among reviews mentioning each keyword, aggregated by month.",
        "",
        md_table(keywords),
        "",
        "## High vs Low Attenuation Product Contrast",
        "",
        md_table(contrast),
        "",
        "## Cautions",
        "",
        "- This Phase 1 run uses static product metadata repeated across review months; it is a feasibility model, not direct evidence of historical copy changes.",
        "- Star rating is a rough sentiment proxy for keyword drift.",
        "- Product-page metadata and reviews come from a public research dataset and may not represent live Amazon pages.",
        "- The exploratory attenuation index still requires human annotation validation.",
        "",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir
    fig_dir = out_dir / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    panel = pd.read_csv(args.panel)
    products = pd.read_csv(args.products)
    reviews = pd.read_csv(args.reviews)
    panel["month"] = pd.to_datetime(panel["month"], errors="coerce")
    panel = panel.dropna(subset=["month"])
    panel["month"] = panel["month"].dt.to_period("M").dt.to_timestamp().dt.date.astype(str)

    monthly = weighted_monthly_trends(panel)
    monthly.to_csv(out_dir / "monthly_trends.csv", index=False)
    svg_line_chart(monthly, "month", "skepticism_ratio_weighted", "Weighted Monthly Skepticism Ratio", fig_dir / "skepticism_ratio_trend.svg")
    svg_line_chart(monthly, "month", "scenario_entropy_weighted", "Weighted Monthly Scenario Entropy", fig_dir / "scenario_entropy_trend.svg")

    spf = spf_comparison(panel, products)
    spf.to_csv(out_dir / "spf_group_comparison.csv", index=False)

    regressions = pd.DataFrame(
        [
            fixed_effect_regression(panel, "skepticism_ratio"),
            fixed_effect_regression(panel, "scenario_entropy"),
        ]
    )
    regressions.to_csv(out_dir / "fixed_effect_models.csv", index=False)

    keywords = keyword_drift(reviews, KEYWORDS)
    keywords.to_csv(out_dir / "keyword_sentiment_drift.csv", index=False)

    product_summary = pd.read_csv("reports/phase1/product_metric_summary.csv")
    contrast = high_low_attenuation_contrast(product_summary)
    contrast.to_csv(out_dir / "attenuation_group_contrast.csv", index=False)

    write_markdown_report(out_dir / "phase1_analysis_report.md", monthly, spf, regressions, keywords, contrast)
    print(f"wrote analysis outputs to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
