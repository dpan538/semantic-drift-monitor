#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from constraints import check_data_availability, check_required_columns, check_temporal_coverage


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Phase 1 local input CSVs.")
    parser.add_argument("--products", type=Path, default=Path("data/raw/products.csv"))
    parser.add_argument("--snapshots", type=Path, default=Path("data/raw/snapshots.csv"))
    parser.add_argument("--reviews", type=Path, default=Path("data/raw/reviews.csv"))
    parser.add_argument("--strict", action="store_true", help="Fail on minimum review-count or temporal-coverage warnings.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    for path in [args.products, args.snapshots, args.reviews]:
        if not path.exists():
            print(f"[FAIL] Missing file: {path}")
            return 1

    products = pd.read_csv(args.products)
    snapshots = pd.read_csv(args.snapshots)
    reviews = pd.read_csv(args.reviews)

    structural_checks = [
        check_required_columns(products, ["product_id", "brand", "product_name", "category"], "products"),
        check_required_columns(snapshots, ["product_id", "snapshot_date", "title", "description"], "snapshots"),
        check_required_columns(reviews, ["review_id", "product_id", "review_date", "rating", "review_text"], "reviews"),
    ]
    health_checks = [
        check_data_availability(products, reviews),
        check_temporal_coverage(reviews),
    ]

    print(f"products: {len(products)} rows")
    print(f"snapshots: {len(snapshots)} rows")
    print(f"reviews: {len(reviews)} rows")
    print(f"review products: {reviews['product_id'].nunique() if 'product_id' in reviews else 0}")

    if not all(structural_checks):
        return 1
    if args.strict and not all(health_checks):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
