# EX YU Music Analysis — Detaljan pregled napretka

## Faza 1 — Priprema projekta

Pre bilo kakvog koda, postavile smo temelj koji sve ostalo koristi:

**Struktura foldera** — svaka faza ima svoj folder u `src/` (`scraping/`, `preprocessing/`, `nlp/`, `llm/`, `visualization/`, `utils/`), `data/` je podeljena na `raw/` (sirovi tekstovi), `processed/` (očišćeni podaci) i `gold_standard/` (ručne anotacije). Ideja: kad god tražiš kod za određenu fazu, znaš tačno gde da gledaš.

**`config.py`** — jedno mesto gde žive sve konstante koje se koriste kroz ceo projekat: tri istorijska perioda (SFRJ 1960–1991, tranzicija 1991–2005, savremeno 2005–danas) sa funkcijom `get_period()` koja automatski svrstava godinu u period, osam žanrova kao kontrolisana lista (da "Rok" i "rock" ne postanu dve različite kategorije), i putanje do svih foldera. Kasnije smo dodale i LLM/scraping podešavanja u isti fajl.

**Git/GitHub** — privatan repozitorijum, `.gitignore` podešen da nikad ne pošalje sirove tekstove pesama (autorska prava) ni tajne API ključeve na GitHub.

## Faza 2 — Prikupljanje korpusa

Ovo je bila najduža faza po broju pravih tehničkih prepreka, i svaka je rešena metodom "testiraj uživo, ne nagađaj".

**Scraper (`src/scraping/tekstovi_pjesama.py`)** — pravi zahteve ka tekstovi-pjesama.com preko `requests`+`BeautifulSoup`. Ključne funkcije: `slugify_sr()` (pretvara "Riblja Čorba" u "riblja-corba" za URL), `resolve_artist_url()` (nalazi stranicu izvođača), `get_artist_songs()` (izvlači listu pesama), `scrape_song()` (skida i čisti tekst).

**Problemi na koje smo naišle i kako smo ih rešile:**
- *Kolizija imena* — "Azra" na sajtu nije bend Johnny Štulića nego savremena pevačica Azra Polumenta; "Ceca" nije Svetlana Ražnatović nego druga pevačica, Ceca Slavković. Rešeno automatskom proverom: kad se ime izvođača koje smo tražile razlikuje od imena koje sajt vrati za tu pesmu, beležimo napomenu (ne blokiramo unos — samo označavamo za ručnu proveru).
- *Sidebar kontaminacija* — `get_artist_songs()` je prvobitno hvatala i linkove iz globalnog "Zadnji dodani tekstovi" vidžeta (prisutnog na svakoj stranici sajta), ne samo prave pesme tog izvođača. Popravljeno ograničavanjem pretrage na deo stranice između naslova "Popis pjesama" i sledećeg naslova.
- *Mrtvi linkovi* — neki linkovi na sajtu vode ka nepostojećim stranicama (npr. Miroslav Ilić/Lepa Brena duet) — sajtova greška, ne naša, dokumentovano kao poznato ograničenje.

**Rezultat:** 104 izvođača (od planiranih ~106, dva su bila moje greške u listi — dupli unosi), **4.113 pesama** — premašen cilj elaborata od minimum 3.000.

**Dokumentovana ograničenja:** trep žanr ima samo 8 pesama (sajt praktično nema tu scenu), par SFRJ rok izvođača nedostaje (Riblja Čorba, Šarlo Akrobata i dr.), `lyricstranslate.com` istražen kao dopunski izvor ali odbačen jer blokira automatizovane zahteve (bot detection).

## Faza 3 — Preprocessing

**Čišćenje teksta (`src/preprocessing/clean_text.py`)** — tri koraka: uklanjanje strukturnih oznaka poput `[Strofa 1]`/`[Refren]`, konverzija ćirilice u latinicu (slovo-po-slovo mapiranje, uz posebnu pažnju za dvoslove lj/nj/dž), normalizacija razmaka i praznih linija.

