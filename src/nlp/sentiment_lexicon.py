"""
src/nlp/sentiment_lexicon.py

Leksikonska (rečnik-bazirana) analiza sentimenta za srpski/hrvatski.

NAPOMENA O OGRANIČENJU: ne postoji standardizovan, opšteprihvaćen
sentiment leksikon za srpski/hrvatski (za razliku od engleskog gde
postoji SentiWordNet). Ovo je ručno sastavljen, mali leksikon (~70 reči)
baziran na rečima koje dominiraju ovim korpusom (potvrđeno TF-IDF
analizom). Nije validiran akademski instrument - orijentaciona mera.
Elaborat (4.3) predviđa dopunu LLM klasifikacijom u Fazi 5, koja bolje
hvata kontekst (ironiju, negaciju...) koje leksikon ne može.

Leksikon koristi LEME jer se primenjuje na 'lemmas' kolonu - classla
model normalizuje leme ka ekavskom obliku čak i za ijekavski unet tekst
(npr. 'svijetu' -> lema 'svet'), pa je dovoljno imati uglavnom ekavske
oblike ovde.
"""

POSITIVE_LEXICON = {
    "ljubav", "voleti", "sreća", "srećan", "radost", "radostan", "lep",
    "dobro", "smejati", "osmeh", "sunce", "prijatelj", "nada", "mir",
    "sloboda", "pobeda", "uspeh", "zagrljaj", "poljubac", "cvet",
    "proleće", "veselje", "veseo", "milovati", "draga", "dragi", "anđeo",
    "sjaj", "sjajan", "svetlost", "toplina", "topao", "lepota", "žudeti",
    "čežnja",
}

NEGATIVE_LEXICON = {
    "tuga", "tužan", "suza", "bol", "bolan", "samoća", "sam", "plakati",
    "izdaja", "izdati", "laž", "lagati", "mrzeti", "strah", "smrt",
    "gubitak", "patnja", "jad", "nesreća", "rat", "tama", "taman", "zlo",
    "greh", "prevariti", "prevara", "kajanje", "kajati", "žaliti",
    "napustiti", "ostaviti", "razočaranje", "razočarati", "krv",
    "umreti", "propast", "propasti", "usamljen",
}


def sentiment_score(lemmas_text: str) -> float:
    """Vraća skor u opsegu [-1, 1]: (broj pozitivnih - broj negativnih
    reči) / ukupan broj reči. Napomena: 0 znači i 'neutralno' i 'leksikon
    nije pogodio nijednu reč' - ova mera ta dva slučaja ne razlikuje."""
    words = lemmas_text.lower().split()
    if not words:
        return 0.0
    pos = sum(1 for w in words if w in POSITIVE_LEXICON)
    neg = sum(1 for w in words if w in NEGATIVE_LEXICON)
    return (pos - neg) / len(words)


def sentiment_label(score: float, threshold: float = 0.01) -> str:
    """Pretvara skor u kategoriju - prag 0.01 (ne 0) jer su skorovi po
    pesmi mali brojevi (par pogodaka na stotine reči); prag tačno na 0
    bi klasifikovao skoro svaku blagu razliku kao pozitivnu/negativnu."""
    if score > threshold:
        return "pozitivno"
    if score < -threshold:
        return "negativno"
    return "neutralno"