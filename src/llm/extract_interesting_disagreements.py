"""
src/llm/extract_interesting_disagreements.py

Izvlači posebno zanimljive slučajeve neslaganja LLM-a i ljudske
anotacije - konkretne primere za diskusiju u radu.

Fokus na dva obrasca koje smo uočile u validaciji:
1. EMOCIJA: gold je "mešano" ili "pozitivno", LLM kaže "negativno"
2. TEMA: gold je "hedonizam/provod" ili "politika/društvo" (retke
   kategorije koje LLM slabo prepoznaje), a LLM ih pogrešno svrstao

Pokretanje (iz root foldera projekta):
    python src/llm/extract_interesting_disagreements.py
"""

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.config import GOLD_STANDARD_DIR, REPORTS_DIR

GOLD_PATH = GOLD_STANDARD_DIR / "gold_standard_sample.csv"
LLM_PATH = REPORTS_DIR / "llm_classifications.csv"


def normalize_category(text) -> str:
    if not isinstance(text, str):
        return ""
    text = text.strip().lower()
    text = re.sub(r'\s+', ' ', text)
    for a, b in {'š': 's', 'č': 'c', 'ć': 'c', 'ž': 'z', 'đ': 'dj'}.items():
        text = text.replace(a, b)
    return text


def main():
    gold = pd.read_csv(GOLD_PATH)
    llm = pd.read_csv(LLM_PATH)

    merged = gold.merge(
        llm[["song_id", "llm_theme", "llm_emotion", "llm_values"]],
        on="song_id", how="inner",
    )

    merged["gold_theme_n"] = merged["gold_theme"].apply(normalize_category)
    merged["llm_theme_n"] = merged["llm_theme"].apply(normalize_category)
    merged["gold_emotion_n"] = merged["gold_emotion"].apply(normalize_category)
    merged["llm_emotion_n"] = merged["llm_emotion"].apply(normalize_category)

    # Slučaj 1: emocija "ublažena" u negativno
    emotion_cases = merged[
        merged["gold_emotion_n"].isin(["mesano", "pozitivno"])
        & (merged["llm_emotion_n"] == "negativno")
    ].copy()
    emotion_cases["tip_slucaja"] = "emocija: " + emotion_cases["gold_emotion"] + " -> negativno"

    # Slučaj 2: retka tema pogrešno svrstana
    theme_cases = merged[
        merged["gold_theme_n"].isin(["hedonizam/provod", "politika/drustvo"])
        & (merged["gold_theme_n"] != merged["llm_theme_n"])
    ].copy()
    theme_cases["tip_slucaja"] = "tema: " + theme_cases["gold_theme"] + " -> " + theme_cases["llm_theme"]

    combined = pd.concat([emotion_cases, theme_cases], ignore_index=True)
    combined["lyrics_snippet"] = combined["lyrics_clean"].fillna("").str.slice(0, 200)

    cols = [
        "tip_slucaja", "artist", "title", "period", "genre",
        "gold_theme", "llm_theme", "gold_emotion", "llm_emotion",
        "gold_values", "llm_values", "annotator_notes", "lyrics_snippet",
    ]

    out_path = REPORTS_DIR / "interesting_disagreements.csv"
    combined[cols].to_csv(out_path, index=False, encoding="utf-8")

    print(f"Ukupno zanimljivih slučajeva: {len(combined)}")
    print(f"  - emocija (mešano/pozitivno -> negativno): {len(emotion_cases)}")
    print(f"  - tema (retka kategorija pogrešno svrstana): {len(theme_cases)}")
    print(f"Sačuvano: {out_path}")

    with_notes = combined[combined["annotator_notes"].notna() & (combined["annotator_notes"] != "")]
    print(f"\nOd toga, {len(with_notes)} ima annotator_notes - najkorisniji za citiranje u radu:")
    if len(with_notes):
        print(with_notes[["artist", "title", "tip_slucaja", "annotator_notes"]].to_string(index=False))


if __name__ == "__main__":
    main()