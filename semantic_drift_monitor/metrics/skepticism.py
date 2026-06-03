import numpy as np
import pandas as pd

from semantic_drift_monitor.text_processing.cleaner import sentence_split
from semantic_drift_monitor.text_processing.phrase_matcher import match_phrases


def flagged_sentence_ratio(texts: list[str], lexicon: dict[str, list[str]]) -> float:
    sentences: list[str] = []
    for text in texts:
        sentences.extend(sentence_split(text))
    if not sentences:
        return 0.0
    flagged = sum(1 for sentence in sentences if match_phrases(sentence, lexicon))
    return flagged / len(sentences)


def keyword_sentiment_drift(keyword: str, reviews_df: pd.DataFrame) -> float:
    if reviews_df.empty:
        return float("nan")
    df = reviews_df.copy()
    df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")
    df = df[df["review_text"].str.contains(keyword, case=False, na=False)]
    df = df.dropna(subset=["review_date"])
    if len(df) < 3:
        return float("nan")
    df["month_index"] = (df["review_date"] - df["review_date"].min()).dt.days / 30.44
    grouped = df.groupby("month_index")["rating"].mean().reset_index()
    if len(grouped) < 3:
        return float("nan")
    slope = np.polyfit(grouped["month_index"], grouped["rating"], 1)[0]
    return float(slope) if np.isfinite(slope) else float("nan")
