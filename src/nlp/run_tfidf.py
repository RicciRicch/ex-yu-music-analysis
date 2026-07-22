"""
src/nlp/run_tfidf.py

Primenjuje TF-IDF analizu ključnih reči po periodu i po žanru na
corpus_analysis_ready.csv, čuva rezultate kao CSV izveštaje.

Pokretanje (iz root foldera projekta):
    python src/nlp/run_tfidf.py
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.config import PROCESSED_DATA_DIR, REPORTS_DIR
from src.nlp.tfidf_keywords import top_keywords_by_group

INPUT_PATH = PROCESSED_DATA_DIR / "corpus_analysis_ready.csv"


def run_and_save(df: pd.DataFrame, group_col: str, top_n: int = 20):
    results = top_keywords_by_group(df, group_col, top_n=top_n)

    rows = []
    for group, words in results.items():
        for rank, (word, score) in enumerate(words, start=1):
            rows.append({"grupa": group, "rang": rank, "rec": word, "tfidf_skor": score})

    out_df = pd.DataFrame(rows)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / f"tfidf_top_reci_{group_col}.csv"
    out_df.to_csv(out_path, index=False, encoding="utf-8")

    print(f"\n=== TF-IDF po '{group_col}' ===")
    for group, words in results.items():
        top10 = ', '.join(w for w, _ in words[:10])
        print(f"  {group}: {top10}")
    print(f"Sačuvano: {out_path}")


def main():
    df = pd.read_csv(INPUT_PATH)
    print(f"Učitano {len(df)} pesama iz {INPUT_PATH}")

    run_and_save(df, "period")
    run_and_save(df, "genre")


if __name__ == "__main__":
    main()