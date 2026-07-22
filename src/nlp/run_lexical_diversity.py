"""
src/nlp/run_lexical_diversity.py

Računa TTR, MATTR i grubu Flesch-Kincaid adaptaciju za svaku pesmu,
agregira (prosek) po periodu i po žanru.

Pokretanje (iz root foldera projekta):
    python src/nlp/run_lexical_diversity.py
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.config import PROCESSED_DATA_DIR, REPORTS_DIR
from src.nlp.lexical_diversity import flesch_kincaid_grade_sr, mattr, type_token_ratio

INPUT_PATH = PROCESSED_DATA_DIR / "corpus_analysis_ready.csv"


def main():
    df = pd.read_csv(INPUT_PATH)
    print(f"Učitano {len(df)} pesama")

    # Koristimo lyrics_clean (pravi oblik reči), ne lemme - za TTR i
    # čitljivost želimo stvarne reči kako se pojavljuju u tekstu.
    lyrics = df["lyrics_clean"].fillna("")
    df["ttr"] = lyrics.apply(type_token_ratio)
    df["mattr"] = lyrics.apply(mattr)
    df["fk_grade"] = lyrics.apply(flesch_kincaid_grade_sr)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    per_song_path = REPORTS_DIR / "lexical_diversity_per_song.csv"
    df[["song_id", "artist", "title", "period", "genre", "ttr", "mattr", "fk_grade"]].to_csv(
        per_song_path, index=False, encoding="utf-8"
    )
    print(f"Sačuvano po pesmi: {per_song_path}")

    for group_col in ["period", "genre"]:
        agg = df.groupby(group_col)[["ttr", "mattr", "fk_grade"]].mean().round(3)
        agg_path = REPORTS_DIR / f"lexical_diversity_by_{group_col}.csv"
        agg.to_csv(agg_path, encoding="utf-8")
        print(f"\n=== Prosek po '{group_col}' ===")
        print(agg)
        print(f"Sačuvano: {agg_path}")


if __name__ == "__main__":
    main()