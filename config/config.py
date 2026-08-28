"""
Centralna konfiguracija za EX YU Music Analysis projekat.

Ovde se definišu:
- vremenski periodi (u skladu sa elaboratom master rada)
- žanrovi koje pratimo
- putanje do foldera sa podacima
- podešavanja za LLM API pozive

Svi ostali moduli (scraping, preprocessing, nlp, llm) uvoze
podatke odavde, umesto da hardkoduju vrednosti po fajlovima.
To znači: ako promeniš granicu perioda ili dodaš žanr, menjaš
SAMO ovaj fajl.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Putanje
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
GOLD_STANDARD_DIR = DATA_DIR / "gold_standard"

RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
REPORTS_DIR = RESULTS_DIR / "reports"

# ---------------------------------------------------------------------------
# Istorijski periodi (iz elaborata, poglavlje 2.1 / 4.6)
# ---------------------------------------------------------------------------
# Format: naziv_perioda -> (prva_godina, poslednja_godina) - oba inkluzivno.
# Ove granice se koriste za automatsko svrstavanje pesme u period na
# osnovu godine izdavanja.
PERIODS = {
    "sfrj": (1960, 1991),
    "tranzicija": (1991, 2005),
    "savremeno": (2005, 2025),
}

PERIOD_LABELS_SR = {
    "sfrj": "SFRJ (1960–1991)",
    "tranzicija": "Tranzicioni period (1991–2005)",
    "savremeno": "Savremeni period (2005–danas)",
}


def get_period(year: int) -> str:
    """Vraća naziv perioda ('sfrj' / 'tranzicija' / 'savremeno') za datu godinu.

    Granične godine (1991, 2005) pripisujemo mlađem periodu, jer u
    elaboratu obe granice figurišu kao početak sledeće faze
    (npr. 1991 = raspad SFRJ = početak tranzicije).
    """
    if year is None:
        return "nepoznato"
    if year < 1991:
        return "sfrj"
    if year < 2005:
        return "tranzicija"
    return "savremeno"


def get_decade(year: int) -> str:
    """Vraća dekadu u formatu '1980s', '1990s', itd. Korisno za finiju
    granulaciju analize unutar velikih perioda (npr. razlika 2005-2012
    vs 2013-2025 unutar 'savremenog' perioda)."""
    if year is None:
        return "nepoznato"
    decade_start = (year // 10) * 10
    return f"{decade_start}s"


# ---------------------------------------------------------------------------
# Žanrovi
# ---------------------------------------------------------------------------
# Kontrolisana lista - scraping/anotacija treba da mapira sirove žanr
# oznake sa sajtova na ove kanonske vrednosti (vidi src/preprocessing).
GENRES = [
    "rok",
    "pop",
    "novi_talas",
    "narodna_narodnjacka",
    "turbo_folk",
    "hip_hop_rep",
    "trep",
    "ostalo",
]

GENRE_LABELS_SR = {
    "rok": "Rok",
    "pop": "Pop",
    "novi_talas": "Novi talas",
    "narodna_narodnjacka": "Narodna / Narodnjačka",
    "turbo_folk": "Turbo-folk",
    "hip_hop_rep": "Hip-hop / Rep",
    "trep": "Trep",
    "ostalo": "Ostalo",
}

# ---------------------------------------------------------------------------
# Dataset schema - kanonske kolone koje SVAKI zapis u finalnom
# datasetu mora imati (vidi src/utils/schema.py za detaljniju validaciju)
# ---------------------------------------------------------------------------
DATASET_COLUMNS = [
    "song_id",       # str, unique - hash od (artist, title)
    "title",         # str
    "artist",        # str
    "year",          # int ili None ako nepoznato
    "period",        # str - jedno od PERIODS.keys(), izvedeno iz year
    "decade",        # str - npr. "1990s", izvedeno iz year
    "genre",         # str - jedno od GENRES
    "language",      # str - "sr" / "hr" / "bs" / "sl" / "nepoznato"
    "country",       # str - zemlja porekla izvođača (opciono)
    "lyrics_raw",    # str - sirov tekst pesme (pre čišćenja)
    "lyrics_clean",  # str - očišćen/normalizovan tekst (popunjava preprocessing)
    "source_site",   # str - odakle je tekst preuzet (npr. "genius")
    "source_url",    # str - link ka izvoru (za proveru/atribuciju)
    "scraped_at",    # str (ISO datetime) - kad je zapis prikupljen
]

# ---------------------------------------------------------------------------
# LLM podešavanja (Claude Anthropic)
# ---------------------------------------------------------------------------
LLM_PROVIDER = "anthropic"
LLM_MODEL = "claude-haiku-4-5-20251001"  # brz i jeftin za analizu velikog broja pesama
LLM_MAX_TOKENS = 1024
LLM_TEMPERATURE = 0.0             # determinističke klasifikacije, ne kreativno pisanje

# Koliko pesama šaljemo u jednom API pozivu (batch) - videćemo u Fazi 4
# da li je isplativije 1-po-1 sa strogim JSON izlazom ili batch prompt.
LLM_BATCH_SIZE = 1

# ---------------------------------------------------------------------------
# Scraping podešavanja
# ---------------------------------------------------------------------------
REQUEST_TIMEOUT_SECONDS = 15
REQUEST_DELAY_SECONDS = 1.5   # pauza između zahteva - poštovanje servera
USER_AGENT = "Mozilla/5.0 (research bot - master rad FON, kontakt: <tvoj-mejl>)"

MIN_CORPUS_SIZE = 3000        # ciljna veličina korpusa iz elaborata
GOLD_STANDARD_SIZE = 300      # veličina ručno anotiranog uzorka
BASE_URL = "https://tekstovi-pjesama.com"
MAX_RETRIES = 3
