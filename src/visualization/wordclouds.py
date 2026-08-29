"""
src/visualization/wordclouds.py

Pravi word cloud slike iz TF-IDF izveštaja (Faza 4) - veličina reči
prati TF-IDF skor, ne prostu frekvenciju, pa vizuelno ističe reči
KARAKTERISTIČNE za tu grupu, ne samo najčešće uopšte.
"""

from wordcloud import WordCloud
import matplotlib
matplotlib.use("Agg")  # bez ovoga, matplotlib pokušava da otvori prozor - ne radi na serverima/skriptama
import matplotlib.pyplot as plt


def make_wordcloud(word_scores: dict, title: str, output_path):
    """Pravi i čuva jedan word cloud iz rečnika {reč: skor}."""
    wc = WordCloud(
        width=1000, height=500,
        background_color="white",
        colormap="viridis",
        max_words=40,
        prefer_horizontal=1.0,
    ).generate_from_frequencies(word_scores)

    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.title(title, fontsize=16)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()