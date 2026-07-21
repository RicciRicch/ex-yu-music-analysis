"""
Smoke-test scraping skripta za Fazu 2.

Šta radi:
    1. Učitava data/artist_seed_list.csv (mala test lista od 8 izvođača)
    2. Za svakog: nalazi stranicu izvođača, uzima prvih par pesama
    3. Skida tekst svake pesme i pravi standardizovan zapis (schema.build_record)
    4. Čuva sve u data/raw/test_corpus.csv
    5. Beleži probleme (šta i zašto nije uspelo) u data/raw/problem_log.csv

Pokretanje (iz root foldera projekta):
    python src/scraping/run_test_scrape.py
"""

import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.config import RAW_DATA_DIR
from src.scraping.tekstovi_pjesama import (
    get_artist_songs,
    make_session,
    resolve_artist_url,
    scrape_song,
)
from src.utils.schema import build_record, empty_dataset, validate_dataset

MAX_SONGS_PER_ARTIST = 5
SEED_LIST_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "artist_seed_list.csv"
OUTPUT_PATH = RAW_DATA_DIR / "test_corpus.csv"
PROBLEM_LOG_PATH = RAW_DATA_DIR / "problem_log.csv"

def _artist_mismatch_note(expected_artist: str, scraped_artist: str | None) -> str | None:
    """Vraća napomenu ako se ime izvođača koje smo TRAŽILE razlikuje od
    imena koje je SAM SAJT vratio za tu pesmu - NE blokira unos u korpus
    (podatak ostaje), samo ga označava za ručnu proveru. Ovo hvata slučajeve
    kolizije imena (npr. "Azra" bend vs. "Azra Polumenta" pevačica) a da
    pritom ne baca dobre podatke kad je razlika bezazlena (npr. mala/velika
    slova, "Bijelo Dugme" vs "Bijelo dugme")."""
    if not scraped_artist:
        return None
    if expected_artist.strip().lower() == scraped_artist.strip().lower():
        return None
    return f"napomena: tražen izvođač '{expected_artist}', sajt vraća '{scraped_artist}' - proveri ručno"

def main():
    seed_df = pd.read_csv(SEED_LIST_PATH)
    session = make_session()

    records = []
    problems = []  # (artist, song_title_or_prazno, url_or_prazno, razlog)

    for _, row in tqdm(seed_df.iterrows(), total=len(seed_df), desc="Izvođači"):
        artist_name = row["artist_name"]
        genre = row["genre"]
        year = int(row["approx_year"])

        artist_url = resolve_artist_url(session, artist_name)
        if artist_url is None:
            problems.append((artist_name, "", "", "izvođač nije pronađen na sajtu"))
            continue

        songs = get_artist_songs(session, artist_url)
        print(f"  {artist_name}: {len(songs)} pesama pronađeno")
        if not songs:
            problems.append((artist_name, "", artist_url, "nema pronađenih pesama"))
            continue

        for title, song_url in songs[:MAX_SONGS_PER_ARTIST]:
            result = scrape_song(session, song_url)
            if result is None:
                problems.append((artist_name, title, song_url, "parsiranje teksta nije uspelo"))
                continue

            record = build_record(
                title=result["title"] or title,
                artist=result["artist"] or artist_name,
                year=year,
                genre=genre,
                lyrics_raw=result["lyrics_raw"],
                source_site="tekstovi-pjesama.com",
                source_url=song_url,
            )
            records.append(record)

            note = _artist_mismatch_note(artist_name, result["artist"])
            if note:
                problems.append((artist_name, result["title"] or title, song_url, note))

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(records) if records else empty_dataset()
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    problems_df = pd.DataFrame(problems, columns=["artist", "song_title", "url", "razlog"])
    problems_df.to_csv(PROBLEM_LOG_PATH, index=False, encoding="utf-8")

    print(f"\nGotovo. Prikupljeno {len(df)} pesama od {seed_df['artist_name'].nunique()} izvođača.")
    print(f"Sačuvano u: {OUTPUT_PATH}")
    if len(problems_df):
        print(f"Zabeleženo {len(problems_df)} problema u: {PROBLEM_LOG_PATH}")

    if len(df):
        issues = validate_dataset(df)
        if issues:
            print("\nUpozorenja o kvalitetu podataka:")
            for issue in issues:
                print(f"  - {issue}")
        print("\nPregled po periodu:")
        print(df["period"].value_counts())


if __name__ == "__main__":
    main()