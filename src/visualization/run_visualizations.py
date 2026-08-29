"""
src/visualization/run_visualizations.py

Generiše sve vizualizacije iz postojećih CSV izveštaja (Faze 4 i 5).

Pokretanje (iz root foldera projekta):
    python src/visualization/run_visualizations.py
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.config import FIGURES_DIR, REPORTS_DIR, GENRE_LABELS_SR, PERIOD_LABELS_SR
from src.visualization.wordclouds import make_wordcloud
from src.visualization.charts import (
    sentiment_trend_chart,
    lexical_diversity_chart,
    topic_heatmap,
    gold_vs_llm_theme_chart,
)


def make_all_wordclouds():
    print("Pravljenje word cloud-ova...")

    tfidf_period = pd.read_csv(REPORTS_DIR / "tfidf_top_reci_period.csv")
    for period in tfidf_period["grupa"].unique():
        subset = tfidf_period[tfidf_period["grupa"] == period]
        scores = dict(zip(subset["rec"], subset["tfidf_skor"]))
        label = PERIOD_LABELS_SR.get(period, period)
        make_wordcloud(scores, f"Karakteristične reči - {label}",
                        FIGURES_DIR / f"wordcloud_period_{period}.png")

    tfidf_genre = pd.read_csv(REPORTS_DIR / "tfidf_top_reci_genre.csv")
    for genre in tfidf_genre["grupa"].unique():
        subset = tfidf_genre[tfidf_genre["grupa"] == genre]
        scores = dict(zip(subset["rec"], subset["tfidf_skor"]))
        label = GENRE_LABELS_SR.get(genre, genre)
        make_wordcloud(scores, f"Karakteristične reči - {label}",
                        FIGURES_DIR / f"wordcloud_genre_{genre}.png")

    print(f"  Sačuvano {tfidf_period['grupa'].nunique() + tfidf_genre['grupa'].nunique()} word cloud-ova")


def make_trend_charts():
    print("Pravljenje grafova trendova...")

    sentiment = pd.read_csv(REPORTS_DIR / "sentiment_by_period.csv", index_col=0)
    sentiment_trend_chart(sentiment, FIGURES_DIR / "sentiment_trend.png")

    lexdiv = pd.read_csv(REPORTS_DIR / "lexical_diversity_by_period.csv", index_col=0)
    lexical_diversity_chart(lexdiv, FIGURES_DIR / "lexical_diversity_trend.png")

    print("  Sačuvano 2 grafa trendova")


def make_topic_heatmaps():
    print("Pravljenje heatmap-a tema...")

    lda_period = pd.read_csv(REPORTS_DIR / "lda_topic_by_period.csv", index_col=0)
    lda_period = lda_period[["sfrj", "tranzicija", "savremeno"]]
    topic_heatmap(lda_period, "Zastupljenost LDA tema po periodu",
                  FIGURES_DIR / "lda_topics_by_period_heatmap.png")

    lda_genre = pd.read_csv(REPORTS_DIR / "lda_topic_by_genre.csv", index_col=0)
    topic_heatmap(lda_genre, "Zastupljenost LDA tema po žanru",
                  FIGURES_DIR / "lda_topics_by_genre_heatmap.png")

    print("  Sačuvano 2 heatmap-e")


def make_llm_comparison_chart():
    print("Pravljenje LLM/gold standard poređenja...")

    comparison = pd.read_csv(REPORTS_DIR / "gold_vs_llm_comparison.csv")
    gold_vs_llm_theme_chart(comparison, FIGURES_DIR / "gold_vs_llm_theme_comparison.png")

    print("  Sačuvano 1 grafik poređenja")


def main():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    make_all_wordclouds()
    make_trend_charts()
    make_topic_heatmaps()
    make_llm_comparison_chart()
    print(f"\nSve vizualizacije sačuvane u: {FIGURES_DIR}")


if __name__ == "__main__":
    main()