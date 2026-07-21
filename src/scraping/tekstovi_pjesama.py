"""
src/scraping/tekstovi_pjesama.py

Scraper za tekstovi-pjesama.com.

Zašto sajt uopšte treba da pogodimo iz imena: stranica izvođača na tekstovi-pjesama.com
izgleda ovako: https://tekstovi-pjesama.com/autor/{slug}/. Da bismo stigli do te
stranice, moramo pretvoriti "Riblja Čorba" u "riblja-corba" — malim slovima, bez
razmaka i kvačica, spojeno crticom. To rade skoro svi sajtovi (WordPress, koji
ovaj sajt koristi, radi to automatski za svaki naslov).

"""

from __future__ import annotations
from config.config import USER_AGENT
from bs4 import BeautifulSoup
from config.config import BASE_URL, MAX_RETRIES, REQUEST_DELAY_SECONDS, REQUEST_TIMEOUT_SECONDS


import re
import unicodedata
import requests
import time

# đ namerno ide u "dj" (ne samo "d") - tako se najčešće transliterira
# na ex-yu sajtovima (npr. "Đurđevdan" -> "djurdjevdan")
DIACRITIC_MAP = {
    "č": "c", "ć": "c", "š": "s", "ž": "z", "đ": "dj",
    "Č": "C", "Ć": "C", "Š": "S", "Ž": "Z", "Đ": "Dj",
}


