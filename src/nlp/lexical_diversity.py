"""
src/nlp/lexical_diversity.py

Mere leksičke raznovrsnosti (TTR, MATTR) i gruba adaptacija čitljivosti
(Flesch-Kincaid stil) za srpski/hrvatski jezik.

NAPOMENA O ČITLJIVOSTI: Flesch-Kincaid formula je kalibrisana za engleski
jezik (konstante 0.39, 11.8, 15.59 dobijene su empirijski na engleskim
tekstovima). Ovde primenjujemo ISTU formulu na srpski tekst - apsolutna
vrednost "razreda čitljivosti" NIJE validna za srpski (nema empirijsku
osnovu za taj jezik). I dalje je korisna za RELATIVNO poređenje između
perioda/žanrova (da li tekst postaje kompleksniji/jednostavniji kroz
vreme) - ista formula se dosledno primenjuje svuda, pa razlike između
grupa i dalje nešto govore, samo apsolutni broj ne treba doslovno
tumačiti kao "razred škole".
"""

VOWELS = set("aeiouAEIOU")


def count_syllables_sr(word: str) -> int:
    """Gruba procena broja slogova za srpsku/hrvatsku reč - broji
    samoglasnike, plus 'r' kao slogotvorno kada je okruženo suglasnicima
    (npr. 'vrt', 'prst', 'trg') - čest fenomen u srpskom kog engleski
    brojači slogova ne poznaju."""
    word = word.lower()
    count = 0
    for i, ch in enumerate(word):
        if ch in VOWELS:
            count += 1
        elif ch == 'r':
            prev_is_vowel = i > 0 and word[i - 1] in VOWELS
            next_is_vowel = i < len(word) - 1 and word[i + 1] in VOWELS
            if not prev_is_vowel and not next_is_vowel:
                count += 1
    return max(count, 1)


def type_token_ratio(text: str) -> float:
    """Klasičan TTR = broj JEDINSTVENIH reči / ukupan broj reči.
    Poznato osetljiv na dužinu teksta - kraći tekstovi imaju veštački
    viši TTR. Koristiti MATTR za poređenje tekstova različite dužine."""
    words = text.lower().split()
    if not words:
        return 0.0
    return len(set(words)) / len(words)


def mattr(text: str, window_size: int = 50) -> float:
    """Moving-Average TTR - TTR računat u pokretnom prozoru fiksne
    dužine, usrednjen preko svih pozicija prozora. Ne zavisi od ukupne
    dužine teksta kao obični TTR - pouzdaniji za poređenje pesama
    različite dužine (npr. kratak refren vs. duga balada)."""
    words = text.lower().split()
    n = len(words)
    if n < window_size:
        return type_token_ratio(text)
    ratios = []
    for i in range(n - window_size + 1):
        window = words[i:i + window_size]
        ratios.append(len(set(window)) / window_size)
    return sum(ratios) / len(ratios)


def flesch_kincaid_grade_sr(text: str):
    """Flesch-Kincaid Grade Level (ORIGINALNE engleske konstante,
    primenjene na srpski - videti napomenu na vrhu modula). Linije
    teksta koristimo kao proxy za rečenice (tekstovi pesama retko
    imaju standardnu interpunkciju)."""
    lines = [l for l in text.split('\n') if l.strip()]
    words = text.split()
    if not lines or not words:
        return None
    total_syllables = sum(count_syllables_sr(w) for w in words)
    words_per_sentence = len(words) / len(lines)
    syllables_per_word = total_syllables / len(words)
    grade = 0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59
    return round(grade, 2)