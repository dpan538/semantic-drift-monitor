from config import ABSTRACTION_THRESHOLD
from semantic_drift_monitor.text_processing.phrase_matcher import match_phrases


def abstractness_ratio(text: str, concreteness_scores: dict[str, float], threshold: float = ABSTRACTION_THRESHOLD) -> float:
    if not text:
        return 0.0
    lexicon = {"concreteness": list(concreteness_scores.keys())}
    matches = match_phrases(text.lower(), lexicon)
    scored = [concreteness_scores.get(match.term) for match in matches]
    scored = [score for score in scored if score is not None]
    if not scored:
        return 0.0
    abstract = sum(1 for score in scored if float(score) < threshold)
    return abstract / len(scored)

