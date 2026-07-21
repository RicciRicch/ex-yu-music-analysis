import pandas as pd

df = pd.read_csv('data/raw/problem_log_full.csv')
print('Ukupno problema:', len(df))
print()

def categorize(razlog):
    if 'napomena' in razlog:
        return 'napomena (neslaganje imena)'
    if 'nije pronađen' in razlog:
        return 'izvođač nije pronađen'
    if 'nema pronađenih' in razlog:
        return 'nema pesama'
    return 'parsiranje nije uspelo'

df['kategorija'] = df['razlog'].apply(categorize)
print('Po tipu:')
print(df['kategorija'].value_counts())
print()
print('--- Sve napomene (neslaganje imena) - OVO NAJVIŠE PROVERITI ---')
for _, row in df[df['kategorija'] == 'napomena (neslaganje imena)'].iterrows():
    print(f"{row['artist']}: {row['razlog']}")
print()
print('--- Izvođači koji nisu nađeni ---')
print(df[df['kategorija'] == 'izvođač nije pronađen']['artist'].tolist())
print()
print('--- Izvođači bez ijedne pesme (nađeni, ali prazna lista) ---')
print(df[df['kategorija'] == 'nema pesama']['artist'].tolist())

print()
print('--- Parsiranje nije uspelo - po izvođaču ---')
parse_fails = df[df['kategorija'] == 'parsiranje nije uspelo']
print(parse_fails['artist'].value_counts())
print()
print('--- Prvih 10 primera (naslov + url) ---')
print(parse_fails[['artist', 'song_title', 'url']].head(10).to_string(index=False))