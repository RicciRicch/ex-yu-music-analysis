"""
src/preprocessing/clean_text.py

Čisti sirov tekst pesme (lyrics_raw) u čitljiv, normalizovan oblik
(lyrics_clean): uklanja strukturne oznake ([Strofa 1], [Refren]...),
normalizuje ćirilicu u latinicu, čisti višak razmaka/praznih linija.

NAPOMENA - poznato ograničenje: ćirilica->latinica konverzija radi slovo
po slovo, pa dvoslovi (lj, nj, dž) u REČIMA PISANIM SVIM VELIKIM SLOVIMA
neće biti tačno konvertovani (npr. "ЉУБАВ" -> "LjUBAV" umesto "LJUBAV").
Ovo je redak slučaj u tekstovima pesama (uglavnom se koristi za refren/
naglašavanje), pa ga svesno ne rešavamo sada - može se doraditi kasnije
ako se pokaže da je čest problem u stvarnom korpusu.
"""

import re

CYRILLIC_TO_LATIN = {
    'а':'a','б':'b','в':'v','г':'g','д':'d','ђ':'đ','е':'e','ж':'ž','з':'z',
    'и':'i','ј':'j','к':'k','л':'l','љ':'lj','м':'m','н':'n','њ':'nj','о':'o',
    'п':'p','р':'r','с':'s','т':'t','ћ':'ć','у':'u','ф':'f','х':'h','ц':'c',
    'ч':'č','џ':'dž','ш':'š',
    'А':'A','Б':'B','В':'V','Г':'G','Д':'D','Ђ':'Đ','Е':'E','Ж':'Ž','З':'Z',
    'И':'I','Ј':'J','К':'K','Л':'L','Љ':'Lj','М':'M','Н':'N','Њ':'Nj','О':'O',
    'П':'P','Р':'R','С':'S','Т':'T','Ћ':'Ć','У':'U','Ф':'F','Х':'H','Ц':'C',
    'Ч':'Č','Џ':'Dž','Ш':'Š',
}

# Prepoznaje red koji je SAMO strukturna oznaka, npr. "[Strofa 1]", "[Refren]"
STRUCTURE_MARKERS_RE = re.compile(r'^\[.*?\]\s*$', re.MULTILINE)


def cyrillic_to_latin(text: str) -> str:
    """Konvertuje ćirilicu u latinicu, slovo po slovo."""
    return ''.join(CYRILLIC_TO_LATIN.get(ch, ch) for ch in text)


def is_cyrillic(text: str) -> bool:
    """Vraća True ako je više od 30% slova u tekstu ćirilica - prag od
    30%, ne 100%, jer tekst može imati pokoje latinično slovo/broj a
    ipak biti "ćirilični" tekst (npr. brojevi u tekstu su isti u oba pisma)."""
    cyr = sum(1 for ch in text if ch in CYRILLIC_TO_LATIN)
    letters = sum(1 for ch in text if ch.isalpha())
    return letters > 0 and (cyr / letters) > 0.3


def remove_structure_markers(text: str) -> str:
    """Uklanja oznake strukture pesme kao [Strofa 1], [Refren], [Most] -
    ovo nije deo samog teksta, nego navigacioni metapodatak koji neki
    izvori dodaju, i unosi šum u analizu tema/sentimenta ako ostane."""
    return STRUCTURE_MARKERS_RE.sub('', text)


def normalize_whitespace(text: str) -> str:
    """Uklanja višak razmaka na početku/kraju svakog reda i potpuno
    prazne redove (koji su često ostatak posle uklanjanja oznaka iznad)."""
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]
    return '\n'.join(lines)


def clean_lyrics(text: str) -> str:
    """Glavna funkcija - spaja sve korake čišćenja u ispravnom redosledu."""
    if not text:
        return ""
    text = remove_structure_markers(text)
    if is_cyrillic(text):
        text = cyrillic_to_latin(text)
    text = normalize_whitespace(text)
    return text

# --- Detekcija jezika (gruba heuristika, vidi napomenu u docstring-u modula) ---

EKAVICA_MARKERS = [
    r'\bmlek\w*', r'\bvrem\w*', r'\bsvet\w*', r'\blep\w*', r'\brec\w*', r'\breč\w*',
    r'\bdevoj\w*', r'\bcel\w*', r'\bbel\w*', r'\bsneg\w*', r'\bgde\w*', r'\bposle\w*',
    r'\bčovek\w*', r'\bcovek\w*', r'\bzvezd\w*', r'\bžele\w*', r'\bzele\w*', r'\brek\w*',
    r'\bpesm\w*', r'\bver\w*', r'\bleto\w*', r'\bsmeh\w*', r'\bsed\w*', r'\bovde\w*',
]
IJEKAVICA_MARKERS = [
    r'\bmlij\w*', r'\bvrij\w*', r'\bsvij\w*', r'\blij\w*', r'\brij\w*', r'\bdjevoj\w*',
    r'\bcij\w*', r'\bbij\w*', r'\bsnij\w*', r'\bgdje\w*', r'\bposlij\w*', r'\bčovjek\w*',
    r'\bcovjek\w*', r'\bzvijezd\w*', r'\bželj\w*', r'\bzelj\w*', r'\brijek\w*', r'\bpjesm\w*',
    r'\bvjer\w*', r'\bljeto\w*', r'\bsmij\w*', r'\bsjed\w*', r'\bovdje\w*',
]

EKAVICA_RE = re.compile('|'.join(EKAVICA_MARKERS), re.IGNORECASE)
IJEKAVICA_RE = re.compile('|'.join(IJEKAVICA_MARKERS), re.IGNORECASE)


def detect_language(text: str, was_cyrillic: bool) -> str:
    """Gruba heuristika: ćirilica ili preovlađujuća ekavica -> 'sr'.
    Preovlađujuća ijekavica -> 'nepoznato' (moglo bi biti hr ili bs,
    ne razlikujemo pouzdano automatski - videti napomenu u modulu).
    Bez jasnog signala -> 'nepoznato'."""
    if was_cyrillic:
        return "sr"
    ekavica_hits = len(EKAVICA_RE.findall(text))
    ijekavica_hits = len(IJEKAVICA_RE.findall(text))
    if ekavica_hits > ijekavica_hits:
        return "sr"
    return "nepoznato"