def slugify_sr(text: str) -> str:
    """Pretvara naslov/ime u WordPress-style slug (najbolji pokušaj)."""
    for src, dst in DIACRITIC_MAP.items():
        text = text.replace(src, dst)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[’'`]", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    text = re.sub(r"-{2,}", "-", text)
    return text


def make_session() -> requests.Session:
    """Pravi jednu requests.Session koja se ponovo koristi za sve pozive -
    brže je od pravljenja nove konekcije za svaki zahtev, i ovde
    podešavamo User-Agent (bez njega neki sajtovi vraćaju 403 Forbidden)."""
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    return session

def _get(session: requests.Session, url: str) -> BeautifulSoup | None:
    """Zajednička GET + parse logika sa retry i pauzom između pokušaja."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
            if resp.status_code == 200:
                time.sleep(REQUEST_DELAY_SECONDS)
                return BeautifulSoup(resp.text, "lxml")
            if resp.status_code == 404:
                return None  # stranica sigurno ne postoji, nema smisla retry
        except requests.RequestException:
            pass
        time.sleep(REQUEST_DELAY_SECONDS * attempt)  # sačekaj duže na svaki sledeći pokušaj
    return None

def resolve_artist_url(session: requests.Session, artist_name: str) -> str | None:
    """Pretvara ime izvođača u URL njegove stranice, uz proveru da
    stranica stvarno postoji (GET vraća 200, a ne 404)."""
    slug = slugify_sr(artist_name)
    url = f"{BASE_URL}/autor/{slug}/"
    soup = _get(session, url)
    return url if soup is not None else None

def get_artist_songs(session: requests.Session, artist_url: str) -> list[tuple[str, str]]:
    """Vraća listu (naziv_pesme, url_pesme) sa stranice izvođača.

    VAŽNO: pretragu linkova ograničavamo na deo stranice IZMEĐU naslova
    "Popis pjesama" i sledećeg naslova (h1-h4) - jer sajt ima globalni
    sidebar vidžet "Zadnji dodani tekstovi" koji se pojavljuje na SVAKOJ
    stranici i sadrži linkove ka pesmama SASVIM DRUGIH izvođača. Ako bismo
    pretraživali celu stranicu, ti tuđi linkovi bi se pomešali sa pravom
    listom pesama ovog izvođača.
    """
    soup = _get(session, artist_url)
    if soup is None:
        return []

    heading = soup.find(
        lambda tag: tag.name in ("h1", "h2", "h3", "h4")
        and "popis pjesama" in tag.get_text(strip=True).lower()
    )

    songs = []
    seen = set()

    if heading is None:
        # Fallback ako se sajt promeni pa naslov "Popis pjesama" nestane -
        # bolje nešto (uz rizik kontaminacije) nego ništa, ali ovo bi
        # trebalo da se retko/nikad desi.
        candidates = soup.find_all("a", href=re.compile(r"/pjesma/[^/]+/?$"))
    else:
        candidates = []
        for element in heading.find_all_next():
            if element.name in ("h1", "h2", "h3", "h4"):
                break  # sledeći naslov = izašli smo iz liste pesama ovog izvođača
            if element.name == "a":
                candidates.append(element)

    for a in candidates:
        href = a.get("href", "")
        if not isinstance(href, str):
            continue
        if not re.search(r"/pjesma/[^/]+/?$", href):
            continue
        title = a.get_text(strip=True)
        if not href or not title or href in seen:
            continue
        seen.add(href)
        songs.append((title, href))

    return songs

def scrape_song(session: requests.Session, song_url: str) -> dict | None:
    """Skida i parsira jednu stranicu pesme.

    Vraća dict sa title/artist/lyrics_raw/source_url, ili None ako nešto
    ne uspe - pozivalac to beleži u problem_log.csv umesto da ceo scraping
    padne zbog jedne problematične pesme.
    """
    soup = _get(session, song_url)
    if soup is None:
        return None

    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else None

    artist = None
    artist_link = soup.find("a", href=re.compile(r"/autor/[^/]+/?$"))
    if artist_link:
        artist = artist_link.get_text(strip=True)

    lyrics_raw = _extract_lyrics(soup)

    if not lyrics_raw or len(lyrics_raw.split()) < 10:
        return None  # verovatno pogrešan selektor ili prazna/nepotpuna stranica

    return {
        "title": title,
        "artist": artist,
        "lyrics_raw": lyrics_raw,
        "source_url": song_url,
    }


def _extract_lyrics(soup: BeautifulSoup) -> str | None:
    """Pokušava nekoliko strategija da izvuče tekst pesme, od najpreciznije
    ka najgrubljoj - ne znamo tačnu CSS klasu bez pregleda izvorne strukture,
    pa probamo tipične WordPress selektore, a onda fallback na ceo <article>."""
    for selector in ["div.entry-content", "div.post-content", "article .entry-content"]:
        node = soup.select_one(selector)
        if node:
            text = _clean_lyrics_text(node)
            text = _strip_post_meta(text)
            if text and len(text.split()) >= 10:
                return text

    article = soup.find("article")
    if article:
        text = _clean_lyrics_text(article)
        text = _strip_post_meta(text)
        if text and len(text.split()) >= 10:
            return text

    return None


def _clean_lyrics_text(node) -> str:
    """Uzima tekst iz HTML čvora i čisti ga od svega što NIJE tekst pesme
    (navigacija, komentari, sidebar sa 'Latest posts')."""
    for junk in node.select("nav, aside, .comments, .comment-respond, script, style"):
        junk.decompose()

    text = node.get_text(separator="\n", strip=True)

    for marker in ["Latest posts", "Novosti", "Zadnji dodani tekstovi", "Brzi linkovi"]:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]

    return text.strip()

_DATE_LINE_RE = re.compile(r"^\d{1,2}\.\s+\S+\s+\d{4}\.?$")


def _strip_post_meta(text: str) -> str:
    """Uklanja 'šum' sa početka teksta - naslov, 'Izvođač:', ime izvođača,
    korisničko ime koje je pesmu okačilo, datum, broj pregleda i komentara.

    Ovi elementi UVEK prethode pravom tekstu pesme, istim redosledom, pa ih
    prepoznajemo po datumu (uvek u obliku '5. srpnja 2024.') i brojevima
    odmah posle njega (pregledi, komentari) - sve pre tog datuma odbacujemo.
    """
    lines = text.split("\n")

    date_idx = None
    for i, line in enumerate(lines):
        if _DATE_LINE_RE.match(line.strip()):
            date_idx = i
            break

    if date_idx is None:
        return text  # obrazac nije prepoznat - ne diramo tekst, bezbednije je

    start = date_idx + 1
    digits_skipped = 0
    while start < len(lines) and lines[start].strip().isdigit() and digits_skipped < 3:
        start += 1
        digits_skipped += 1

    return "\n".join(lines[start:]).strip()