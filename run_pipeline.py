import argparse
import logging
from pathlib import Path

import pandas as pd

from config import EXAMPLE_DIR, LOG_DIR, OUTPUT_DIR
from constraints import check_data_availability, check_required_columns, check_temporal_coverage
from semantic_drift_monitor.detection.alert import log_alert
from semantic_drift_monitor.detection.drift_detector import DriftDetector
from semantic_drift_monitor.metrics.panel_builder import build_product_month_panel

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build semantic drift metrics for product reviews.")
    parser.add_argument("--demo", action="store_true", help="Run with bundled demo data.")
    parser.add_argument("--products", type=Path, help="Path to products CSV.")
    parser.add_argument("--snapshots", type=Path, help="Path to snapshots CSV.")
    parser.add_argument("--reviews", type=Path, help="Path to reviews CSV.")
    return parser.parse_args()


def load_inputs(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if args.demo:
        products_path = EXAMPLE_DIR / "demo_products.csv"
        snapshots_path = EXAMPLE_DIR / "demo_snapshots.csv"
        reviews_path = EXAMPLE_DIR / "demo_reviews.csv"
    else:
        if not (args.products and args.snapshots and args.reviews):
            raise SystemExit("Provide --products, --snapshots, and --reviews, or run with --demo.")
        products_path = args.products
        snapshots_path = args.snapshots
        reviews_path = args.reviews

    logger.info("Loading products from %s", products_path)
    products_df = pd.read_csv(products_path)
    snapshots_df = pd.read_csv(snapshots_path)
    reviews_df = pd.read_csv(reviews_path)
    return products_df, snapshots_df, reviews_df


def main() -> None:
    args = parse_args()
    products_df, snapshots_df, reviews_df = load_inputs(args)

    checks = [
        check_required_columns(products_df, ["product_id", "brand", "product_name", "category"], "products"),
        check_required_columns(snapshots_df, ["product_id", "snapshot_date", "title", "description"], "snapshots"),
        check_required_columns(reviews_df, ["review_id", "product_id", "review_date", "rating", "review_text"], "reviews"),
        check_data_availability(products_df, reviews_df),
        check_temporal_coverage(reviews_df),
    ]
    if not all(checks):
        logger.warning("Input checks raised warnings or errors; continuing only if critical columns exist.")

    panel = build_product_month_panel(products_df, snapshots_df, reviews_df)
    output_path = OUTPUT_DIR / "product_month_panel.csv"
    panel.to_csv(output_path, index=False)
    logger.info("Wrote product-month panel to %s", output_path)

    detector = DriftDetector(panel)
    alerts = detector.check_alerts()
    if alerts:
        log_alert(alerts, LOG_DIR / "alerts.log")
        logger.info("Wrote %s alert(s) to %s", len(alerts), LOG_DIR / "alerts.log")
    else:
        logger.info("No drift alerts triggered.")


if __name__ == "__main__":
    main()

