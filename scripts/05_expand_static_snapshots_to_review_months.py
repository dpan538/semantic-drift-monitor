#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repeat static metadata snapshots across observed review months.")
    parser.add_argument("--snapshots", type=Path, default=Path("data/raw/snapshots.csv"))
    parser.add_argument("--reviews", type=Path, default=Path("data/raw/reviews.csv"))
    parser.add_argument("--out", type=Path, default=Path("data/raw/snapshots.csv"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    snapshots = pd.read_csv(args.snapshots)
    reviews = pd.read_csv(args.reviews)

    reviews["review_date"] = pd.to_datetime(reviews["review_date"], errors="coerce")
    reviews = reviews.dropna(subset=["review_date"])
    reviews["snapshot_date"] = reviews["review_date"].dt.to_period("M").dt.to_timestamp().dt.date.astype(str)
    product_months = reviews[["product_id", "snapshot_date"]].drop_duplicates()

    base_snapshots = snapshots.sort_values("snapshot_date").groupby("product_id").tail(1)
    expanded = product_months.merge(
        base_snapshots.drop(columns=["snapshot_date"], errors="ignore"),
        on="product_id",
        how="left",
    )
    if "source_method" in expanded.columns:
        expanded["source_method"] = expanded["source_method"].fillna("") + ";static_metadata_repeated"
    else:
        expanded["source_method"] = "static_metadata_repeated"

    expanded = expanded.sort_values(["product_id", "snapshot_date"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    expanded.to_csv(args.out, index=False)
    print(f"wrote {len(expanded)} expanded snapshot rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

