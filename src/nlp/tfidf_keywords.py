"""
src/nlp/tfidf_keywords.py

TF-IDF analiza ključnih reči po periodu i žanru.

Pristup: svaki period (i odvojeno, svaki žanr) tretiramo kao JEDAN
"dokument" (spajamo leme svih pesama u toj grupi u jedan veliki tekst).
TF-IDF preko ovih grupnih "dokumenata" otkriva koje reči su
KARAKTERISTIČNE za tu grupu (česte unutra, retke van nje).

NAPOMENA: sa samo 3 (period) ili 8 (žanr) grupa, IDF ima grublju
rezoluciju nego u tipičnoj TF-IDF primeni sa mnogo dokumenata - očekuj
da se neke opšte česte reči (npr. "ljubav") i dalje pojave, samo niže
rangirane. Ovo je poznato ograničenje pristupa, ne greška.
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# Semantička stop lista - gramatički su glagoli/prilozi (POS filter ih
# propušta kao "sadržajne"), ali su toliko opšti i učestali da nose
# gotovo nikakvo tematsko značenje (modalni/pomoćni glagoli, opšti
# kvantifikatori). Bez ove liste, dominiraju TF-IDF rezultatima u svakoj
# grupi podjednako, gušeći prave karakteristične reči.
SEMANTIC_STOPWORDS = [
    "sav", "sva", "svo", "svi", "samo", "kad", "kada", "još", "sad", "sada",
    "moći", "hteti", "morati", "trebati", "imati", "znati", "dati", "biti",
]

def top_keywords_by_group(
    df: pd.DataFrame,
    group_col: str,
    text_col: str = "lemmas",
    top_n: int = 20,
) -> dict:
    """Vraća dict {grupa: [(reč, tfidf_skor), ...]} - top_n karakterističnih
    reči za svaku vrednost u group_col (npr. za svaki period ili žanr)."""
    grouped = (
        df.groupby(group_col)[text_col]
        .apply(lambda texts: ' '.join(texts.fillna('')))
        .reset_index()
    )

    vectorizer = TfidfVectorizer(max_features=5000, min_df=1, stop_words=SEMANTIC_STOPWORDS)
    tfidf_matrix = vectorizer.fit_transform(grouped[text_col])
    feature_names = vectorizer.get_feature_names_out()

    results = {}
    for i, group_name in enumerate(grouped[group_col]):
        row = tfidf_matrix[i].toarray().flatten()
        top_indices = row.argsort()[::-1][:top_n]
        results[group_name] = [
            (feature_names[idx], round(float(row[idx]), 4))
            for idx in top_indices if row[idx] > 0
        ]
    return results