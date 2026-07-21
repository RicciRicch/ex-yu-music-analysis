"""
src/preprocessing/run_lemmatization.py

Tokenizuje i lematizuje ceo corpus_clean.csv koristeći classla (srpski
model), zadržavajući samo sadržajne reči (imenice, glagoli, pridevi,
prilozi, imena) - efektivno uklanjanje "stop reči" preko POS oznaka
umesto fiksne liste.

NAPOMENA O VREMENU: classla pipeline je spor na CPU-u (nema GPU
akceleraciju u ovom okruženju) - obrada svih ~4000 pesama može potrajati
duže vreme. Testiramo prvo na malom uzorku da procenimo koliko tačno.

Pokretanje (iz root foldera projekta):
    python src/preprocessing/run_lemmatization.py
"""

import sys
import time
from pathlib import Path

import classla
import pandas as pd
from tqdm import tqdm

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.config import PROCESSED_DATA_DIR

INPUT_PATH = PROCESSED_DATA_DIR / "corpus_clean.csv"
OUTPUT_PATH = PROCESSED_DATA_DIR / "corpus_lemmatized.csv"

CONTENT_POS = {"NOUN", "VERB", "ADJ", "ADV", "PROPN"}

# Za probu pre punog pokretanja - promeni na None kad budeš spremna za sve
TEST_LIMIT = None


def lemmatize_for_analysis(nlp, text: str) -> str:
    """Vraća tekst svedan na leme sadržajnih reči, malim slovima,
    razdvojene razmakom - spreman format za LDA/TF-IDF u Fazi 4."""
    if not text or not text.strip():
        return ""
    doc = nlp(text)
    lemmas = []
    for sentence in doc.sentences:
        for word in sentence.words:
            if word.upos in CONTENT_POS and word.lemma:
                lemmas.append(word.lemma.lower())
    return ' '.join(lemmas)


def main():
    df = pd.read_csv(INPUT_PATH)
    print(f"Učitano {len(df)} pesama iz {INPUT_PATH}")

    if TEST_LIMIT:
        df = df.head(TEST_LIMIT).copy()
        print(f"PROBNI REŽIM: obrađujem samo prvih {TEST_LIMIT} pesama")

    print("Učitavanje classla pipeline-a (10-20s)...")
    nlp = classla.Pipeline('sr', processors='tokenize,pos,lemma', verbose=False)

    start = time.time()
    lemmas_col = []
    for text in tqdm(df["lyrics_clean"].fillna(""), desc="Lematizacija"):
        lemmas_col.append(lemmatize_for_analysis(nlp, text))
    elapsed = time.time() - start

    df["lemmas"] = lemmas_col
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    # Finalni filter za NLP-spremni korpus (Faza 4) - izbacujemo pesme sa
    # premalo lema (uglavnom strane, ne-ex-yu-jezičke verzije pesama, vidi
    # README "Poznata ograničenja")
    MIN_LEMMAS = 10
    lemma_counts = df["lemmas"].fillna("").str.split().str.len()
    analysis_ready = df[lemma_counts >= MIN_LEMMAS].copy()
    excluded = len(df) - len(analysis_ready)

    analysis_ready_path = PROCESSED_DATA_DIR / "corpus_analysis_ready.csv"
    analysis_ready.to_csv(analysis_ready_path, index=False, encoding="utf-8")

    print(f"\nFilter za analizu: izbačeno {excluded} pesama sa manje od {MIN_LEMMAS} lema")
    print(f"(uglavnom strane/ne-ex-yu-jezičke verzije pesama - vidi primere u README)")
    print(f"Analiza-spreman korpus: {len(analysis_ready)} pesama -> {analysis_ready_path}")

    print(f"\nSačuvano u: {OUTPUT_PATH}")
    print(f"Vreme: {elapsed:.1f}s za {len(df)} pesama ({elapsed/len(df):.2f}s po pesmi)")
    if TEST_LIMIT:
        procena_min = (elapsed / len(df)) * 4113 / 60
        print(f"Procena za ceo korpus (4113 pesama): ~{procena_min:.0f} minuta")


if __name__ == "__main__":
    main()