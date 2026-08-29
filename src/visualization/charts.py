"""
src/visualization/charts.py

Grafovi trendova: sentiment po periodu, leksička raznovrsnost po periodu,
zastupljenost LDA tema (heatmap), poređenje gold standard vs. LLM.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

PERIOD_ORDER = ["sfrj", "tranzicija", "savremeno"]


def sentiment_trend_chart(sentiment_by_period_df: pd.DataFrame, output_path):
    """Stacked bar - udeo pozitivno/negativno/neutralno po periodu."""
    df = sentiment_by_period_df.reindex(PERIOD_ORDER)
    df = df.fillna(0)

    fig, ax = plt.subplots(figsize=(8, 5))
    df.plot(kind="bar", stacked=True, ax=ax,
            color={"pozitivno": "#4CAF50", "negativno": "#E53935", "neutralno": "#9E9E9E"})
    ax.set_title("Raspodela sentimenta po periodu")
    ax.set_xlabel("Period")
    ax.set_ylabel("Udeo pesama")
    ax.legend(title="Sentiment", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def lexical_diversity_chart(lexdiv_by_period_df: pd.DataFrame, output_path):
    """Bar chart poredi TTR i MATTR po periodu - namerno prikazuje OBA,
    da se vidi kontradikcija koju smo otkrile (TTR i MATTR daju suprotan
    zaključak o tome koji je period 'raznovrsniji')."""
    df = lexdiv_by_period_df.reindex(PERIOD_ORDER)

    fig, ax = plt.subplots(figsize=(8, 5))
    df[["ttr", "mattr"]].plot(kind="bar", ax=ax, color=["#90A4AE", "#1E88E5"])
    ax.set_title("Leksička raznovrsnost po periodu (TTR vs. MATTR)")
    ax.set_xlabel("Period")
    ax.set_ylabel("Vrednost")
    ax.legend(["TTR (osetljiv na dužinu)", "MATTR (pouzdaniji)"])
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def topic_heatmap(topic_by_group_df: pd.DataFrame, title: str, output_path, topic_labels: dict = None):
    """Heatmap zastupljenosti tema po periodu/žanru."""
    df = topic_by_group_df.copy()
    if topic_labels:
        df.index = [topic_labels.get(i, str(i)) for i in df.index]

    plt.figure(figsize=(max(8, len(df.columns) * 1.3), max(5, len(df) * 0.5)))
    sns.heatmap(df, annot=True, fmt=".2f", cmap="YlOrRd", cbar_kws={"label": "Udeo pesama"})
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def gold_vs_llm_theme_chart(comparison_df: pd.DataFrame, output_path):
    """Grupisan bar chart - raspodela tema po gold standardu naspram LLM-a,
    jedna pored druge za lako vizuelno poređenje."""
    gold_dist = comparison_df["gold_theme"].value_counts(normalize=True)
    llm_dist = comparison_df["llm_theme"].value_counts(normalize=True)

    combined = pd.DataFrame({"Gold standard (ljudi)": gold_dist, "LLM": llm_dist}).fillna(0)
    combined = combined.sort_values("Gold standard (ljudi)", ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    combined.plot(kind="bar", ax=ax, color=["#43A047", "#1E88E5"])
    ax.set_title("Raspodela tema: gold standard (ljudi) vs. LLM")
    ax.set_xlabel("Tema")
    ax.set_ylabel("Udeo pesama")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()