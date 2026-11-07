# Forma-1 adatelemzés Pythonnal

Python beadandó: a Forma-1 világbajnokság teljes történetét (1950–2024) elemzi öt összetett kérdés mentén, **numpy**, **pandas** és **plotly** segítségével. A script az eredményeket kiírja a terminálba, a grafikonokat pedig megnyitja a böngészőben.

## Gyors kipróbálás

```bash
git clone https://github.com/FELHASZNALONEV/REPO-NEVE.git
cd REPO-NEVE
pip install numpy pandas plotly
python f1_elemzes.py
```

Nincs git a gépeden? Kattints a repó oldalán a zöld **Code** gombra, majd a **Download ZIP** opcióra, csomagold ki, és lépj be a kicsomagolt mappába. A további lépések ugyanazok.

macOS-en és Linuxon `python` helyett `python3`, `pip` helyett `pip3` kell.

## Mit csinál a script?

Öt kérdésre keres választ a Forma-1 történeti adataiból:

1. **Hazai pálya előnye:** hányszor esélyesebb a győzelem hazai pályán, mint idegenben? Az összes győzelem hány százaléka hazai győzelem, és kik nyertek így a legtöbbet?
2. **Rajtpozíció és fordítások:** mekkora a győzelmi esély rajtpozíciónként, mekkora a pole-ból nyerés aránya évtizedenként, és kik nyertek a legtöbbször hátulról?
3. **Megbízhatóság:** hogyan változott a célba érés, a baleseti és a műszaki kiesések aránya évtizedenként, és melyik csapat a legmegbízhatóbb 2014 óta?
4. **Életkor:** hány évesen nyernek a pilóták, kik a legfiatalabb és a legidősebb győztesek, és melyik korcsoportnak a legnagyobb a győzelmi esélye?
5. **Csapatdominancia:** mely szezonokat uralta egy csapat, és melyek voltak a legkiegyenlítettebbek? (Herfindahl-indexszel.)

## Részletes lépések

### 1. Követelmények

- Python 3.9 vagy újabb (ellenőrzés: `python --version`). Ha nincs, töltsd le a [python.org](https://www.python.org/downloads/) oldalról. Windowson telepítéskor pipáld be az **"Add Python to PATH"** opciót.
- Internetkapcsolat a csomagok telepítéséhez.

### 2. A projekt letöltése

Töltsd le a repót `git clone` paranccsal vagy ZIP-ként (lásd fent), majd nyiss egy terminált a projekt mappájában. Windowson a mappa címsorába írd be, hogy `cmd`, és nyomj Entert.

### 3. Csomagok telepítése

```bash
pip install numpy pandas plotly
```

Ha a `pip` nem található, használd ezt: `python -m pip install numpy pandas plotly`.

Ha nem szeretnéd a gép globális Python-környezetét módosítani, előbb létrehozhatsz egy virtuális környezetet (opcionális):

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Futtatás

```bash
python f1_elemzes.py
```

Mindig a projekt mappájából indítsd, mert a script relatív útvonalon keresi az adatokat.

### 5. Mire számíts

- Az első indítás néhány másodperctől fél percig is eltarthat, mert a csomagok betöltése időbe telik.
- A kérdésenkénti eredmények a terminálban jelennek meg.
- Minden kérdés végén megnyílik egy böngészőfül az adott interaktív grafikonnal (ráhúzhatod az egeret az értékekre, zoomolhatsz, a kamera ikonnal PNG-ként le is töltheted).
- A grafikonok HTML fájlként az `output` mappába is mentődnek. A mappát a script magától létrehozza, a repóban nincs benne.

| Fájl | Tartalom |
|---|---|
| `q1_hazai_elony.html` | Győzelmi arány hazai és idegen pályán, évtizedenként |
| `q2_rajtpozicio.html` | Győzelmi esély a rajtpozíció függvényében |
| `q3_megbizhatosag.html` | Célba érés és kiesések okai évtizedenként |
| `q4_eletkor.html` | A futamgyőztesek életkora évtizedenként |
| `q5_dominancia.html` | Győzelmek koncentrációja szezononként (HHI) |

## Adatok

A repóban benne van a `data` mappa a Forma-1 adatbázis CSV fájljaival, ezért nem kell külön letöltened semmit. A script ezeket használja: `races.csv`, `results.csv`, `drivers.csv`, `circuits.csv`, `constructors.csv`, `status.csv`. A többi fájl nincs használatban.

Ha a `data` mappa hiányzik vagy üres, töltsd le az adatbázist a [Kaggle-ről](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020) (ingyenes fiók kell hozzá), és csomagold ki a CSV fájlokat a `data` mappába.

Forrás: Rohan Rao (Vopani): *Formula 1 World Championship (1950–2024)*, Kaggle. Az adatok az Ergast adatbázisból származnak. A felhasználási feltételeket az eredeti Kaggle oldalon találod.

## Gyakori hibák

| Hiba | Megoldás |
|---|---|
| `git` nem található | Használd a **Download ZIP** opciót a repó oldalán. |
| `python` nem található (macOS/Linux) | Használd a `python3` parancsot. |
| `FileNotFoundError: data/races.csv` | Nem a projekt mappájából indítottad a scriptet, vagy a CSV-k nincsenek a `data` mappában. |
| `ModuleNotFoundError: No module named 'plotly'` | A csomag nem abba a Pythonba települt, amivel futtatod. Használd a `python -m pip install numpy pandas plotly` parancsot. |
| A cmd "lefagyni" látszik (Windows) | Ha belekattintottál az ablakba, a Windows megállítja a futást. Nyomj egy Entert vagy Esc-et. |
| Nem nyílik meg böngésző | Nyisd meg kézzel az `output` mappában lévő HTML fájlokat. |

## Korlátok

- Az adatbázis **nem tartalmaz időjárási adatot**, ezért az "esős pályán" jellegű kérdések nem vizsgálhatók vele.
- A hazai pilóta megállapítása a pilóta nemzetisége és a pálya országa alapján történik. A `NAT_TO_COUNTRY` szótárban nem szereplő nemzetiségek kimaradnak a hazai elemzésből, a szótár a script elején bővíthető.
- A kiesések okainak (baleset vs. műszaki hiba) besorolása a `status` oszlop szövegének kulcsszavas keresésén alapul, ezért közelítés.

## A projekt felépítése

```
.
├── f1_elemzes.py   # az elemző script
├── README.md
└── data/           # Forma-1 adatok (CSV)
```

Futtatás után egy `output` mappa is megjelenik a generált grafikonokkal.
