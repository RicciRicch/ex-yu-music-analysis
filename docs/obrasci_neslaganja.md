# Obrasci neslaganja LLM klasifikacije i gold standarda — skica za diskusiju

## Kontekst (brojke iz validacije)

- Uzorak: 299 pesama, stratifikovano semplovanih po periodu i žanru
- Tema: Cohen's kappa = 0.405 (slabo-umereno slaganje), prosto slaganje 58.9%
- Emocija: Cohen's kappa = 0.356 (slabo-umereno slaganje), prosto slaganje 58.9%
- LLM sistematski favorizuje dominantne/opšte kategorije (ljubav, raskid/tuga za temu;
  negativno za emociju) nauštrb ređih, specifičnijih kategorija

Detaljni podaci: `results/reports/gold_vs_llm_comparison.csv`,
`results/reports/interesting_disagreements.csv`

---

## Obrazac 1 — Kategorijalno sažimanje nijanse

**Opis:** LLM u svom slobodnom opisu (`llm_values`) često *sam* prepoznaje mešovitu,
dvojaku prirodu emocije (i pozitivne i negativne elemente istovremeno), ali kad mora
da izabere JEDNU od četiri ponuđene kategorije emocije, ta nijansa se gubi — model
bira "negativno" umesto "mešano", iako njegov sopstveni opis to demantuje.

**Verovatan uzrok:** Prinudni izbor jedne kategorije (umesto npr. generisanja opisa
pa tek onda izvođenja kategorije iz njega) briše informaciju koju model interno ima.

**Primeri:**
- Nina Badrić – "Nebo": `llm_values` = "bol od gubitka, **nada** unatoč boli, vera u
  božansku pravdu", ali `llm_emotion` = negativno (gold: mešano)
- Boban Rajović – "Jugoslavijo": `llm_values` pominje i "patriotizam" i "žal, bol od
  raspada", ali `llm_emotion` = negativno (gold: mešano)
- Bombaj Štampa – "Bolje letim sam": `llm_values` gotovo potpuno pozitivan
  ("oslobađanje", "samootkrivanje", "samopouzdanje"), a `llm_emotion` = negativno
  (gold: mešano)

**Predložena rečenica za rad:** "Analiza pokazuje da model u više navrata interno
prepoznaje ambivalentnu prirodu emocije (vidljivo u generisanom opisu vrednosti), ali
gubi tu nijansu pri prinudnom izboru jedne od četiri ponuđene kategorije — što sugeriše
da bi drugačiji dizajn prompta (npr. dozvoljavanje generisanja opisa pre kategorizacije)
mogao poboljšati preciznost."

---

## Obrazac 2 — Mešanje tona sa sadržajem

**Opis:** Kod starijih, sporijih, čežnjivih ljubavnih balada (tipično SFRJ pop), LLM
melanholičan/nostalgičan STIL izražavanja pogrešno tumači kao dokaz da je SADRŽAJ
pesme o raskidu/gubitku — čak i kad pesma zapravo govori o trajnoj, postojanoj ljubavi.

**Verovatan uzrok:** Model povezuje leksičke markere melanholije (sećanje, čekanje,
sporost) sa temom raskida, ne razlikujući čežnjiv ton od stvarnog sadržaja o kraju veze.

**Primeri:**
- Zdravko Čolić – "Ti si bila uvijek bila": gold tema = ljubav, LLM tema = raskid/tuga;
  gold vrednosti "večna konstanta, stena oslonca, nepokolebljivost" nasuprot LLM
  "kajanje, nada uprkos boli"
- Oliver Dragojević – "Vrime je": gold tema = ljubav, LLM tema = raskid/tuga; gold
  "sazrevanje, emotivna predaja" nasuprot LLM "žal za izgubljenom ljubavlju"

**Predložena rečenica za rad:** "Kod starijih, poetskijih ljubavnih balada primećena
je tendencija modela da melanholičan ton izražavanja pogrešno protumači kao znak
raskida, umesto kao stilsku odliku žanra koja prati i pesme o postojanoj ljubavi."

---

## Obrazac 3 — Žanrovska konvencija predanosti čitana kao patološka zavisnost

**Opis:** U narodnoj/sevdah tradiciji, izrazi poput "ne mogu bez tebe da živim" ili
"suviše te volim" predstavljaju konvencionalan, pozitivno kodiran izraz strasti unutar
žanra. LLM ove izraze čita doslovno, kroz okvir bliži savremenom (zapadnom)
psihološkom rečniku, i kodira ih kao "zavisnost" — negativno, umesto kao žanrovski
standardnu romantičnu predanost.

