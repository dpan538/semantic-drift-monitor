from semantic_drift_monitor.text_processing.phrase_matcher import match_phrases


def extract_claims(text: str, promo_lexicon: dict[str, list[str]]) -> list[dict]:
    claims: list[dict] = []
    for match in match_phrases(text, promo_lexicon):
        claims.append(
            {
                "claim_type": match.category,
                "claim_text": match.term,
                "start": match.start,
                "end": match.end,
            }
        )
    return claims

