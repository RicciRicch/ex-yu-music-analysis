import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

import pandas as pd
from src.preprocessing.clean_text import EKAVICA_RE, IJEKAVICA_RE

df = pd.read_csv('data/processed/corpus_clean.csv')
nepoznato = df[df['language'] == 'nepoznato'].copy()

def hits(text):
    text = str(text)
    e = len(EKAVICA_RE.findall(text))
    ij = len(IJEKAVICA_RE.findall(text))
    return e, ij

nepoznato[['e_hits', 'ij_hits']] = nepoznato['lyrics_clean'].apply(lambda t: pd.Series(hits(t)))

no_markers = ((nepoznato['e_hits'] == 0) & (nepoznato['ij_hits'] == 0)).sum()
real_ijekavica = (nepoznato['ij_hits'] > nepoznato['e_hits']).sum()
tie_nonzero = ((nepoznato['e_hits'] == nepoznato['ij_hits']) & (nepoznato['e_hits'] > 0)).sum()

print(f"Od {len(nepoznato)} 'nepoznato' pesama:")
print(f"  Nijedan marker pogođen (pravi 'ne znamo'): {no_markers}")
print(f"  Stvarno više ijekavica markera (hr/bs): {real_ijekavica}")
print(f"  Nerešeno neodlučeno (isti broj oba, >0): {tie_nonzero}")