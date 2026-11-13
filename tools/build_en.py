#!/usr/bin/env python3
"""Sestaví anglickou verzi en/index.html z české index.html.

Spuštění z kořene repozitáře:  python3 tools/build_en.py

Překlady jsou ve složce tools/:
  en_texty.json  česky -> anglicky pro texty a popisky v HTML
  en_js.json     dvojice [česky, anglicky] pro texty ve skriptech a stylech (v daném pořadí)
  en_kviz.json   anglický zásobník otázek kvízu (stejné pořadí a čísla jako český)

Skript vypíše texty, ke kterým překlad chybí. Po úpravě české stránky stačí
doplnit překlady a spustit ho znovu.
"""
import json, pathlib, re, sys

KOREN = pathlib.Path(__file__).resolve().parent.parent
TOOLS = KOREN / 'tools'
src = (KOREN / 'index.html').read_text(encoding='utf-8')
texty = json.loads((TOOLS / 'en_texty.json').read_text(encoding='utf-8'))
dvojice = json.loads((TOOLS / 'en_js.json').read_text(encoding='utf-8'))
kviz = json.loads((TOOLS / 'en_kviz.json').read_text(encoding='utf-8'))

chybi, problemy = [], []
PISMENO = re.compile(r'[A-Za-zÀ-ž]')


def preloz(s):
    """Přeloží jeden textový uzel nebo atribut, okolní mezery zachová."""
    jadro = s.strip()
    if not jadro or not PISMENO.search(jadro):
        return s
    if jadro not in texty:
        if jadro not in chybi:
            chybi.append(jadro)
        return s
    i = s.index(jadro)
    return s[:i] + texty[jadro] + s[i + len(jadro):]


# --- rozdělení na hlavičku, HTML tělo a skripty ---
b0 = src.index('<body>')
b1 = src.index('<script>', b0)
hlava, telo, skripty = src[:b0], src[b0:b1], src[b1:]

# --- přepínač jazyka (před překladem se schová za značku) ---
CZ_ODKAZ = '<a class="jazyk" href="en/index.html" hreflang="en" lang="en" aria-label="English version">EN</a>'
EN_ODKAZ = '<a class="jazyk" href="../index.html" hreflang="cs" lang="cs" aria-label="Česká verze">CZ</a>'
ZNACKA = '<!--JAZYK-->'
if CZ_ODKAZ not in telo:
    problemy.append('V české stránce chybí odkaz na anglickou verzi (přepínač jazyka).')
telo = telo.replace(CZ_ODKAZ, ZNACKA)

# --- HTML tělo: textové uzly a popisné atributy ---
telo = re.sub(r'>([^<>]+)<', lambda m: '>' + preloz(m.group(1)) + '<', telo)
telo = re.sub(r'(aria-label|placeholder|title)="([^"]+)"', lambda m: m.group(1) + '="' + preloz(m.group(2)) + '"', telo)

# --- hlavička ---
hlava = hlava.replace('<html lang="cs">', '<html lang="en">')
hlava = re.sub(r'<title>([^<]+)</title>', lambda m: '<title>' + preloz(m.group(1)) + '</title>', hlava)
hlava = re.sub(r'(<meta name="description" content=")([^"]+)"', lambda m: m.group(1) + preloz(m.group(2)) + '"', hlava)
hlava = hlava.replace('url("fonts/', 'url("../fonts/')
hlava = hlava.replace('<link rel="alternate" hreflang="en" href="en/index.html">', '<link rel="alternate" hreflang="cs" href="../index.html">')

telo = telo.replace(ZNACKA, EN_ODKAZ)

# --- kvíz ---
m = re.search(r'var ZASOBNIK=(\[.*?\]);\n', skripty, re.S)
cz_kviz = json.loads(m.group(1))
if [x['n'] for x in cz_kviz] != [x['n'] for x in kviz]:
    problemy.append('Anglický kvíz nemá stejné otázky (čísla n) jako český.')
for a, b in zip(cz_kviz, kviz):
    if len(a['o']) != len(b['o']) or a['r'] != b['r']:
        problemy.append(f'Kvíz, otázka {a["n"]}: jiný počet možností nebo jiné číslo pravidla.')
skripty = skripty[:m.start(1)] + json.dumps(kviz, ensure_ascii=False, separators=(',', ':')) + skripty[m.end(1):]

# --- skripty a styly: dvojice v daném pořadí ---
for cz, en in dvojice:
    n = hlava.count(cz) + skripty.count(cz)
    if n == 0:
        problemy.append('Ve skriptech nenalezeno: ' + cz[:90])
    hlava = hlava.replace(cz, en)
    skripty = skripty.replace(cz, en)

vystup = hlava + telo + skripty
(KOREN / 'en').mkdir(exist_ok=True)
(KOREN / 'en' / 'index.html').write_text(vystup, encoding='utf-8')

# --- kontrola: zbylá čeština (podle diakritiky) mimo komentáře a povolené výjimky ---
POVOLENO = ('Pravidla florbalu a jejich výklad', 'Česká verze')
bez_komentaru = re.sub(r'/\*.*?\*/|<!--.*?-->', lambda k: '\n' * k.group(0).count('\n'), vystup, flags=re.S)
zbytky = []
for i, radek in enumerate(bez_komentaru.split('\n'), 1):
    if re.search(r'[ěščřžýáíéůúťďňĚŠČŘŽÝÁÍÉŮÚŤĎŇ]', radek) and not any(p in radek for p in POVOLENO):
        mm = re.search(r'.{0,40}[ěščřžýáíéůúťďňĚŠČŘŽÝÁÍÉŮÚŤĎŇ].{0,40}', radek)
        zbytky.append(f'  řádek {i}: …{mm.group(0)}…')

print(f'en/index.html zapsán ({len(vystup)} znaků).')
if chybi:
    print(f'\nChybí překlad {len(chybi)} textů (doplňte do tools/en_texty.json):')
    for c in chybi:
        print('  ' + c)
if problemy:
    print('\nProblémy:')
    for p in problemy:
        print('  ' + p)
if zbytky:
    print(f'\nV anglické stránce zůstala čeština na {len(zbytky)} řádcích:')
    print('\n'.join(zbytky[:40]))
sys.exit(1 if (chybi or problemy or zbytky) else 0)
