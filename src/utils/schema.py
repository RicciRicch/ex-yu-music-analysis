"""
Pomoćne funkcije oko dataset šeme.

Ideja: svaki scraper (Genius, Tekstovi-pesama, ...) na kraju treba da
proizvede listu Python dict-ova koji odgovaraju DATASET_COLUMNS iz
config-a. Ove funkcije to olakšavaju i standardizuju - tako da nam
je svejedno odakle je pesma došla, dataframe je uvek isti oblik.
"""

import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from config.config import DATASET_COLUMNS, get_decade, get_period


def make_song_id(artist: str, title: str) -> str:
    """Generiše stabilan, jedinstven ID za pesmu na osnovu izvođača i naslova.

    Koristimo hash umesto redovnog brojača zato što više scraper-a
    (Genius, Tekstovi-pesama...) može pokupiti istu pesmu - želimo da
    se ta dva zapisa kasnije lako prepoznaju kao duplikat (isti song_id).
    """
    normalized = re.sub(r"\s+", " ", f"{artist.strip().lower()}|{title.strip().lower()}")
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()[:12]


def build_record(
    title: str,
    artist: str,
    year: Optional[int],
    genre: str,
    lyrics_raw: str,
    source_site: str,
    source_url: str,
    language: str = "nepoznato",
    country: str = "nepoznato",
) -> dict:
    """Pravi jedan standardizovan zapis pesme (dict) u skladu sa DATASET_COLUMNS.

    lyrics_clean namerno ostavljamo prazno ovde - to je posao
    preprocessing faze (Faza 2), ne scraping-a. Scraping treba samo
    da sakupi sirove podatke, bez logike čišćenja/analize.
    """
    return {
        "song_id": make_song_id(artist, title),
        "title": title.strip(),
        "artist": artist.strip(),
        "year": year,
        "period": get_period(year) if year else "nepoznato",
        "decade": get_decade(year) if year else "nepoznato",
        "genre": genre,
        "language": language,
        "country": country,
        "lyrics_raw": lyrics_raw,
        "lyrics_clean": "",
        "source_site": source_site,
        "source_url": source_url,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }


def empty_dataset() -> pd.DataFrame:
    """Vraća prazan DataFrame sa tačno definisanim kolonama i redosledom."""
    return pd.DataFrame(columns=DATASET_COLUMNS)


def validate_dataset(df: pd.DataFrame) -> list[str]:
    """Vraća listu problema u datasetu (prazna lista = sve OK).

    Namerno ne baca exception - u fazi prikupljanja je normalno da
    ima nedostataka (npr. nepoznata godina), samo želimo da ih vidimo.
    """
    issues = []

    missing_cols = set(DATASET_COLUMNS) - set(df.columns)
    if missing_cols:
        issues.append(f"Nedostaju kolone: {missing_cols}")

    if "song_id" in df.columns:
        dupes = df["song_id"].duplicated().sum()
        if dupes:
            issues.append(f"Broj duplikata (isti song_id): {dupes}")

    if "lyrics_raw" in df.columns:
        empty_lyrics = df["lyrics_raw"].isna().sum() + (df["lyrics_raw"] == "").sum()
        if empty_lyrics:
            issues.append(f"Broj zapisa bez teksta pesme: {empty_lyrics}")

    if "year" in df.columns:
        missing_year = df["year"].isna().sum()
        if missing_year:
            issues.append(f"Broj zapisa bez godine (nije moguće odrediti period): {missing_year}")

    return issues
