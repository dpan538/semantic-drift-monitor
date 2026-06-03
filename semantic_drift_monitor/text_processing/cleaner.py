import re


def normalize_text(text: object) -> str:
    if text is None:
        return ""
    value = str(text).lower()
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def sentence_split(text: object) -> list[str]:
    clean = normalize_text(text)
    if not clean:
        return []
    return [sentence.strip() for sentence in re.split(r"[.!?]+", clean) if sentence.strip()]

