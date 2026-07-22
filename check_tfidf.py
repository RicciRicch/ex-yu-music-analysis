import pandas as pd

df = pd.read_csv('results/reports/tfidf_top_reci_genre.csv')
for genre in df['grupa'].unique():
    subset = df[(df['grupa'] == genre) & (df['rang'] > 10) & (df['rang'] <= 20)]
    words = ', '.join(subset['rec'])
    print(f"{genre}: {words}")