**Detekcija jezika** — pošto ne postoji pouzdan automatski način da se sa sigurnošću razlikuju srpski/hrvatski/bosanski (međusobno su previše slični), napravile smo heuristiku baziranu na ekavici/ijekavici (parovi reči poput "gde"/"gdje", "reka"/"rijeka", "čovek"/"čovjek") — ekavica ili ćirilica → "sr", ijekavica → "nepoznato" (pošteno priznajemo da ne znamo da li je hr ili bs), bez markera → "nepoznato". Ovo smo iterativno proširivale (od 10 na ~24 para reči) da smanjimo broj "nepoznato" slučajeva bez lažnog povećanja pouzdanosti.

**Lematizacija (`classla`)** — svođenje reči na osnovni oblik (npr. "volela" → "voleti"), uz zadržavanje samo sadržajnih reči (imenice, glagoli, pridevi, prilozi, imena) — efikasnija zamena za klasičnu "stop-word" listu, jer se oslanja na jezički model, ne na ručno pravljenu listu.

**Filter za analizu** — otkrile smo da neke pesme uopšte nisu na srpskom/hrvatskom (englesk verzije pesama za strano tržište, npr. Zdravko Čolić "Fire is burning"; čak i jedna nemačka pesma Električnog Orgazma) — prepoznate po tome što `classla` lematizacija vrati skoro nula reči. 29 takvih pesama izbačeno iz analize-spremnog seta.

**Rezultat:** `corpus_analysis_ready.csv`, **4.084 pesama**, sa kolonama `lyrics_clean`, `language`, `lemmas` spremnim za NLP.

## Faza 4 — NLP analiza

Pet zasebnih analiza, svaka testirana na malom uzorku pre punog korpusa:

**TF-IDF** (`src/nlp/tfidf_keywords.py`) — svaki period/žanr tretiran kao jedan veliki "dokument", da bismo videle koje reči su karakteristične za njega, ne samo najčešće uopšte. Morale smo dodati "semantičku stop listu" (modalni glagoli poput "moći"/"hteti"/"znati" — gramatički su sadržajne reči, ali semantički prazne, pa su dominirale rezultatima dok ih nismo isključile). **Nalaz:** na vrhu liste (rang 1-10) sve grupe deluju slično (ljubav, srce dominiraju svuda) — prava razlika izranja na rangovima 11-20 (npr. "kokain"/"ortak" za hip-hop, "duša"/"suza" za narodnu muziku).

**Leksička raznovrsnost** (`src/nlp/lexical_diversity.py`) — pored običnog TTR-a (tip/token odnos), dodale smo MATTR (pokretni prosek kroz prozor fiksne dužine) jer je obični TTR osetljiv na dužinu teksta. Otkrile smo da TTR i MATTR daju **suprotne** zaključke o tome koji je period "raznovrsniji" — MATTR je pouzdaniji jer ne zavisi od dužine pesme. Dodale smo i grubu Flesch-Kincaid adaptaciju za srpski (brojanje slogova uz "r" kao slogotvorno u rečima poput "vrt"/"prst"), uz jasnu napomenu da apsolutna vrednost nije validna za srpski (formula je kalibrisana za engleski) — korisna je samo za relativno poređenje.

**Sentiment** (`src/nlp/sentiment_lexicon.py`) — pošto ne postoji standardizovan sentiment leksikon za srpski/hrvatski, napravile smo mali ručni leksikon (~70 reči) baziran na rečima koje dominiraju korpusom. **Nalaz:** blag trend — SFRJ period ima najviše pozitivnih pesama (48.8%), tranzicija/savremeno nešto negativnije obojeni periodi.

**LDA tematsko modelovanje** (`src/nlp/topic_modeling_lda.py`, preko `gensim`) — jedan model treniran na celom korpusu (ne poseban po grupi, da bi teme bile uporedive). 10 tema, uključujući jasno prepoznatljivu "brat/život/kraj" temu upadljivo dominantnu u hip-hop/rep žanru (44% naspram jednocifrenih procenata svuda drugde).

