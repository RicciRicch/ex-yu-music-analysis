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

> **Status**: Faze 1-6 gotove - ceo pipeline kompletan. Prikupljanje
> (4113 pesama) → preprocessing (4084 spremno) → NLP analiza (TF-IDF,
> LDA, BERTopic, sentiment, leksička raznovrsnost) → LLM validacija
> (gold standard n=299, Cohen's kappa: tema=0.405, emocija=0.356) →
> vizualizacije (word cloud-ovi, grafovi trendova, heatmap-e, dekadni
> prikazi). Interaktivan pregled svih nalaza:
> `notebooks/finalni_pregled.ipynb`. Detaljna dokumentacija u `docs/`.

## Struktura projekta

```
ex-yu-music-analysis/
├── config/
│   └── config.py          # periodi, žanrovi, putanje, LLM/scraping podešavanja
├── data/
│   ├── raw/                # sirovo prikupljeni tekstovi (NIJE na GitHub-u)
│   ├── processed/          # očišćen dataset (NIJE na GitHub-u)
│   └── gold_standard/      # ručno anotiran uzorak za validaciju
├── docs/
│   ├── napredak_projekta.md    # detaljan pregled napretka kroz sve faze
│   └── obrasci_neslaganja.md   # analiza obrazaca LLM/gold standard neslaganja
├── src/
│   ├── scraping/           # prikupljanje tekstova sa lyrics sajtova
│   ├── preprocessing/      # čišćenje, normalizacija, lematizacija
│   ├── nlp/                # tematsko modelovanje, sentiment, NER, TF-IDF
│   ├── llm/                # Claude API analiza + prompt šabloni
│   ├── visualization/      # grafikoni, word cloud-ovi
│   └── utils/              # zajedničke pomoćne funkcije (schema, itd.)
├── notebooks/               # Jupyter notebook-ovi sa analizom
│   └── finalni_pregled.ipynb   # interaktivan pregled svih nalaza za odbranu
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

## Poznata ograničenja (stanje: Faza 5)

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
- Google Gemini besplatan API nivo se pokazao znatno ograničeniji od
  dokumentovanog (~20 zahteva/dan umesto ~1.500, promena krajem 2025) -
  napravljen prelazak na Anthropic Claude API (plaćen, ali jeftin za ovaj
  obim, ~$0.50).
- LLM klasifikacija (tema/emocija/vrednosti) sprovedena na gold standard
  uzorku (n=299), ne celom korpusu (n=4084) - metodološka odluka: isti
  uzorak služi i za validaciju, izbegava se nepotreban trošak/vreme na
  celom korpusu bez merljive dobiti u pouzdanosti nalaza.
- LLM klasifikacija pokazuje sistematsku pristrasnost ka dominantnim
  kategorijama i slabije prepoznaje žanrovski/kulturno specifične
  nijanse (satira, narodnjačka konvencija izražavanja, hedonizam vs.
  ljubav) - detaljno dokumentovano u `docs/obrasci_neslaganja.md`.
- Analiza po DEKADAMA treba se tumačiti sa oprezom - decade kolona je
  izvedena iz jedne procenjene godine po izvođaču, ne stvarne godine
  svake pesme, pa pojedine dekade (posebno 2000s, n=271) imaju
  neujednačen žanrovski sastav koji može izgledati kao "trend" a
  zapravo je posledica uzorkovanja (videti napomenu na
  results/figures/mattr_by_decade.png).
