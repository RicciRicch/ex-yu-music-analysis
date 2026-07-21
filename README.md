# EX YU Music Analysis

Tehnička realizacija AI/NLP dela master rada:
**"Analiza podataka u promeni trendova u EX YU muzici pomoću LLM modela"**
(Univerzitet u Beogradu, Fakultet organizacionih nauka)

Projekat analizira tematske, lingvističke i vrednosne transformacije u
tekstovima EX YU popularne muzike kroz tri istorijska perioda:

| Period | Godine |
|---|---|
| SFRJ | 1960–1991 |
| Tranzicija | 1991–2005 |
| Savremeno | 2005–danas |

koristeći kombinaciju klasičnih NLP metoda (tematsko modelovanje, sentiment
analiza, NER) i LLM analize (Claude API) za dublju interpretaciju sadržaja.

> **Status**: Faza 1 (priprema projekta) gotova. Faza 2 (prikupljanje
> korpusa) suštinski gotova — 4113 pesama, 104 izvođača, tri perioda,
> 8 žanrova. Vidi "Poznata ograničenja" ispod za otvorena pitanja.

## Struktura projekta

```
ex-yu-music-analysis/
├── config/
│   └── config.py          # periodi, žanrovi, putanje, LLM/scraping podešavanja
├── data/
│   ├── raw/                # sirovo prikupljeni tekstovi (NIJE na GitHub-u)
│   ├── processed/          # očišćen dataset (NIJE na GitHub-u)
│   └── gold_standard/      # ručno anotiran uzorak za validaciju
├── src/
│   ├── scraping/           # prikupljanje tekstova sa lyrics sajtova
│   ├── preprocessing/      # čišćenje, normalizacija, lematizacija
│   ├── nlp/                # tematsko modelovanje, sentiment, NER, TF-IDF
│   ├── llm/                # Claude API analiza + prompt šabloni
│   ├── visualization/      # grafikoni, word cloud-ovi
│   └── utils/              # zajedničke pomoćne funkcije (schema, itd.)
├── notebooks/               # Jupyter notebook-ovi sa analizom
├── results/
│   ├── figures/             # generisani grafikoni
│   └── reports/             # tabele/izveštaji sa rezultatima
└── tests/
```

## Instalacija

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
cp .env.example .env          # pa upiši svoj ANTHROPIC_API_KEY
```

## Zašto sirovi tekstovi pesama nisu na GitHub-u

Tekstovi pesama su autorski zaštićeni. Na GitHub ide kod, metapodaci
(izvođač/godina/žanr) i agregovani rezultati analize, nikad sam tekst pesme.

## Poznata ograničenja (stanje: Faza 2)

- **Trep žanr je slabo zastupljen** (8 pesama od 4113 u korpusu). Glavni izvor
  (tekstovi-pjesama.com) gotovo da nema trep izvođače (Coby, Voyage, Jala Brat,
  Buba Corelli, Nucci nisu pronađeni). Genius.com proveren i odbačen (nema
  regionalnu pokrivenost). lyricstranslate.com ima sadržaj, ali blokira
  automatizovane zahteve (bot detection) - potrebno rešiti pre eventualnog
  korišćenja. **Odloženo za kasniju fazu**, dokumentovano kao ograničenje u
  skladu sa metodologijom iz elaborata (4.6).
- Nekoliko poznatih SFRJ rok/novi-talas izvođača takođe nije na glavnom izvoru
  (Riblja Čorba, Šarlo Akrobata, Film, Bajaga i Instruktori i dr.) - isti uzrok.
