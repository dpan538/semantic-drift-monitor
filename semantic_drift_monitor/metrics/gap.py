import math
import re
from collections import Counter


def semantic_gap(promo_texts: list[str], review_texts: list[str]) -> float:
    promo = " ".join(text for text in promo_texts if isinstance(text, str)).strip()
    reviews = " ".join(text for text in review_texts if isinstance(text, str)).strip()
    if not promo or not reviews:
        return 0.0
    promo_vector = _ngram_counts(promo)
    review_vector = _ngram_counts(reviews)
    similarity = _cosine(promo_vector, review_vector)
    return float(1 - similarity)


def _tokens(text: str) -> list[str]:
    return re.findall(r"\b[\w-]+\b", text.lower())


def _ngram_counts(text: str) -> Counter:
    tokens = _tokens(text)
    counts: Counter = Counter(tokens)
    counts.update(" ".join(tokens[index : index + 2]) for index in range(len(tokens) - 1))
    return counts


def _cosine(left: Counter, right: Counter) -> float:
    if not left or not right:
        return 0.0
    shared = set(left) & set(right)
    numerator = sum(left[key] * right[key] for key in shared)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)
