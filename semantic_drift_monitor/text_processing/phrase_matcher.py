import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PhraseMatch:
    category: str
    term: str
    start: int
    end: int


def compile_phrase_patterns(lexicon: dict[str, list[str]]) -> list[tuple[str, str, re.Pattern]]:
    patterns: list[tuple[str, str, re.Pattern]] = []
    for category, terms in lexicon.items():
        for term in terms or []:
            escaped = re.escape(term.lower()).replace(r"\ ", r"\s+")
            pattern = re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)
            patterns.append((category, term, pattern))
    return patterns


def match_phrases(text: str, lexicon: dict[str, list[str]]) -> list[PhraseMatch]:
    matches: list[PhraseMatch] = []
    for category, term, pattern in compile_phrase_patterns(lexicon):
        for match in pattern.finditer(text or ""):
            matches.append(PhraseMatch(category=category, term=term, start=match.start(), end=match.end()))
    return sorted(matches, key=lambda item: (item.start, item.end, item.term))


def category_counts(text: str, lexicon: dict[str, list[str]]) -> dict[str, int]:
    counts = {category: 0 for category in lexicon}
    for match in match_phrases(text, lexicon):
        counts[match.category] = counts.get(match.category, 0) + 1
    return counts

