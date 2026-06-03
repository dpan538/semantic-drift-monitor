import pandas as pd

from config import (
    CONCRETENESS_LEXICON_PATH,
    PROMO_LEXICON_PATH,
    SCENARIO_LEXICON_PATH,
    SKEPTICISM_LEXICON_PATH,
    VALUE_LEXICON_PATH,
)
from semantic_drift_monitor.metrics.attenuation import exploratory_attenuation_index
from semantic_drift_monitor.metrics.gap import semantic_gap
from semantic_drift_monitor.metrics.lockin import scenario_entropy
from semantic_drift_monitor.metrics.overload import promo_density, promo_density_by_category
from semantic_drift_monitor.metrics.skepticism import flagged_sentence_ratio
from semantic_drift_monitor.text_processing.abstractness import abstractness_ratio
from semantic_drift_monitor.text_processing.cleaner import normalize_text
from semantic_drift_monitor.text_processing.keyword_dicts import load_yaml_lexicon

NEGATIVE_REPURCHASE_LEXICON = {
    "negative_repurchase": [
        "will not buy again",
        "won't buy again",
        "would not repurchase",
        "not repurchase",
        "not buying again",
        "never again",
    ]
}


def _prepare_inputs(
    products_df: pd.DataFrame,
    snapshots_df: pd.DataFrame,
    reviews_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    products = products_df.copy()
    snapshots = snapshots_df.copy()
    reviews = reviews_df.copy()

    snapshots["snapshot_date"] = pd.to_datetime(snapshots["snapshot_date"], errors="coerce")
    reviews["review_date"] = pd.to_datetime(reviews["review_date"], errors="coerce")
    snapshots["month"] = snapshots["snapshot_date"].dt.to_period("M").dt.to_timestamp()
    reviews["month"] = reviews["review_date"].dt.to_period("M").dt.to_timestamp()

    def text_column(frame: pd.DataFrame, column: str) -> pd.Series:
        if column in frame.columns:
            return frame[column].fillna("").astype(str)
        return pd.Series([""] * len(frame), index=frame.index)

    snapshots["promo_text"] = (
        text_column(snapshots, "title")
        + " "
        + text_column(snapshots, "description")
        + " "
        + text_column(snapshots, "bullet_points")
        + " "
        + text_column(snapshots, "image_ocr_text")
    ).map(normalize_text)
    reviews["review_text_clean"] = reviews["review_text"].map(normalize_text)
    return products, snapshots, reviews


def build_product_month_panel(
    products_df: pd.DataFrame,
    snapshots_df: pd.DataFrame,
    reviews_df: pd.DataFrame,
) -> pd.DataFrame:
    promo_lexicon = load_yaml_lexicon(PROMO_LEXICON_PATH)
    skepticism_lexicon = load_yaml_lexicon(SKEPTICISM_LEXICON_PATH)
    value_lexicon = load_yaml_lexicon(VALUE_LEXICON_PATH)
    scenario_lexicon = load_yaml_lexicon(SCENARIO_LEXICON_PATH)
    concreteness_lexicon = load_yaml_lexicon(CONCRETENESS_LEXICON_PATH)

    products, snapshots, reviews = _prepare_inputs(products_df, snapshots_df, reviews_df)

    rows: list[dict] = []
    product_ids = sorted(set(products["product_id"]) | set(snapshots["product_id"]) | set(reviews["product_id"]))
    for product_id in product_ids:
        product_snapshots = snapshots[snapshots["product_id"] == product_id]
        product_reviews = reviews[reviews["product_id"] == product_id]
        months = sorted(set(product_snapshots["month"].dropna()) | set(product_reviews["month"].dropna()))

        for month in months:
            snapshot_month = product_snapshots[product_snapshots["month"] == month]
            review_month = product_reviews[product_reviews["month"] == month]
            promo_texts = snapshot_month["promo_text"].dropna().tolist()
            review_texts = review_month["review_text_clean"].dropna().tolist()
            promo_text = " ".join(promo_texts)

            densities = promo_density_by_category(promo_text, promo_lexicon)
            entropy = scenario_entropy(review_texts, scenario_lexicon)
            skepticism = flagged_sentence_ratio(review_texts, skepticism_lexicon)
            value_complaint = flagged_sentence_ratio(review_texts, value_lexicon)
            negative_repurchase = flagged_sentence_ratio(review_texts, NEGATIVE_REPURCHASE_LEXICON)

            row = {
                "product_id": product_id,
                "month": month.date().isoformat(),
                "review_count_month": int(len(review_month)),
                "avg_rating_month": float(review_month["rating"].mean()) if not review_month.empty else None,
                "promo_density_total": promo_density(promo_text, promo_lexicon),
                "promo_density_natural_clean": densities.get("natural_clean", 0.0),
                "promo_density_clinical_premium": densities.get("clinical_premium", 0.0),
                "promo_density_sensorial": densities.get("sensorial", 0.0),
                "promo_density_efficacy": densities.get("efficacy", 0.0),
                "abstractness_ratio": abstractness_ratio(promo_text, concreteness_lexicon),
                "semantic_gap_coarse": semantic_gap(promo_texts, review_texts),
                "skepticism_ratio": skepticism,
                "value_complaint_ratio": value_complaint,
                "negative_repurchase_ratio": negative_repurchase,
                "scenario_entropy": entropy,
                "lockin_risk": 1 - entropy,
                "price": float(snapshot_month["price"].iloc[-1]) if "price" in snapshot_month and not snapshot_month.empty else None,
            }
            row["attenuation_index_exploratory"] = exploratory_attenuation_index(
                row["skepticism_ratio"],
                row["value_complaint_ratio"],
                row["negative_repurchase_ratio"],
                row["scenario_entropy"],
            )
            rows.append(row)

    panel = pd.DataFrame(rows)
    if not panel.empty:
        panel = panel.sort_values(["product_id", "month"]).reset_index(drop=True)
    return panel
