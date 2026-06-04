#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_QUERY_TERMS = [
    "sunscreen",
    "sun screen",
    "sunblock",
    "spf",
    "broad spectrum",
    "uva",
    "uvb",
    "zinc oxide",
    "titanium dioxide",
    "reef safe",
]

CHEMICAL_FILTER_TERMS = [
    "avobenzone",
    "octinoxate",
    "octisalate",
    "octocrylene",
    "homosalate",
    "oxybenzone",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sample sunscreen/SPF products from local Amazon Reviews 2023 JSONL files."
    )
    parser.add_argument("--metadata-jsonl", type=Path, required=True, help="Local metadata JSONL or JSONL.GZ file.")
    parser.add_argument("--reviews-jsonl", type=Path, required=True, help="Local reviews JSONL or JSONL.GZ file.")
    parser.add_argument("--target-products", type=int, default=100)
    parser.add_argument("--min-reviews", type=int, default=20)
    parser.add_argument("--min-review-months", type=float, default=12.0)
    parser.add_argument("--max-reviews-per-product", type=int, default=500)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "data/raw")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports/phase1")
    parser.add_argument("--source-id", default="mcaulay_amazon_reviews_2023_beauty")
    parser.add_argument("--dataset-url", default="https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023")
    parser.add_argument("--snapshot-date", default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument("--query-term", action="append", dest="query_terms", help="Additional sunscreen/SPF query term.")
    return parser.parse_args()


def open_text(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return path.open("r", encoding="utf-8", errors="replace")


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with open_text(path) as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at {path}:{line_number}: {exc}") from exc
            if isinstance(row, dict):
                yield row


def flatten_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(flatten_value(item) for item in value)
    if isinstance(value, dict):
        return " ".join(f"{key} {flatten_value(item)}" for key, item in value.items())
    return str(value)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def field(row: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in row and row[name] not in (None, ""):
            return row[name]
    return ""


def metadata_text(row: dict[str, Any]) -> str:
    parts = [
        field(row, "title"),
        field(row, "description"),
        field(row, "features"),
        field(row, "categories"),
        field(row, "main_category"),
        field(row, "details"),
        field(row, "store", "brand"),
    ]
    return normalize(" ".join(flatten_value(part) for part in parts))


def contains_query(text: str, query_terms: list[str]) -> bool:
    return any(term.lower() in text for term in query_terms)


def extract_spf(text: str) -> str:
    match = re.search(r"\bspf\s*[-:]?\s*(\d{2,3})\b", text, flags=re.IGNORECASE)
    return match.group(1) if match else ""


def classify_filter_type(text: str) -> str:
    has_mineral = "zinc oxide" in text or "titanium dioxide" in text or "mineral" in text
    has_chemical = any(term in text for term in CHEMICAL_FILTER_TERMS)
    if has_mineral and has_chemical:
        return "mixed"
    if has_mineral:
        return "mineral"
    if has_chemical:
        return "chemical"
    return ""


def timestamp_to_date(value: Any) -> str:
    if value in (None, ""):
        return ""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        text = str(value)
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).date().isoformat()
        except ValueError:
            return ""
    if numeric > 10_000_000_000:
        numeric = numeric / 1000
    return datetime.fromtimestamp(numeric, tz=timezone.utc).date().isoformat()


def months_between(first_date: str, last_date: str) -> float:
    if not first_date or not last_date:
        return 0.0
    first = datetime.fromisoformat(first_date)
    last = datetime.fromisoformat(last_date)
    return max((last - first).days / 30.44, 0.0)


def collect_candidates(metadata_path: Path, query_terms: list[str]) -> dict[str, dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}
    for row in iter_jsonl(metadata_path):
        product_id = str(field(row, "parent_asin", "asin")).strip()
        if not product_id:
            continue
        text = metadata_text(row)
        if not contains_query(text, query_terms):
            continue
        title = flatten_value(field(row, "title")).strip()
        if not title:
            continue
        candidates[product_id] = {
            "raw": row,
            "product_id": product_id,
            "title": title,
            "text": text,
            "matched_terms": [term for term in query_terms if term.lower() in text],
        }
    return candidates


def collect_review_stats(
    reviews_path: Path,
    candidates: dict[str, dict[str, Any]],
    max_reviews_per_product: int,
) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    stats = {
        product_id: {
            "review_count": 0,
            "first_review_date": "",
            "last_review_date": "",
            "rating_sum": 0.0,
            "verified_count": 0,
        }
        for product_id in candidates
    }
    reviews_by_product: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in iter_jsonl(reviews_path):
        product_id = str(field(row, "parent_asin", "asin")).strip()
        if product_id not in candidates:
            continue
        review_text = flatten_value(field(row, "text", "reviewText")).strip()
        if not review_text:
            continue
        review_date = timestamp_to_date(field(row, "timestamp", "unixReviewTime", "review_date"))
        if not review_date:
            continue

        rating = field(row, "rating", "overall")
        try:
            rating_float = float(rating)
        except (TypeError, ValueError):
            rating_float = 0.0

        product_stats = stats[product_id]
        product_stats["review_count"] += 1
        product_stats["rating_sum"] += rating_float
        if bool(field(row, "verified_purchase", "verified")):
            product_stats["verified_count"] += 1
        if not product_stats["first_review_date"] or review_date < product_stats["first_review_date"]:
            product_stats["first_review_date"] = review_date
        if not product_stats["last_review_date"] or review_date > product_stats["last_review_date"]:
            product_stats["last_review_date"] = review_date

        if len(reviews_by_product[product_id]) < max_reviews_per_product:
            reviews_by_product[product_id].append(
                {
                    "review_id": flatten_value(field(row, "review_id", "reviewID", "reviewId"))
                    or f"{product_id}-{product_stats['review_count']}",
                    "product_id": product_id,
                    "review_date": review_date,
                    "rating": rating_float,
                    "verified_purchase": bool(field(row, "verified_purchase", "verified")),
                    "review_title": flatten_value(field(row, "title", "summary")),
                    "review_text": review_text,
                    "helpful_votes": flatten_value(field(row, "helpful_vote", "helpful")),
                    "source_method": "amazon_reviews_2023_public_research_dataset",
                }
            )

    return stats, reviews_by_product


def select_products(
    candidates: dict[str, dict[str, Any]],
    stats: dict[str, dict[str, Any]],
    target_products: int,
    min_reviews: int,
    min_review_months: float,
) -> list[str]:
    scored: list[tuple] = []
    brand_counts: Counter = Counter()
    for product_id, candidate in candidates.items():
        product_stats = stats.get(product_id, {})
        review_count = int(product_stats.get("review_count", 0))
        span_months = months_between(
            product_stats.get("first_review_date", ""),
            product_stats.get("last_review_date", ""),
        )
        if review_count < min_reviews or span_months < min_review_months:
            continue
        metadata_completeness = sum(
            bool(field(candidate["raw"], name))
            for name in ["title", "description", "features", "price", "average_rating", "rating_number"]
        )
        scored.append((-review_count, -metadata_completeness, product_id))

    selected: list[str] = []
    for _, _, product_id in sorted(scored):
        brand = flatten_value(field(candidates[product_id]["raw"], "brand", "store", "manufacturer")) or "unknown"
        if brand_counts[brand] >= max(5, target_products // 10):
            continue
        selected.append(product_id)
        brand_counts[brand] += 1
        if len(selected) >= target_products:
            break
    return selected


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_outputs(
    args: argparse.Namespace,
    candidates: dict[str, dict[str, Any]],
    stats: dict[str, dict[str, Any]],
    reviews_by_product: dict[str, list[dict[str, Any]]],
    selected: list[str],
) -> None:
    product_rows: list[dict[str, Any]] = []
    snapshot_rows: list[dict[str, Any]] = []
    review_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    for product_id in selected:
        candidate = candidates[product_id]
        row = candidate["raw"]
        text = candidate["text"]
        product_stats = stats[product_id]
        review_count = int(product_stats["review_count"])
        avg_rating = product_stats["rating_sum"] / review_count if review_count else ""
        brand = flatten_value(field(row, "brand", "store", "manufacturer"))
        title = flatten_value(field(row, "title"))
        description = flatten_value(field(row, "description"))
        features = flatten_value(field(row, "features"))
        price = flatten_value(field(row, "price"))

        product_rows.append(
            {
                "product_id": product_id,
                "platform": "amazon_reviews_2023",
                "asin_or_sku": product_id,
                "brand": brand,
                "product_name": title,
                "category": "skincare",
                "subcategory": "sunscreen_or_spf_skincare",
                "spf_value": extract_spf(text),
                "mineral_or_chemical": classify_filter_type(text),
                "size_ml_or_oz": flatten_value(field(row, "unit_count", "item_volume", "size")),
                "product_url": f"https://www.amazon.com/dp/{product_id}",
                "notes": "sampled from Amazon Reviews 2023 public research dataset",
            }
        )

        snapshot_rows.append(
            {
                "product_id": product_id,
                "snapshot_date": args.snapshot_date,
                "title": title,
                "description": description,
                "bullet_points": features,
                "image_ocr_text": "",
                "price": price,
                "rating_avg": flatten_value(field(row, "average_rating")) or avg_rating,
                "rating_count": flatten_value(field(row, "rating_number")) or review_count,
                "review_count": review_count,
                "source_url": args.dataset_url,
                "source_method": "amazon_reviews_2023_metadata_snapshot",
            }
        )

        review_rows.extend(reviews_by_product.get(product_id, []))
        summary_rows.append(
            {
                "product_id": product_id,
                "brand": brand,
                "review_count": review_count,
                "sampled_reviews": len(reviews_by_product.get(product_id, [])),
                "first_review_date": product_stats["first_review_date"],
                "last_review_date": product_stats["last_review_date"],
                "review_span_months": f"{months_between(product_stats['first_review_date'], product_stats['last_review_date']):.1f}",
                "matched_terms": "; ".join(candidate["matched_terms"]),
            }
        )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        args.out_dir / "products.csv",
        product_rows,
        [
            "product_id",
            "platform",
            "asin_or_sku",
            "brand",
            "product_name",
            "category",
            "subcategory",
            "spf_value",
            "mineral_or_chemical",
            "size_ml_or_oz",
            "product_url",
            "notes",
        ],
    )
    write_csv(
        args.out_dir / "snapshots.csv",
        snapshot_rows,
        [
            "product_id",
            "snapshot_date",
            "title",
            "description",
            "bullet_points",
            "image_ocr_text",
            "price",
            "rating_avg",
            "rating_count",
            "review_count",
            "source_url",
            "source_method",
        ],
    )
    write_csv(
        args.out_dir / "reviews.csv",
        review_rows,
        [
            "review_id",
            "product_id",
            "review_date",
            "rating",
            "verified_purchase",
            "review_title",
            "review_text",
            "helpful_votes",
            "source_method",
        ],
    )
    write_csv(
        args.out_dir / "source_registry.csv",
        [
            {
                "source_id": args.source_id,
                "platform": "amazon_reviews_2023",
                "source_type": "public_research_dataset",
                "access_method": "local_jsonl_import",
                "access_url": args.dataset_url,
                "robots_checked": "not_applicable_dataset_import",
                "tos_checked": "user_to_confirm_dataset_terms",
                "license_or_terms_notes": "public research dataset; verify redistribution limits before publishing derived text",
                "collection_allowed": "true_for_local_research_import",
                "collector": "Dai Pan",
                "collection_date": args.snapshot_date,
                "notes": "Generated by scripts/04_sample_amazon_reviews_2023.py",
            }
        ],
        [
            "source_id",
            "platform",
            "source_type",
            "access_method",
            "access_url",
            "robots_checked",
            "tos_checked",
            "license_or_terms_notes",
            "collection_allowed",
            "collector",
            "collection_date",
            "notes",
        ],
    )
    write_csv(
        args.out_dir / "collection_targets.csv",
        [
            {
                "product_id": product_id,
                "url": f"https://www.amazon.com/dp/{product_id}",
                "platform": "amazon_reviews_2023",
                "source_type": "metadata_reference_url",
                "collection_priority": index + 1,
                "notes": "reference only; do not fetch live page unless compliance is confirmed",
            }
            for index, product_id in enumerate(selected)
        ],
        ["product_id", "url", "platform", "source_type", "collection_priority", "notes"],
    )
    write_csv(
        args.report_dir / "source_selection_summary.csv",
        summary_rows,
        [
            "product_id",
            "brand",
            "review_count",
            "sampled_reviews",
            "first_review_date",
            "last_review_date",
            "review_span_months",
            "matched_terms",
        ],
    )


def main() -> int:
    args = parse_args()
    query_terms = DEFAULT_QUERY_TERMS + (args.query_terms or [])
    print(f"Scanning metadata: {args.metadata_jsonl}")
    candidates = collect_candidates(args.metadata_jsonl, query_terms)
    print(f"Metadata candidates: {len(candidates)}")
    if not candidates:
        raise SystemExit("No sunscreen/SPF metadata candidates found.")

    print(f"Scanning reviews: {args.reviews_jsonl}")
    stats, reviews_by_product = collect_review_stats(
        args.reviews_jsonl,
        candidates,
        args.max_reviews_per_product,
    )
    selected = select_products(
        candidates,
        stats,
        args.target_products,
        args.min_reviews,
        args.min_review_months,
    )
    if not selected:
        raise SystemExit("No products met the review-count/time-span criteria.")

    build_outputs(args, candidates, stats, reviews_by_product, selected)
    print(f"Selected products: {len(selected)}")
    print(f"Wrote Phase 1 CSVs to {args.out_dir}")
    print(f"Wrote selection summary to {args.report_dir / 'source_selection_summary.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

