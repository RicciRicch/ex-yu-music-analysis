"""
src/nlp/embeddings_topics.py

BERTopic tematsko modelovanje i K-means klasterizacija na BERT
embeddings-ima (elaborat 4.3).

Za razliku od LDA (koji koristi leme, bag-of-words), ovde koristimo
lyrics_clean (prirodan tekst) - sentence-transformers modeli su
trenirani na prirodnom jeziku i gube na kvalitetu ako im se da
lematizovana "vreća reči" bez gramatičke strukture.
"""

import warnings
warnings.filterwarnings("ignore")

from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer

# Lista srpskih stop reči za IMENOVANJE tema u BERTopic-u (ne utiče na
# samu klasterizaciju - ta se radi na embeddings-ima, ovo utiče samo na
# to koje reči predstavljaju temu kad je čitamo).
SERBIAN_STOPWORDS = [
    "ja", "mene", "meni", "mnom", "mnome", "me",
    "ti", "tebe", "tebi", "tobom", "te",
    "on", "ona", "ono", "njega", "njemu", "njim", "njoj", "nju", "njom", "njome",
    "mi", "nas", "nama", "vi", "vas", "vama", "oni", "one", "njih", "njima",
    "se", "sebe", "sebi", "sobom", "ga", "ju", "ih", "mu", "joj", "im",
    "moj", "moja", "moje", "moji", "mog", "moga", "mome", "mojoj", "mojim",
    "tvoj", "tvoja", "tvoje", "tvoji", "tvog", "tvoga", "tvome", "tvojoj", "tvojim",
    "njegov", "njegova", "njegovo", "njen", "njena", "njeno",
    "naš", "nasa", "naša", "naše", "naši", "vaš", "vaša", "vaše", "vaši",
    "njihov", "njihova", "njihovo",
    "ovaj", "ova", "ovo", "ovi", "ove", "taj", "ta", "to", "te", "onaj", "ono",
    "ko", "koga", "kome", "kim", "koji", "koja", "koje", "što", "sto", "sta", "šta",
    "i", "a", "ali", "pa", "ili", "nego", "već", "vec", "jer", "da", "kao", "dok",
    "kad", "kada", "gde", "gdje", "još", "jos", "samo", "li", "ne", "ni", "niti",
    "sve", "svi", "sva", "svo",
    "u", "o", "s", "sa", "iz", "do", "za", "po", "pod", "nad", "pred", "kroz",
    "oko", "bez", "prema", "ka", "od", "na", "kod", "među", "medju", "uz",
    "je", "sam", "si", "smo", "ste", "su", "bio", "bila", "bilo", "bili", "bile",
    "biti", "bi", "budem", "budeš", "bude", "budemo", "budete", "budu",
    "nisam", "nisi", "nije", "nismo", "niste", "nisu",
    "tu", "tamo", "ovde", "ovdje", "onde", "sad", "sada", "opet",
]

EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def load_embedding_model():
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def compute_embeddings(model, texts, show_progress=True):
    return model.encode(texts, show_progress_bar=show_progress)


def run_bertopic(texts, embeddings, embedding_model, min_topic_size=15):
    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0,
                       metric='cosine', random_state=42)
    hdbscan_model = HDBSCAN(min_cluster_size=min_topic_size, metric='euclidean',
                             cluster_selection_method='eom', prediction_data=True)
    vectorizer_model = CountVectorizer(stop_words=SERBIAN_STOPWORDS, min_df=2)

    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer_model,
        language="multilingual",
        calculate_probabilities=False,
        verbose=True,
    )
    topics, _ = topic_model.fit_transform(texts, embeddings)
    return topic_model, topics


def run_kmeans(embeddings, n_clusters=10, random_state=42):
    """K-means direktno na embeddings-ima - odvojeno od BERTopic-ovog
    internog HDBSCAN-a, kao dopunska/uporedna metoda klasterizacije."""
    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = km.fit_predict(embeddings)
    return labels