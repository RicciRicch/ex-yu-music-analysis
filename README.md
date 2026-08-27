# EX YU Music Analysis

Tehnička realizacija AI/NLP dela master rada za Veštačku inteligenciju:
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

> **Status**: Faza 1, 2 i 3 gotove. Faza 4 (NLP analiza) gotova - TF-IDF,
> leksička raznovrsnost, sentiment (leksikonski), LDA i BERTopic tematsko
> modelovanje, K-means klasterizacija. NER isključen zbog nekompatibilnosti
> verzija (vidi "Poznata ograničenja"). Sledeće: Faza 5 (LLM analiza).

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
- Otkriveno ~29 pesama na stranom jeziku (engleski, nemački) - verzije
  pesama snimane za strano tržište (npr. Zdravko Čolić, Dragana Mirković).
  Automatski izbačene iz analize-spremnog korpusa (manje od 10 lema posle
  lematizacije = pouzdan signal da nije ex-yu jezik).
- NER (imenovani entiteti) daje nepouzdane, isprekidane rezultate zbog
  neusklađenosti verzija - classla biblioteka je testirana sa torch 1.12.0,
  a dostupna verzija za Python 3.13 je torch 2.6.0+ (raskorak od ~3 godine
  razvoja). Kod za ekstrakciju entiteta je napisan i funkcionalan
  (src/nlp/run_ner.py), ali izlazni rezultati nisu pouzdani za analizu -
  NER je isključen iz finalnih nalaza rada. Downgrade torch-a nije moguć
  na Python 3.13 (nema kompatibilnih paketa ispod verzije 2.6.0).
