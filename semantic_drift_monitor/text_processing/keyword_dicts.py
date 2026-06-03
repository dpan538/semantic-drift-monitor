from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - exercised only in minimal environments.
    yaml = None


def load_yaml_lexicon(path: str | Path) -> dict:
    text = Path(path).read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text) or {}
    return _parse_simple_yaml(text)


def flatten_lexicon(lexicon: dict) -> list[str]:
    terms: list[str] = []
    for values in lexicon.values():
        terms.extend(values or [])
    return terms


def _parse_simple_yaml(text: str) -> dict:
    """Parse the small subset of YAML used by the bundled dictionaries.

    Supports:
    - top-level mapping to lists
    - top-level mapping to scalar float/string values
    """
    result: dict = {}
    current_key: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and line.endswith(":"):
            current_key = line[:-1].strip()
            result[current_key] = []
            continue
        if line.startswith("  - ") and current_key is not None:
            value = line[4:].strip().strip('"').strip("'")
            result[current_key].append(value)
            continue
        if not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = _coerce_scalar(value.strip().strip('"').strip("'"))
    return result


def _coerce_scalar(value: str):
    try:
        return float(value)
    except ValueError:
        return value
