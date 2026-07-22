"""
src/nlp/run_ner.py

Ekstraktuje imenovane entitete (PER - osobe, LOC - mesta, ORG - organizacije)
iz svake pesme koristeći classla, čuva sirove entitete i agregira
najčešće po periodu/žanru.

NAPOMENA: NER model ume pogrešno da klasifikuje imena bendova kao osobe
(npr. "Bijelo Dugme" -> PER umesto ORG) - poznato ograničenje modela na
žanrovski specifičnim imenima, ne greška u kodu.

Pokretanje (iz root foldera projekta):
    python src/nlp/run_ner.py
"""

import sys
import time
from collections import Counter
from pathlib import Path

import classla
import pandas as pd
from tqdm import tqdm

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.config import PROCESSED_DATA_DIR, REPORTS_DIR

INPUT_PATH = PROCESSED_DATA_DIR / "corpus_analysis_ready.csv"

# Za probu pre punog pokretanja - promeni na None kad budeš spremna za sve
TEST_LIMIT = None


def extract_entities(nlp, text: str):
    if not text or not text.strip():
        return []
    doc = nlp(text)
    return [(ent.text, ent.type) for ent in doc.entities]


def main():
    df = pd.read_csv(INPUT_PATH)
    print(f"Učitano {len(df)} pesama")

    if TEST_LIMIT:
        df = df.head(TEST_LIMIT).copy()
        print(f"PROBNI REŽIM: obrađujem samo prvih {TEST_LIMIT} pesama")

    print("Učitavanje classla NER pipeline-a...")
    nlp = classla.Pipeline('sr', processors='tokenize,ner', verbose=False)

    start = time.time()
    all_entities = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="NER"):
        entities = extract_entities(nlp, row["lyrics_clean"])
        for text, etype in entities:
            all_entities.append({
                "song_id": row["song_id"],
                "period": row["period"],
                "genre": row["genre"],
                "entity_text": text,
                "entity_type": etype,
            })
    elapsed = time.time() - start

    ent_df = pd.DataFrame(all_entities)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ent_path = REPORTS_DIR / "ner_entities_raw.csv"
    ent_df.to_csv(ent_path, index=False, encoding="utf-8")

    print(f"\nSačuvano: {ent_path} ({len(ent_df)} entiteta)")
    print(f"Vreme: {elapsed:.1f}s za {len(df)} pesama ({elapsed/len(df):.2f}s po pesmi)")
    if TEST_LIMIT:
        procena_min = (elapsed / len(df)) * 4084 / 60
        print(f"Procena za ceo korpus (4084 pesama): ~{procena_min:.0f} minuta")

    if not TEST_LIMIT and len(ent_df):
        print("\nTop 15 entiteta po tipu:")
        for etype in ent_df["entity_type"].unique():
            top = Counter(ent_df[ent_df["entity_type"] == etype]["entity_text"]).most_common(15)
            print(f"\n{etype}:")
            for name, count in top:
                print(f"  {name}: {count}")


if __name__ == "__main__":
    main()