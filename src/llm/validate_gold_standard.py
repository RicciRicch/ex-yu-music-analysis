"""
src/llm/validate_gold_standard.py

Spaja LLM klasifikacije sa gold standard (ljudskim) anotacijama po
song_id, računa Cohen's kappa za theme/emotion (elaborat 4.6), i
priprema pregled neslaganja za kvalitativnu analizu.

Pokretanje (iz root foldera projekta):
    python src/llm/validate_gold_standard.py
"""

import re
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.config import GOLD_STANDARD_DIR, REPORTS_DIR

GOLD_PATH = GOLD_STANDARD_DIR / "gold_standard_sample.csv"
LLM_PATH = REPORTS_DIR / "llm_classifications.csv"


def normalize_category(text) -> str:
    """Normalizuje kategoriju pre poređenja - mala slova, bez viška
    razmaka, bez dijakritika - da 'društvo' i 'drustvo' budu ISTA
    vrednost, bez obzira ko je i kako otkucao."""
    if not isinstance(text, str):
        return ""
    text = text.strip().lower()
    text = re.sub(r'\s+', ' ', text)
    replacements = {'š': 's', 'č': 'c', 'ć': 'c', 'ž': 'z', 'đ': 'dj'}
    for a, b in replacements.items():
        text = text.replace(a, b)
    return text


def main():
    gold = pd.read_csv(GOLD_PATH)
    llm = pd.read_csv(LLM_PATH)

    merged = gold.merge(
        llm[["song_id", "llm_theme", "llm_emotion", "llm_values"]],
        on="song_id",
        how="inner",
    )
    print(f"Spojeno {len(merged)} pesama (gold: {len(gold)}, llm: {len(llm)})")

    merged["gold_theme_norm"] = merged["gold_theme"].apply(normalize_category)
    merged["llm_theme_norm"] = merged["llm_theme"].apply(normalize_category)
    merged["gold_emotion_norm"] = merged["gold_emotion"].apply(normalize_category)
    merged["llm_emotion_norm"] = merged["llm_emotion"].apply(normalize_category)

    theme_kappa = cohen_kappa_score(merged["gold_theme_norm"], merged["llm_theme_norm"])
    emotion_kappa = cohen_kappa_score(merged["gold_emotion_norm"], merged["llm_emotion_norm"])

    theme_agreement = (merged["gold_theme_norm"] == merged["llm_theme_norm"]).mean()
    emotion_agreement = (merged["gold_emotion_norm"] == merged["llm_emotion_norm"]).mean()

    print(f"\n=== TEMA ===")
    print(f"Cohen's kappa: {theme_kappa:.3f}")
    print(f"Prosto slaganje: {theme_agreement:.1%}")

    print(f"\n=== EMOCIJA ===")
    print(f"Cohen's kappa: {emotion_kappa:.3f}")
    print(f"Prosto slaganje: {emotion_agreement:.1%}")

    print(f"\n=== Unakrsna tabela TEME (red=gold, kolona=llm) ===")
    print(pd.crosstab(merged["gold_theme_norm"], merged["llm_theme_norm"]))

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / "gold_vs_llm_comparison.csv"
    cols = ["song_id", "artist", "title", "period", "genre",
            "gold_theme", "llm_theme", "gold_emotion", "llm_emotion",
            "gold_values", "llm_values"]
    merged[cols].to_csv(out_path, index=False, encoding="utf-8")
    print(f"\nSačuvano: {out_path}")

    disagreements = merged[merged["gold_theme_norm"] != merged["llm_theme_norm"]]
    disagree_path = REPORTS_DIR / "gold_vs_llm_disagreements.csv"
    disagreements[cols].to_csv(disagree_path, index=False, encoding="utf-8")
    print(f"Neslaganja po temi ({len(disagreements)} pesama): {disagree_path}")


if __name__ == "__main__":
    main()