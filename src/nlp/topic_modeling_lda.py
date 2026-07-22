"""
src/nlp/topic_modeling_lda.py

LDA (Latent Dirichlet Allocation) tematsko modelovanje preko gensim.

Trenira JEDAN model na celom korpusu - obezbeđuje da sve pesme dele isti
"prostor tema", pa je zastupljenost tema po periodu/žanru smisleno
uporediva (poseban model po grupi bi dao neuporedive teme).
"""

import warnings
warnings.filterwarnings("ignore")

from gensim import corpora
from gensim.models import LdaModel

from src.nlp.tfidf_keywords import SEMANTIC_STOPWORDS  # reuse iste stop liste


def build_corpus(texts, no_below: int = 5, no_above: float = 0.5):
    """Priprema gensim Dictionary i bag-of-words korpus iz liste tekstova
    (lema). no_below/no_above filtriraju retke i previše česte reči."""
    tokenized = [
        [w for w in text.split() if w not in SEMANTIC_STOPWORDS]
        for text in texts
    ]
    dictionary = corpora.Dictionary(tokenized)
    dictionary.filter_extremes(no_below=no_below, no_above=no_above)
    corpus = [dictionary.doc2bow(tokens) for tokens in tokenized]
    return dictionary, corpus, tokenized


def train_lda(corpus, dictionary, num_topics: int = 10, passes: int = 10, random_state: int = 42):
    return LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=num_topics,
        random_state=random_state,
        passes=passes,
    )


def get_dominant_topic(lda_model, dictionary, tokens):
    """Vraća (broj_teme, verovatnoća) za dominantnu temu jednog dokumenta.
    Ako je dokument prazan/nema poznatih reči, vraća (None, 0.0)."""
    bow = dictionary.doc2bow(tokens)
    if not bow:
        return None, 0.0
    topic_probs = lda_model.get_document_topics(bow)
    if not topic_probs:
        return None, 0.0
    return max(topic_probs, key=lambda x: x[1])