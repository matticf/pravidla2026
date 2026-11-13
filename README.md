# Florbal srozumitelně

Grafický přehled pravidel florbalu pro diváky a laiky – podle dokumentu *Pravidla florbalu a jejich výklad, edice 2026* (platná od 1. 7. 2026).

Statický web bez závislostí: `index.html` + písmo Geogrotesque ve složce `fonts/`.

## Anglická verze

Anglická stránka je v `en/index.html` (*Floorball Made Simple*). Přepíná se tlačítkem EN / CZ v horní liště.

Anglická stránka se neupravuje ručně. Vyrábí se z české skriptem:

```bash
python3 tools/build_en.py
```

Překlady jsou ve složce `tools/`:

- `en_texty.json` – texty stránky (česky → anglicky),
- `en_js.json` – texty ve skriptech: komiksy, hra, simulátor, signály,
- `en_kviz.json` – anglický zásobník otázek kvízu.

Po změně české stránky spusťte skript znovu. Vypíše texty, ke kterým chybí překlad. Termíny se drží oficiálních pravidel IFF (*Rules of the Game 2026*).

## Zobrazení přes GitHub Pages

Settings → Pages → Source: *Deploy from a branch* → větev `main`, složka `/ (root)`.

Dotazy k pravidlům: pravidla@ceskyflorbal.cz
