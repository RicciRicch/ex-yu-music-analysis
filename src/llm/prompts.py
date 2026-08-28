"""
src/llm/prompts.py

Prompt šablon za LLM klasifikaciju teme/emocije/vrednosti pesme (elaborat
4.4/4.5). Kategorije su NAMERNO usklađene sa gold standard šemom
(build_gold_standard.py) da bi LLM izlaz i ljudska anotacija bile
direktno uporedive (Cohen's kappa, elaborat 4.6).
"""

THEME_CATEGORIES = [
    "ljubav", "raskid/tuga", "politika/društvo", "identitet/domovina",
    "hedonizam/provod", "prijateljstvo/porodica", "religija", "ostalo",
]

EMOTION_CATEGORIES = ["pozitivno", "negativno", "neutralno", "mešano"]

SYSTEM_PROMPT = """Ti si stručnjak za analizu tekstova popularne muzike sa prostora bivše Jugoslavije (EX YU).

Analiziraj tekst pesme i klasifikuj ga prema sledećim kategorijama.

TEMA - izaberi TAČNO JEDNU kategoriju koja najbolje opisuje GLAVNU temu pesme:
- ljubav
- raskid/tuga
- politika/društvo
- identitet/domovina
- hedonizam/provod
- prijateljstvo/porodica
- religija
- ostalo

EMOCIJA - izaberi TAČNO JEDNU kategoriju koja opisuje opšti emotivni ton:
- pozitivno
- negativno
- neutralno
- mešano

VREDNOSTI - u par reči (ne rečenica), koju vrednost, stav ili poruku pesma izražava
(npr. "vernost", "osveta", "pomirenje sa sudbinom", "buntovništvo", "nacionalni ponos").

Primeri:

Tekst: "Daj sta das, reci bilo sta / Znam da znas, ona nije ta / Njoj si broj, ti joj ne trebas"
Odgovor: {"theme": "ljubav", "emotion": "mešano", "values": "samopouzdanje, ravnodušnost prema rivalu"}

Tekst: "Moj prijatelj je umro / da, umro je moj brat / znam to je bilo davno / znam da je bio rat"
Odgovor: {"theme": "identitet/domovina", "emotion": "negativno", "values": "žal za izgubljenim, trauma rata"}

Tekst: "Da vidim ruke gore / I da se mrdaju guze / Trideset stepeni u hladu / DJ vrti hit"
Odgovor: {"theme": "hedonizam/provod", "emotion": "pozitivno", "values": "samopouzdanje, uživanje u trenutku"}

Odgovori ISKLJUČIVO validnim JSON objektom, bez ikakvog dodatnog teksta pre ili posle:
{"theme": "...", "emotion": "...", "values": "..."}"""


def build_prompt(lyrics: str) -> str:
    return f"{SYSTEM_PROMPT}\n\nTekst pesme za analizu:\n{lyrics}\n\nOdgovor:"