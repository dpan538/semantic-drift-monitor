from collections import Counter

import numpy as np

from semantic_drift_monitor.text_processing.phrase_matcher import match_phrases


def scenario_counts(texts: list[str], scenario_lexicon: dict[str, list[str]]) -> Counter:
    counts: Counter = Counter()
    for text in texts:
        found = {match.category for match in match_phrases(text or "", scenario_lexicon)}
        for category in found:
            counts[category] += 1
    return counts


def scenario_entropy(texts: list[str], scenario_lexicon: dict[str, list[str]]) -> float:
    counts = scenario_counts(texts, scenario_lexicon)
    if not counts:
        return 0.0
    total = sum(counts.values())
    probabilities = [count / total for count in counts.values()]
    entropy = -sum(p * np.log(p) for p in probabilities if p > 0)
    max_entropy = np.log(len(scenario_lexicon))
    return float(entropy / max_entropy) if max_entropy > 0 else 0.0