**Verovatan uzrok:** Kulturno/žanrovsko nerazumevanje konvencije, ne opšta greška u
razumevanju jezika.

**Primeri:**
- Halid Muslimović – "Ljube mi se usne tvoje": gold emocija = mešano, LLM = negativno;
  LLM vrednosti "bezuslovna ljubav, **nemogućnost napuštanja**, zavisan odnos"
- Halid Muslimović – "Kunem se": gold emocija = mešano, LLM = negativno; LLM
  vrednosti "apsolutna privrženost, **nemoć bez voljene osobe**"
- Miroslav Ilić – "Nije život jedna žena": gold emocija = mešano, LLM = negativno,
  iako gold vrednosti ističu "inat, ponos, kretanje dalje" (otporan, ne slab ton)

**Predložena rečenica za rad:** "Primetno je da model izraze intenzivne predanosti
karakteristične za narodnu/sevdah tradiciju sistematski kodira kao negativne (kroz
okvir 'zavisnosti'), ne prepoznajući ih kao žanrovski konvencionalan, pozitivno
kodiran izraz strasti — mogući znak kulturno/žanrovski ograničenog razumevanja."

---

## Obrazac 4 — Hedonizam/provod sa romantičnom notom postaje "ljubav"

**Opis:** Najčešći temski obrazac greške: pesme koje gold anotatori svrstavaju kao
"hedonizam/provod" (flert, fizička privlačnost, život za trenutak, površniji ugođaj)
LLM sistematski svrstava kao "ljubav" čim prepozna romantičan ili fizički vokabular,
ne razlikujući površniju, hedonističku notu od dublje emotivne privrženosti.

**Primeri:**
- Nedeljko Bajić Baja – "Crna kosa, oči plave": gold = hedonizam/provod (opčinjenost
  izgledom, gubljenje razuma), LLM = ljubav
- Nedeljko Bajić Baja – "Mini suknja": gold = hedonizam/provod (letnja provokacija,
  vizuelni flert), LLM = ljubav
- Colonia – "Oduzimaš mi dah": gold = hedonizam/provod (fizička privlačnost,
  gubljenje kontrole), LLM = ljubav

**Predložena rečenica za rad:** "Model ne razlikuje pouzdano 'hedonizam/provod' od
'ljubavi' kada je prisutan romantičan ili fizički vokabular — čim prepozna privlačnost
ili flert, poseže za širom, generičkom kategorijom ljubavi, gubeći nijansu površnijeg,
hedonističkog konteksta koji su ljudski anotatori prepoznali."

---

## Obrazac 5 — Satirična društvena kritika čitana kao identitet/domovina

**Opis:** Pesme sa indirektnom, satiričnom društvenom kritikom (karakteristično za
bendove poput Zabranjeno pušenje) LLM ne prepoznaje kao "politika/društvo", nego ih
svrstava u "identitet/domovina" — verovatno zato što očekuje eksplicitniji,
direktniji politički jezik za tu kategoriju.

**Primeri:**
- Zabranjeno pušenje – "Halid umjesto Halida": gold = politika/društvo (satira o
  lažnoj slavi), LLM = identitet/domovina
- Zabranjeno pušenje – "Modni guru": gold = politika/društvo (satira društvenih
  normi), LLM = identitet/domovina
- Parni valjak – "Autoput": gold = politika/društvo, LLM = identitet/domovina

**Predložena rečenica za rad:** "Indirektna, ironična društvena kritika ostaje slabo
prepoznata kao 'politika/društvo' — model je verovatno kalibrisan da tu kategoriju
prepoznaje kroz eksplicitniji politički jezik, pa satiru sistematski preusmerava ka
kategoriji identiteta."

---

## Sinteza za zaključak diskusije

Svih pet obrazaca ukazuje na zajedničku tendenciju: **LLM dobro prepoznaje eksplicitan,
doslovan sadržaj, ali slabije hvata nijansu koja zavisi od žanrovskog konteksta, tona,
ironije ili kulturne konvencije.** Ovo je u skladu sa poznatim ograničenjima LLM alata
na manje zastupljenim (low-resource) jezicima i kulturno specifičnim žanrovima
pomenutim u elaboratu (3.2) — model razume srpski/hrvatski na nivou reči i gramatike,
ali mu nedostaje kulturno/žanrovsko "iskustvo" koje ljudski anotator ima.
