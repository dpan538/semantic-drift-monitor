import re

from semantic_drift_monitor.text_processing.phrase_matcher import category_counts, match_phrases


def token_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))


def promo_density(text: str, keyword_dict: dict[str, list[str]]) -> float:
    matches = match_phrases(text, keyword_dict)
    return len(matches) / max(token_count(text), 1) * 100


def promo_density_by_category(text: str, keyword_dict: dict[str, list[str]]) -> dict[str, float]:
    counts = category_counts(text, keyword_dict)
    total_tokens = max(token_count(text), 1)
    return {category: count / total_tokens * 100 for category, count in counts.items()}

