"""
Python beadandó - Forma-1 világbajnokság (1950-2020) elemzése
Adatforrás (Kaggle): rohanrao/formula-1-world-championship-1950-2020
A CSV fájlokat a script mellett egy "data" mappába kell kicsomagolni.

Használt csomagok: numpy, pandas, plotly
    pip install numpy pandas plotly
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DATA = Path("data")
OUT = Path("output")
OUT.mkdir(exist_ok=True)


# ----------------------------------------------------------------------
# 1. Adatok betöltése és egyesítése
# ----------------------------------------------------------------------
def load(name: str) -> pd.DataFrame:
   
    return pd.read_csv(DATA / f"{name}.csv", na_values=["\\N"])


races = load("races")
results = load("results")
drivers = load("drivers")
circuits = load("circuits")
constructors = load("constructors")
status = load("status")

df = (
    results
    .merge(races[["raceId", "year", "round", "name", "date", "circuitId"]]
           .rename(columns={"name": "race_name"}), on="raceId")
    .merge(drivers[["driverId", "forename", "surname", "dob", "nationality"]], on="driverId")
    .merge(circuits[["circuitId", "country"]], on="circuitId")
    .merge(constructors[["constructorId", "name"]].rename(columns={"name": "constructor"}),
           on="constructorId")
    .merge(status, on="statusId")
)
df["driver"] = df["forename"] + " " + df["surname"]
df["date"] = pd.to_datetime(df["date"])
df["dob"] = pd.to_datetime(df["dob"])
df["decade"] = (df["year"] // 10) * 10
df["win"] = df["positionOrder"].eq(1)
df["podium"] = df["positionOrder"].le(3)


def header(text: str) -> None:
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


# ----------------------------------------------------------------------
# 1. KÉRDÉS - Hazai pálya előnye
# Mennyivel nagyobb a győzelmi esély, ha a pilóta hazai pályán indul?
# Az összes győzelem hányad része hazai győzelem, és kik nyertek így a legtöbbet?
# ----------------------------------------------------------------------
NAT_TO_COUNTRY = {
    "British": "UK", "German": "Germany", "Italian": "Italy", "French": "France",
    "Brazilian": "Brazil", "Argentine": "Argentina", "Austrian": "Austria",
    "Finnish": "Finland", "Spanish": "Spain", "Australian": "Australia",
    "Canadian": "Canada", "Japanese": "Japan", "American": "USA", "Mexican": "Mexico",
    "Dutch": "Netherlands", "Belgian": "Belgium", "Swiss": "Switzerland",
    "Monegasque": "Monaco", "Swedish": "Sweden", "South African": "South Africa",
    "Hungarian": "Hungary", "Portuguese": "Portugal", "Colombian": "Colombia",
    "Russian": "Russia", "Malaysian": "Malaysia", "New Zealander": "New Zealand",
    "Venezuelan": "Venezuela", "Chinese": "China",
}


def q1_hazai_elony() -> None:
    header("1. KÉRDÉS: Hazai pálya előnye")
    d = df.copy()
    d["home_country"] = d["nationality"].map(NAT_TO_COUNTRY)
    d["is_home"] = d["home_country"] == d["country"]

    
    had_home = d[d["is_home"]]["driver"].unique()
    e = d[d["driver"].isin(had_home)]

    summary = e.groupby("is_home").agg(
        rajtok=("win", "size"),
        gyozelmek=("win", "sum"),
        dobogok=("podium", "sum"),
        atlag_rajt=("grid", lambda s: s[s > 0].mean()),
    )
    summary["gyozelmi_arany_%"] = summary["gyozelmek"] / summary["rajtok"] * 100
    summary["dobogos_arany_%"] = summary["dobogok"] / summary["rajtok"] * 100
    print(summary.round(2).rename(index={True: "hazai", False: "idegen"}))

   
    n1, w1 = summary.loc[True, ["rajtok", "gyozelmek"]]
    n2, w2 = summary.loc[False, ["rajtok", "gyozelmek"]]
    p1, p2, p = w1 / n1, w2 / n2, (w1 + w2) / (n1 + n2)
    z = (p1 - p2) / np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    print(f"\nHazai / idegen győzelmi esély aránya: {p1 / p2:.2f}x   (z = {z:.2f}, "
          f"|z|>1.96 esetén szignifikáns 5%-on)")

    all_wins = d[d["win"]]
    print(f"Az összes futamgyőzelem {all_wins['is_home'].mean() * 100:.1f}%-a hazai győzelem, "
          f"{(~all_wins['is_home']).mean() * 100:.1f}%-a nem hazai.")

    print("\nTop 10 pilóta hazai győzelmek szerint:")
    print(all_wins[all_wins["is_home"]].groupby("driver").size()
          .sort_values(ascending=False).head(10))

    by_dec = e.groupby(["decade", "is_home"])["win"].mean().mul(100).reset_index()
    by_dec["is_home"] = by_dec["is_home"].map({True: "hazai", False: "idegen"})
    fig = px.bar(by_dec, x="decade", y="win", color="is_home", barmode="group",
                 labels={"decade": "Évtized", "win": "Győzelmi arány (%)", "is_home": ""},
                 title="Győzelmi arány hazai és idegen pályán, évtizedenként")
    fig.write_html(OUT / "q1_hazai_elony.html")


# ----------------------------------------------------------------------
# 2. KÉRDÉS - Rajtpozíció és fordítások
# Mennyit számít a rajtpozíció, és kik nyertek a legtöbbször hátulról?
# ----------------------------------------------------------------------
def q2_rajtpozicio() -> None:
    header("2. KÉRDÉS: Rajtpozíció és fordítások")
    g = df[df["grid"] > 0].copy()          

    by_grid = g[g["grid"] <= 20].groupby("grid")["win"].mean().mul(100)
    print("Győzelmi esély rajtpozíció szerint (első 5):")
    print(by_grid.head(5).round(1))

    corr = np.corrcoef(g["grid"], g["positionOrder"])[0, 1]
    print(f"\nKorreláció a rajtpozíció és a végső helyezés között: {corr:.3f}")

    pole = g[g["grid"] == 1].groupby("decade")["win"].mean().mul(100).round(1)
    print("\nPole pozícióból nyerés aránya évtizedenként (%):")
    print(pole)

    comeback = (g[g["win"] & (g["grid"] >= 15)]
                [["year", "race_name", "driver", "constructor", "grid"]]
                .sort_values("grid", ascending=False).head(10))
    print("\nLegnagyobb fordítások (győzelem a 15. vagy hátrébbi rajtról):")
    print(comeback.to_string(index=False))

    print("\nA legtöbb győzelem a 10. vagy hátrébbi rajtról:")
    print(g[g["win"] & (g["grid"] >= 10)].groupby("driver").size()
          .sort_values(ascending=False).head(5))

    fig = px.bar(by_grid.reset_index(), x="grid", y="win",
                 labels={"grid": "Rajtpozíció", "win": "Győzelmi esély (%)"},
                 title="Győzelmi esély a rajtpozíció függvényében")
    fig.write_html(OUT / "q2_rajtpozicio.html")


# ----------------------------------------------------------------------
# 3. KÉRDÉS - Megbízhatóság
# Hogyan változott a kiesések aránya és oka (baleset vs. műszaki hiba),
# és melyik csapat a legmegbízhatóbb a hibrid korszakban (2014-től)?
# ----------------------------------------------------------------------
def q3_megbizhatosag() -> None:
    header("3. KÉRDÉS: Megbízhatóság és kiesések")
    d = df[~df["status"].isin(["Did not qualify", "Did not prequalify"])].copy()
    finished = d["status"].eq("Finished") | d["status"].str.startswith("+")
    accident = d["status"].str.contains("Accident|Collision|Spun off", case=False)
    d["dnf"] = ~finished
    d["tipus"] = np.select([finished, accident],
                           ["Célba ért", "Baleset/ütközés"], default="Műszaki/egyéb")

    shares = pd.crosstab(d["decade"], d["tipus"], normalize="index") * 100
    print("Eredmények megoszlása évtizedenként (%):")
    print(shares.round(1))

    recent = d[d["year"] >= 2014]
    cs = recent.groupby("constructor").agg(rajtok=("dnf", "size"), kiesesi_arany=("dnf", "mean"))
    cs = cs[cs["rajtok"] >= 100].sort_values("kiesesi_arany")
    cs["kiesesi_arany"] = (cs["kiesesi_arany"] * 100).round(1)
    print("\nLegmegbízhatóbb csapatok 2014 óta (min. 100 rajt), kiesési arány %:")
    print(cs.head(5))
    print("\nLeggyengébb megbízhatóságú csapatok:")
    print(cs.tail(5))

    fig = px.bar(shares.reset_index().melt(id_vars="decade", var_name="tipus", value_name="szazalek"),
                 x="decade", y="szazalek", color="tipus",
                 labels={"decade": "Évtized", "szazalek": "%", "tipus": ""},
                 title="Célba érés és kiesések okai évtizedenként")
    fig.write_html(OUT / "q3_megbizhatosag.html")


# ----------------------------------------------------------------------
# 4. KÉRDÉS - Életkor
# Hány évesen nyernek a pilóták, és melyik korcsoportnak a legnagyobb az esélye?
# ----------------------------------------------------------------------
def q4_eletkor() -> None:
    header("4. KÉRDÉS: Életkor és győzelmek")
    d = df.copy()
    d["age"] = (d["date"] - d["dob"]).dt.days / 365.25
    w = d[d["win"]]

    p10, p50, p90 = np.percentile(w["age"], [10, 50, 90])
    print(f"Győztesek életkora: medián {p50:.1f} év, 10-90% intervallum: {p10:.1f}-{p90:.1f} év")

    cols = ["driver", "race_name", "year", "age"]
    print("\nLegfiatalabb győztesek:")
    print(w.nsmallest(5, "age")[cols].round(1).to_string(index=False))
    print("\nLegidősebb győztesek:")
    print(w.nlargest(5, "age")[cols].round(1).to_string(index=False))

    print("\nGyőztesek átlagéletkora évtizedenként:")
    print(w.groupby("decade")["age"].agg(["mean", "median"]).round(1))

    d["korcsoport"] = pd.cut(d["age"], [17, 22, 26, 30, 34, 38, 60])
    rate = d.groupby("korcsoport", observed=True)["win"].mean().mul(100).round(2)
    print("\nGyőzelmi esély korcsoportonként (%):")
    print(rate)

    fig = px.box(w, x="decade", y="age", points="outliers",
                 labels={"decade": "Évtized", "age": "Győztes életkora"},
                 title="A futamgyőztesek életkora évtizedenként")
    fig.write_html(OUT / "q4_eletkor.html")


# ----------------------------------------------------------------------
# 5. KÉRDÉS - Dominancia
# Mely szezonokat uralta egy csapat? Herfindahl-index a győzelmek koncentrációjára.
# ----------------------------------------------------------------------
def q5_dominancia() -> None:
    header("5. KÉRDÉS: Csapatdominancia szezononként")
    w = df[df["win"]]
    wins = w.groupby(["year", "constructor"]).size().rename("wins").reset_index()
    races_per_year = wins.groupby("year")["wins"].sum().rename("futamok")
    wins = wins.join(races_per_year, on="year")
    wins["share"] = wins["wins"] / wins["futamok"]

    hhi = wins.groupby("year")["share"].apply(lambda s: np.sum(s.to_numpy() ** 2)).rename("hhi")
    top = (wins.sort_values("share").groupby("year").tail(1)
           .set_index("year")[["constructor", "share"]])
    res = pd.concat([hhi, races_per_year, top], axis=1)

    print("Legdominánsabb szezonok (a győzelmek koncentrációja alapján):")
    print(res.sort_values("hhi", ascending=False).head(5).round(3))
    print("\nLegkiegyenlítettebb szezonok:")
    print(res.sort_values("hhi").head(5).round(3))

    corr = np.corrcoef(res["futamok"], res["hhi"])[0, 1]
    print(f"\nKorreláció a futamok száma és a dominancia (HHI) között: {corr:.3f}")

    print("\nA legtöbb szezont 'uraló' csapat (>50% győzelmi arány):")
    print(res[res["share"] > 0.5]["constructor"].value_counts().head(5))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=res.index, y=res["hhi"], mode="lines+markers",
                             text=res["constructor"],
                             hovertemplate="%{x}: HHI=%{y:.2f}<br>%{text}<extra></extra>"))
    fig.update_layout(title="Győzelmek koncentrációja szezononként (HHI)",
                      xaxis_title="Év", yaxis_title="HHI (1 = egy csapat nyert mindent)")
    fig.write_html(OUT / "q5_dominancia.html")


if __name__ == "__main__":
    q1_hazai_elony()
    q2_rajtpozicio()
    q3_megbizhatosag()
    q4_eletkor()
    q5_dominancia()
    print(f"\nA grafikonok az '{OUT}' mappába kerültek (HTML, böngészőben nyithatók).")
