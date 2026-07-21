"""
src/preprocessing/run_preprocessing.py

Primenjuje čišćenje teksta i detekciju jezika na CEO corpus.csv (izlaz
Faze 2) i čuva rezultat kao data/processed/corpus_clean.csv (izlaz Faze 3).

Pokretanje (iz root foldera projekta):
    python src/preprocessing/run_preprocessing.py
"""

import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.preprocessing.clean_text import clean_lyrics, is_cyrillic, detect_language

INPUT_PATH = RAW_DATA_DIR / "corpus.csv"
OUTPUT_PATH = PROCESSED_DATA_DIR / "corpus_clean.csv"


def main():
    df = pd.read_csv(INPUT_PATH)
    print(f"Učitano {len(df)} pesama iz {INPUT_PATH}")

    lyrics_clean = []
    languages = []

    for raw in tqdm(df["lyrics_raw"].fillna(""), desc="Čišćenje teksta"):
        was_cyr = is_cyrillic(raw)
        cleaned = clean_lyrics(raw)
        lang = detect_language(cleaned, was_cyr)
        lyrics_clean.append(cleaned)
        languages.append(lang)

    df["lyrics_clean"] = lyrics_clean
    df["language"] = languages

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print(f"\nSačuvano u: {OUTPUT_PATH}")
    print("\nRaspodela po jeziku:")
    print(df["language"].value_counts())

    empty_clean = (df["lyrics_clean"].str.strip() == "").sum()
    if empty_clean:
        print(f"\nUPOZORENJE: {empty_clean} pesama ima prazan lyrics_clean posle čišćenja - proveri ručno")


if __name__ == "__main__":
    main()