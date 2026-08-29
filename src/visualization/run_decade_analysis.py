"""
src/visualization/run_decade_analysis.py

Finiji prikaz trendova po DEKADAMA (ne samo tri velika perioda) - spaja
postojeće per-pesma izveštaje sa 'decade' kolonom iz korpusa i pravi
linijske grafike koji pokazuju postepenu promenu kroz vreme.

Pokretanje (iz root foldera projekta):
    python src/visualization/run_decade_analysis.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.config import FIGURES_DIR, PROCESSED_DATA_DIR, REPORTS_DIR


def decade_sort_key(decades):
    return sorted(decades, key=lambda d: int(str(d).rstrip("s")))


def main():
    corpus = pd.read_csv(PROCESSED_DATA_DIR / "corpus_analysis_ready.csv")
    decade_map = corpus[["song_id", "decade"]]

    counts = decade_map["decade"].value_counts()
    ordered_decades = decade_sort_key(counts.index)
    print("Broj pesama po dekadi (proveri pouzdanost pre tumačenja trenda):")
    for d in ordered_decades:
        print(f"  {d}: {counts[d]}")

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # --- Sentiment kroz dekade ---
    sentiment = pd.read_csv(REPORTS_DIR / "sentiment_per_song.csv")
    sentiment = sentiment.merge(decade_map, on="song_id", how="left")
    sentiment_by_decade = sentiment.groupby("decade")["sentiment_score"].mean().reindex(ordered_decades)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(ordered_decades, sentiment_by_decade.values, marker="o", linewidth=2, color="#1E88E5")
    ax.axhline(0, color="gray", linestyle="--", linewidth=1)
    ax.set_title("Prosečan sentiment skor kroz dekade")
    ax.set_xlabel("Dekada")
    ax.set_ylabel("Sentiment skor (- negativno, + pozitivno)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "sentiment_by_decade.png", dpi=150)
    plt.close()

    # --- Leksička raznovrsnost (MATTR) kroz dekade ---
    lexdiv = pd.read_csv(REPORTS_DIR / "lexical_diversity_per_song.csv")
    lexdiv = lexdiv.merge(decade_map, on="song_id", how="left")
    mattr_by_decade = lexdiv.groupby("decade")["mattr"].mean().reindex(ordered_decades)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(ordered_decades, mattr_by_decade.values, marker="o", linewidth=2, color="#43A047")
    ax.set_title("Leksička raznovrsnost (MATTR) kroz dekade")
    ax.set_xlabel("Dekada")
    ax.set_ylabel("MATTR")
    plt.xticks(rotation=45)
    fig.text(0.5, -0.05,
             "Napomena: dekada je izvedena iz jedne procenjene godine po izvođaču, ne\n"
             "stvarne godine svake pesme - 2000s dekada je u ovom uzorku dominantno\n"
             "pop žanr (videti genre_by_decade.png), pa nalaz za tu tačku treba tumačiti oprezno.",
             ha="center", fontsize=8, style="italic")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "mattr_by_decade.png", dpi=150, bbox_inches="tight")
    plt.close()

    # --- Zastupljenost žanrova kroz dekade (stacked bar) ---
    genre_decade = pd.crosstab(corpus["decade"], corpus["genre"], normalize="index")
    genre_decade = genre_decade.reindex(ordered_decades)

    fig, ax = plt.subplots(figsize=(12, 6))
    genre_decade.plot(kind="bar", stacked=True, ax=ax, colormap="tab10")
    ax.set_title("Zastupljenost žanrova kroz dekade")
    ax.set_xlabel("Dekada")
    ax.set_ylabel("Udeo pesama")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "genre_by_decade.png", dpi=150)
    plt.close()

    print(f"\nSačuvano: sentiment_by_decade.png, mattr_by_decade.png, genre_by_decade.png u {FIGURES_DIR}")


if __name__ == "__main__":
    main()