import pandas as pd
import classla

df = pd.read_csv('data/processed/corpus_analysis_ready.csv')
nlp = classla.Pipeline('sr', processors='tokenize,ner', verbose=False)

# Pronađi prvu pesmu čiji tekst sadrži "Republike" ili slično - test na
# konkretnom, poznatom problematičnom primeru
for _, row in df.iterrows():
    text = str(row['lyrics_clean'])
    if 'epublik' in text.lower() or 'republik' in text.lower():
        print(f"ARTIST: {row['artist']} - {row['title']}")
        print()
        print("--- CEO TEKST (repr, da vidimo tačne karaktere/nove redove) ---")
        print(repr(text[:500]))
        print()
        print("--- NER ENTITETI ---")
        doc = nlp(text)
        for ent in doc.entities:
            print(repr(ent.text), '->', ent.type)
        break