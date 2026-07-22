"""
src/nlp/run_sentiment.py

Primenjuje leksikonsku sentiment analizu na ceo corpus_analysis_ready.csv,
agregira po periodu i žanru.

Pokretanje (iz root foldera projekta):
    python src/nlp/run_sentiment.py
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.config import PROCESSED_DATA_DIR, REPORTS_DIR
from src.nlp.sentiment_lexicon import sentiment_label, sentiment_score

INPUT_PATH = PROCESSED_DATA_DIR / "corpus_analysis_ready.csv"


def main():
    df = pd.read_csv(INPUT_PATH)
    print(f"Učitano {len(df)} pesama")

    lemmas = df["lemmas"].fillna("")
    df["sentiment_score"] = lemmas.apply(sentiment_score)
    df["sentiment_label"] = df["sentiment_score"].apply(sentiment_label)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    per_song_path = REPORTS_DIR / "sentiment_per_song.csv"
    df[["song_id", "artist", "title", "period", "genre", "sentiment_score", "sentiment_label"]].to_csv(
        per_song_path, index=False, encoding="utf-8"
    )
    print(f"Sačuvano po pesmi: {per_song_path}")

    for group_col in ["period", "genre"]:
        print(f"\n=== Sentiment po '{group_col}' ===")
        label_dist = df.groupby(group_col)["sentiment_label"].value_counts(normalize=True).unstack().fillna(0).round(3)
        print(label_dist)

        avg_score = df.groupby(group_col)["sentiment_score"].mean().round(4)
        print(f"\nProsečan skor po '{group_col}':")
        print(avg_score)

        out_path = REPORTS_DIR / f"sentiment_by_{group_col}.csv"
        label_dist.to_csv(out_path, encoding="utf-8")
        print(f"Sačuvano: {out_path}")


if __name__ == "__main__":
    main()