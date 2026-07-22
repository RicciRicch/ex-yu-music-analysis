"""
src/nlp/run_bertopic_clustering.py

Računa BERT embeddings jednom, koristi ih i za BERTopic i za K-means
klasterizaciju.

NAPOMENA O VREMENU: računanje embeddings-a na CPU-u (nemamo GPU) je
najsporiji korak. Testiramo prvo na malom uzorku pre punog korpusa.

Pokretanje (iz root foldera projekta):
    python src/nlp/run_bertopic_clustering.py
"""

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.config import PROCESSED_DATA_DIR, REPORTS_DIR
from src.nlp.embeddings_topics import (
    compute_embeddings,
    load_embedding_model,
    run_bertopic,
    run_kmeans,
)

INPUT_PATH = PROCESSED_DATA_DIR / "corpus_analysis_ready.csv"
EMBEDDINGS_CACHE = PROCESSED_DATA_DIR / "embeddings.npy"

# Za probu pre punog pokretanja - promeni na None kad budeš spremna za sve
TEST_LIMIT = None


def main():
    df = pd.read_csv(INPUT_PATH)
    print(f"Učitano {len(df)} pesama")

    if TEST_LIMIT:
        df = df.head(TEST_LIMIT).copy()
        print(f"PROBNI REŽIM: obrađujem samo prvih {TEST_LIMIT} pesama")

    texts = df["lyrics_clean"].fillna("").tolist()

    print("Učitavanje višejezičnog modela (prvi put skida ~470MB, posle je keširano)...")
    model = load_embedding_model()

    print("Računanje embeddings-a...")
    start = time.time()
    embeddings = compute_embeddings(model, texts)
    elapsed = time.time() - start
    print(f"Embeddings gotovi: {elapsed:.1f}s za {len(texts)} pesama ({elapsed/len(texts):.2f}s po pesmi)")
    if TEST_LIMIT:
        procena_min = (elapsed / len(texts)) * 4084 / 60
        print(f"Procena za ceo korpus (4084 pesama): ~{procena_min:.0f} minuta")

    if not TEST_LIMIT:
        np.save(EMBEDDINGS_CACHE, embeddings)
        print(f"Embeddings sačuvani: {EMBEDDINGS_CACHE}")

    print("\nTreniranje BERTopic modela...")
    topic_model, topics = run_bertopic(texts, embeddings, model)
    df["bertopic_topic"] = topics

    print("\n--- BERTopic teme ---")
    topic_info = topic_model.get_topic_info()
    print(topic_info.head(15).to_string(index=False))

    print("\nK-means klasterizacija (10 klastera)...")
    kmeans_labels = run_kmeans(embeddings, n_clusters=10)
    df["kmeans_cluster"] = kmeans_labels

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    out_path = REPORTS_DIR / "bertopic_kmeans_per_song.csv"
    df[["song_id", "artist", "title", "period", "genre", "bertopic_topic", "kmeans_cluster"]].to_csv(
        out_path, index=False, encoding="utf-8"
    )
    print(f"\nSačuvano: {out_path}")

    topic_info_path = REPORTS_DIR / "bertopic_topic_info.csv"
    topic_info.to_csv(topic_info_path, index=False, encoding="utf-8")
    print(f"Sačuvano info o temama: {topic_info_path}")


if __name__ == "__main__":
    main()