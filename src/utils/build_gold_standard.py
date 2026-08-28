"""
src/utils/build_gold_standard.py

Pravi stratifikovan uzorak od ~300 pesama za ručnu anotaciju (gold
standard), proporcionalno zastupljen po periodu i žanru - u skladu sa
elaboratom (4.6).
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.config import GOLD_STANDARD_DIR, GOLD_STANDARD_SIZE, PROCESSED_DATA_DIR

INPUT_PATH = PROCESSED_DATA_DIR / "corpus_analysis_ready.csv"
OUTPUT_PATH = GOLD_STANDARD_DIR / "gold_standard_sample.csv"


def main():
    df = pd.read_csv(INPUT_PATH)
    print(f"Učitano {len(df)} pesama")

    frac = GOLD_STANDARD_SIZE / len(df)
    sample = df.groupby(["period", "genre"], group_keys=False).sample(frac=frac, random_state=42)

    print(f"Uzorkovano {len(sample)} pesama (cilj: {GOLD_STANDARD_SIZE})")
    print("\nRaspodela po periodu:")
    print(sample["period"].value_counts())
    print("\nRaspodela po žanru:")
    print(sample["genre"].value_counts())

    sample = sample.copy()
    sample["gold_theme"] = ""      # vidi listu ispod
    sample["gold_emotion"] = ""    # pozitivno / negativno / neutralno / mešano
    sample["gold_values"] = ""     # slobodan tekst - koje vrednosti pesma izražava
    sample["annotator_notes"] = ""

    GOLD_STANDARD_DIR.mkdir(parents=True, exist_ok=True)
    cols = ["song_id", "artist", "title", "year", "period", "genre", "lyrics_clean",
            "gold_theme", "gold_emotion", "gold_values", "annotator_notes"]
    sample[cols].to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"\nSačuvano: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()