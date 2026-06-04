#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import time
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib import robotparser
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_USER_AGENT = "SemanticDriftMonitor/0.1 academic-research"


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip_depth = 0
        self.title_parts: list[str] = []
        self.in_title = False

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style", "noscript"}:
            self.skip_depth += 1
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self.skip_depth:
            self.skip_depth -= 1
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if not text:
            return
        if self.in_title:
            self.title_parts.append(text)
        if self.skip_depth == 0:
            self.parts.append(text)

    @property
    def visible_text(self) -> str:
        return " ".join(self.parts)

    @property
    def title(self) -> str:
        return " ".join(self.title_parts)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect permitted static product-page snapshots.")
    parser.add_argument("--targets", type=Path, required=True, help="CSV with product_id,url columns.")
    parser.add_argument("--out", type=Path, default=ROOT / "data/raw/snapshots.csv")
    parser.add_argument("--html-dir", type=Path, default=ROOT / "data/raw/html")
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    parser.add_argument("--confirm-compliance", action="store_true", help="Required to perform URL requests.")
    return parser.parse_args()


def robots_allowed(url: str, user_agent: str) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    robots = robotparser.RobotFileParser()
    robots.set_url(robots_url)
    try:
        robots.read()
    except Exception:
        return False
    return robots.can_fetch(user_agent, url)


def fetch_html(url: str, user_agent: str) -> str:
    request = Request(url, headers={"User-Agent": user_agent})
    with urlopen(request, timeout=30) as response:
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type and "application/xhtml" not in content_type:
            raise ValueError(f"Unsupported content type: {content_type}")
        return response.read().decode("utf-8", errors="replace")


def load_targets(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"product_id", "url"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Targets file missing columns: {', '.join(sorted(missing))}")
        return [row for row in reader if row.get("product_id") and row.get("url")]


def main() -> int:
    args = parse_args()
    if not args.confirm_compliance:
        raise SystemExit("Refusing to collect. Re-run with --confirm-compliance after checking ToS and robots rules.")

    targets = load_targets(args.targets)
    args.html_dir.mkdir(parents=True, exist_ok=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    capture_date = date.today().isoformat()
    for target in targets:
        product_id = target["product_id"]
        url = target["url"]
        print(f"checking robots for {product_id}: {url}")
        if not robots_allowed(url, args.user_agent):
            print(f"skipping {product_id}: robots check did not allow collection")
            continue
        try:
            html = fetch_html(url, args.user_agent)
        except (URLError, ValueError) as exc:
            print(f"failed {product_id}: {exc}")
            continue

        html_path = args.html_dir / f"{product_id}_{capture_date}.html"
        html_path.write_text(html, encoding="utf-8")

        parser = VisibleTextParser()
        parser.feed(html)
        rows.append(
            {
                "product_id": product_id,
                "snapshot_date": capture_date,
                "title": parser.title,
                "description": parser.visible_text,
                "bullet_points": "",
                "image_ocr_text": "",
                "price": "",
                "rating_avg": "",
                "rating_count": "",
                "review_count": "",
                "source_url": url,
                "source_method": "permitted_static_snapshot",
            }
        )
        time.sleep(args.delay)

    with args.out.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
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
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} snapshot rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

