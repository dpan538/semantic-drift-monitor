#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "run_pipeline.py",
    "config.py",
    "dictionaries/promo_sunscreen_en.yaml",
    "dictionaries/skepticism_en.yaml",
    "dictionaries/value_en.yaml",
    "dictionaries/scenarios_sunscreen_en.yaml",
    "examples/demo_products.csv",
    "examples/demo_snapshots.csv",
    "examples/demo_reviews.csv",
]

CORE_MODULES = ["pandas", "numpy"]
OPTIONAL_MODULES = ["yaml"]
OPTIONAL_ENV_VARS = [
    "AMAZON_PAAPI_ACCESS_KEY",
    "AMAZON_PAAPI_SECRET_KEY",
    "AMAZON_PAAPI_PARTNER_TAG",
]


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def main() -> int:
    print("Semantic Drift Monitor environment check")
    print(f"Repository: {ROOT}")
    print(f"Python: {sys.version.split()[0]}")

    ok = True

    if sys.version_info < (3, 10):
        print("[FAIL] Python >= 3.10 is required.")
        ok = False
    else:
        print("[ OK ] Python version is compatible.")

    for module in CORE_MODULES:
        if module_available(module):
            print(f"[ OK ] Python module available: {module}")
        else:
            print(f"[FAIL] Missing required Python module: {module}")
            ok = False

    for module in OPTIONAL_MODULES:
        status = "available" if module_available(module) else "not installed; fallback parser will be used"
        print(f"[INFO] Optional module {module}: {status}")

    for relative_path in REQUIRED_FILES:
        path = ROOT / relative_path
        if path.exists():
            print(f"[ OK ] Required file exists: {relative_path}")
        else:
            print(f"[FAIL] Missing required file: {relative_path}")
            ok = False

    for env_var in OPTIONAL_ENV_VARS:
        status = "set" if os.getenv(env_var) else "not set"
        print(f"[INFO] Optional credential {env_var}: {status}")

    if ok:
        print("Environment check passed.")
        return 0
    print("Environment check failed. Install requirements or restore missing files.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

