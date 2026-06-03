import logging

import pandas as pd

from config import MIN_REVIEWS_PER_PRODUCT, TIME_WINDOW_MONTHS

logger = logging.getLogger(__name__)


def check_data_availability(products_df: pd.DataFrame, reviews_df: pd.DataFrame) -> bool:
    if products_df.empty:
        logger.error("No products were provided.")
        return False
    if reviews_df.empty:
        logger.error("No reviews were provided.")
        return False

    counts = reviews_df.groupby("product_id").size()
    low_count = counts[counts < MIN_REVIEWS_PER_PRODUCT]
    if not low_count.empty:
        logger.warning(
            "%s products have fewer than %s reviews.",
            len(low_count),
            MIN_REVIEWS_PER_PRODUCT,
        )
    return True


def check_temporal_coverage(reviews_df: pd.DataFrame) -> bool:
    dates = pd.to_datetime(reviews_df["review_date"], errors="coerce").dropna()
    if dates.empty:
        logger.error("No valid review dates were found.")
        return False
    months = (dates.max() - dates.min()).days / 30.44
    if months < TIME_WINDOW_MONTHS * 0.5:
        logger.warning("Temporal window is short: %.1f months.", months)
        return False
    return True


def check_required_columns(df: pd.DataFrame, required: list[str], table_name: str) -> bool:
    missing = [column for column in required if column not in df.columns]
    if missing:
        logger.error("%s is missing required columns: %s", table_name, ", ".join(missing))
        return False
    return True