**BERTopic + K-means klasterizacija** (`src/nlp/embeddings_topics.py`, preko `sentence-transformers`) — koristi embeddings (numeričke reprezentacije značenja teksta) umesto bag-of-words kao LDA. Ovo je bio tehnički najrizičniji deo (najviše zavisnosti: `torch`, `sentence-transformers`, `umap-learn`, `hdbscan`), ali je prošao glatko. **Nalaz:** potvrđuje LDA nalaze i dodaje nove — jasno izdvojena Sarajevo/rat tema, dalmatinski dijalekat kao posebna tema (nešto što LDA nije video jer radi na lematizovanim, dijalekatski "izravnatim" rečima), religiozna tema. Većina pesama (68%) ostaje u "šum" kategoriji — nezavisna potvrda da je korpus tematski dominantno homogen (ljubav), sa jasno izdvojenim "ostrvima" specifičnijih tema.

**NER (imenovani entiteti)** — pokušano, ali `classla`-in NER model je davao besmislene, isprekidane rezultate (fragmenti reči, dupli unosi) zbog neusklađenosti verzija: `classla` je testiran sa `torch 1.12.0`, a jedina dostupna verzija za Python 3.13 je `torch 2.6.0+`. Downgrade nije moguć (nema gotovog paketa za tako nov Python). Dokumentovano kao ograničenje, isključeno iz finalnih nalaza.

## Faza 5 — LLM analiza (u toku)

**Odluka o obimu** — LLM analiza se radi na **gold standard uzorku (299 pesama)**, ne celom korpusu od 4084. Ovo je i metodološki opravdano (isti uzorak služi i za validaciju — Cohen's kappa poređenje LLM rezultata sa ljudskom anotacijom, kako elaborat 4.6 traži) i praktično neophodno (probale smo besplatan Google Gemini API, ali se pokazalo da je stvarni dnevni limit ~20 zahteva, ne ~1.500 kako opšta dokumentacija navodi — Google je limit drastično smanjio krajem 2025). Vratile smo se na Anthropic Claude (Haiku 4.5 model) — jeftinije i pouzdanije za ovaj obim (procena ~$0.50 za svih 299 pesama).

**Gold standard uzorak** (`src/utils/build_gold_standard.py`) — 299 pesama (cilj bio ~300, sitna razlika je zaokruživanje pri stratifikovanom semplovanju po periodu I žanru istovremeno), stratifikovano po periodu i žanru da odražava sastav celog korpusa.

**Prompt šablon** (`src/llm/prompts.py`) — traži klasifikaciju teme (8 kategorija: ljubav, raskid/tuga, politika/društvo, identitet/domovina, hedonizam/provod, prijateljstvo/porodica, religija, ostalo), emocije (pozitivno/negativno/neutralno/mešano) i vrednosti (slobodan tekst) — kategorije namerno usklađene sa kolonama gold standard fajla za lako poređenje. Uključuje tri few-shot primera iz različitih kategorija, kako elaborat (4.5) i predviđa.

**Batch skripta** (`src/llm/run_llm_classification.py`) — dizajnirana da bude prekidljiva/nastavljiva (pamti šta je već obrađeno, pa se sme prekinuti i nastaviti kasnije bez dupliranja posla) — bilo je posebno bitno dok smo mislile da radimo sa ograničenim besplatnim Gemini nivoom.

**Trenutno stanje:** kod je napisan i testiran (JSON parsiranje robusno na različite formate odgovora modela), ali pravi run čeka da se doda kredit na Anthropic nalog — poslednji pokušaj je vratio grešku "credit balance too low" na svih 20 probnih poziva.

**Paralelno, nezavisno:** ti i koleginica treba da popunite `gold_theme`/`gold_emotion`/`gold_values` kolone u `gold_standard_sample.csv` ručno — ovaj korak je potpuno odvojen od LLM koda (različiti fajlovi, redosled nije bitan), spajanje i poređenje dolazi tek kad oba budu gotova.

## Šta ostaje

1. Dodavanje kredita na Anthropic nalog → pun LLM run na 299 pesama
2. Ručna anotacija gold standarda (ti + koleginica)
3. Spajanje LLM + ljudskih anotacija po `song_id`, Cohen's kappa validacija
4. Faza 6 (iz tvog originalnog plana) — vizualizacije: grafovi trendova, word cloud-ovi, komparativni prikazi kroz dekade
5. Finalno ažuriranje README-a, poslednji commit
