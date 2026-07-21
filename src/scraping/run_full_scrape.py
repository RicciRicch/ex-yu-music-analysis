"""
src/scraping/run_full_scrape.py

Pravi (ne test) scraping - prolazi kroz PUNU listu izvođača
(data/full_artist_list.csv) i skida SVE pesme za svakog (bez veštačkog
ograničenja po elaboratu 4.2 - balans se postiže kasnijim semplovanjem,
ne ograničavanjem prikupljanja).

Pokretanje (iz root foldera projekta):
    python src/scraping/run_full_scrape.py

NAPOMENA O VREMENU: sa ~106 izvođača i pauzom od 1.5s između zahteva,
ovo može potrajati 20-60+ minuta u zavisnosti od toga koliko pesama
svaki izvođač ima na sajtu. Normalno je da traje dugo - ne prekidaj
usred rada, skripta čuva sve na kraju odjednom.
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

# Sigurnosna gornja granica po izvođaču (ne stvarno ograničenje - sprečava
# da neka greška u parsiranju liste pesama napravi beskonačnu petlju).
MAX_SONGS_PER_ARTIST = 500

ARTIST_LIST_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "full_artist_list.csv"
OUTPUT_PATH = RAW_DATA_DIR / "corpus.csv"
PROBLEM_LOG_PATH = RAW_DATA_DIR / "problem_log_full.csv"


def _artist_mismatch_note(expected_artist: str, scraped_artist: str | None) -> str | None:
    if not scraped_artist:
        return None
    if expected_artist.strip().lower() == scraped_artist.strip().lower():
        return None
    return f"napomena: tražen izvođač '{expected_artist}', sajt vraća '{scraped_artist}' - proveri ručno"


def main():
    artist_df = pd.read_csv(ARTIST_LIST_PATH)
    session = make_session()

    records = []
    problems = []

    for _, row in tqdm(artist_df.iterrows(), total=len(artist_df), desc="Izvođači"):
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

    print(f"\nGotovo. Prikupljeno {len(df)} pesama od {artist_df['artist_name'].nunique()} traženih izvođača.")
    print(f"Sačuvano u: {OUTPUT_PATH}")
    print(f"Problema/napomena: {len(problems_df)} - videti {PROBLEM_LOG_PATH}")

    if len(df):
        issues = validate_dataset(df)
        if issues:
            print("\nUpozorenja o kvalitetu podataka:")
            for issue in issues:
                print(f"  - {issue}")
        print("\nPregled po periodu:")
        print(df["period"].value_counts())
        print("\nPregled po žanru:")
        print(df["genre"].value_counts())


if __name__ == "__main__":
    main()