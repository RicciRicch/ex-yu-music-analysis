"""
src/nlp/run_topic_modeling.py

Trenira LDA model na celom corpus_analysis_ready.csv, dodeljuje
dominantnu temu svakoj pesmi, čuva top reči po temi i zastupljenost
tema po periodu/žanru.

Pokretanje (iz root foldera projekta):
    python src/nlp/run_topic_modeling.py
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.config import PROCESSED_DATA_DIR, REPORTS_DIR
from src.nlp.topic_modeling_lda import build_corpus, get_dominant_topic, train_lda

INPUT_PATH = PROCESSED_DATA_DIR / "corpus_analysis_ready.csv"
NUM_TOPICS = 10  # hiperparametar - može se menjati/podešavati


def main():
    df = pd.read_csv(INPUT_PATH)
    print(f"Učitano {len(df)} pesama")

    texts = df["lemmas"].fillna("").tolist()
    dictionary, corpus, tokenized = build_corpus(texts)
    print(f"Rečnik posle filtriranja: {len(dictionary)} jedinstvenih reči")

    print(f"Treniranje LDA modela sa {NUM_TOPICS} tema...")
    lda = train_lda(corpus, dictionary, num_topics=NUM_TOPICS)

    print("\n--- Teme (top 10 reči po temi) ---")
    topic_words = {}
    for idx in range(NUM_TOPICS):
        words = [w for w, _ in lda.show_topic(idx, topn=10)]
        topic_words[idx] = words
        print(f"Tema {idx}: {', '.join(words)}")

    dominant_topics, dominant_probs = [], []
    for tokens in tokenized:
        topic_id, prob = get_dominant_topic(lda, dictionary, tokens)
        dominant_topics.append(topic_id)
        dominant_probs.append(round(prob, 3))

    df["dominant_topic"] = dominant_topics
    df["topic_probability"] = dominant_probs

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    per_song_path = REPORTS_DIR / "lda_topics_per_song.csv"
    df[["song_id", "artist", "title", "period", "genre", "dominant_topic", "topic_probability"]].to_csv(
        per_song_path, index=False, encoding="utf-8"
    )
    print(f"\nSačuvano po pesmi: {per_song_path}")

    tw_rows = [{"tema": idx, "top_reci": ", ".join(words)} for idx, words in topic_words.items()]
    topic_words_path = REPORTS_DIR / "lda_topic_words.csv"
    pd.DataFrame(tw_rows).to_csv(topic_words_path, index=False, encoding="utf-8")
    print(f"Sačuvano reči po temi: {topic_words_path}")

    for group_col in ["period", "genre"]:
        crosstab = pd.crosstab(df["dominant_topic"], df[group_col], normalize="columns").round(3)
        out_path = REPORTS_DIR / f"lda_topic_by_{group_col}.csv"
        crosstab.to_csv(out_path, encoding="utf-8")
        print(f"\n=== Zastupljenost tema po '{group_col}' ===")
        print(crosstab)
        print(f"Sačuvano: {out_path}")


if __name__ == "__main__":
    main()