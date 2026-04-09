import turtle            # knihovna pro jednoduchou 2D grafiku
import random            # náhodné pozice jídla
import sqlite3           # práce s SQLite databází
import json              # čtení session.json
import os                # kontrola existence souboru
from datetime import datetime   # aktuální datum a čas pro ukládání skóre
from typing import Optional     # pro typ Optional[str]

# ============================================================
# ========================= DATABÁZE ==========================
# ============================================================
# Tahle část zajišťuje ukládání výsledků hry do SQLite databáze.
# Databáze se jmenuje snake_game.db
# Ukládá:
# - skóre
# - datum odehrání
# - username hráče (pokud je přihlášený)
# ============================================================

DB_NAME = "snake_game.db"   # název databázového souboru


def vytvor_databazi():
    # --------------------------------------------------------
    # Funkce vytvoří databázi a tabulku "hry", pokud ještě neexistuje.
    # Tabulka obsahuje:
    # id       -> unikátní identifikátor
    # skore    -> dosažené skóre
    # datum    -> datum a čas odehrání
    # username -> jméno hráče
    # --------------------------------------------------------
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS hry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skore INTEGER NOT NULL,
            datum TEXT NOT NULL,
            username TEXT
        )
    """)

    # --------------------------------------------------------
    # Tento blok je tu kvůli kompatibilitě se starší verzí DB.
    # Kdyby už existovala stará tabulka bez sloupce username,
    # pokusí se ho přidat.
    # Pokud už tam je, SQLite vyhodí OperationalError
    # a ten jen ignorujeme.
    # --------------------------------------------------------
    try:
        c.execute("ALTER TABLE hry ADD COLUMN username TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


def nacti_prihlaseneho_hrace() -> Optional[str]:
    # --------------------------------------------------------
    # Funkce se pokusí načíst uživatele ze souboru session.json
    # Pokud soubor neexistuje nebo je rozbitý, vrací None.
    # --------------------------------------------------------
    if os.path.exists("session.json"):
        try:
            with open("session.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("username")
        except Exception:
            return None
    return None


def uloz_skore(skore: int):
    # --------------------------------------------------------
    # Uloží skóre aktuální hry do databáze.
    # Zároveň si načte přihlášeného uživatele.
    # --------------------------------------------------------
    username = nacti_prihlaseneho_hrace()

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO hry (skore, datum, username) VALUES (?, ?, ?)",
        (skore, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username)
    )
    conn.commit()
    conn.close()


def nacti_high_score() -> int:
    # --------------------------------------------------------
    # Načte nejvyšší dosažené skóre z databáze.
    # Pokud databáze zatím nic neobsahuje, vrátí 0.
    # --------------------------------------------------------
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COALESCE(MAX(skore), 0) FROM hry")
    vysledek = c.fetchone()[0]
    conn.close()
    return int(vysledek)


# vytvoření databáze při startu programu
vytvor_databazi()

# ============================================================
# ===================== BARVY / POMOCNÉ FUNKCE ===============
# ============================================================
# Tady jsou utility funkce:
# - ztmavení barvy
# - převod textového směru na číselný heading pro turtle
# ============================================================

def ztmav_barvu(hex_color: str, faktor: float) -> str:
    # --------------------------------------------------------
    # Vstup: hex barva, např. "#2aa36b"
    # faktor < 1 -> barva bude tmavší
    # Používá se pro postupné tmavnutí segmentů těla hada.
    # --------------------------------------------------------
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    r = max(0, int(r * faktor))
    g = max(0, int(g * faktor))
    b = max(0, int(b * faktor))

    return f"#{r:02x}{g:02x}{b:02x}"


def smer_na_heading(direction: str) -> int:
    # --------------------------------------------------------
    # Turtle používá heading:
    # 0   = doprava
    # 90  = nahoru
    # 180 = doleva
    # 270 = dolů
    #
    # Tohle převádí textový směr na číslo.
    # --------------------------------------------------------
    return {"nahoru": 90, "dolu": 270, "doleva": 180, "doprava": 0}.get(direction, 0)


# ============================================================
# ========================== SKINS ============================
# ============================================================
# Tady jsou definované vzhledy hry.
# Každý skin obsahuje:
# - barvu pozadí
# - barvu mřížky
# - barvu rámečku
# - barvu hlavy hada
# - barvu těla hada
# - barvu jídla
# - ikonu jídla
# - barvu textu
# ============================================================

SKINS = {
    1: {
        "bg": "#f2e6c9",
        "grid": "#d6c8a3",
        "frame": "#1f3d2a",
        "head": "#0b5d3b",
        "body": "#2aa36b",
        "food": "#b30000",
        "food_icon": "🍎",
        "text": "#1f3d2a"
    },
    2: {
        "bg": "#101018",
        "grid": "#252545",
        "frame": "#7c5cff",
        "head": "#00ffd0",
        "body": "#00c8ff",
        "food": "#ff3df2",
        "food_icon": "✨",
        "text": "#d7d7ff"
    },
    3: {
        "bg": "#0f1a14",
        "grid": "#1d2a22",
        "frame": "#a6ff4d",
        "head": "#a6ff4d",
        "body": "#46d36d",
        "food": "#ff4d6d",
        "food_icon": "☠",
        "text": "#c8ffd8"
    }
}

# výchozí skin
skin_id = 1
skin = SKINS[skin_id]

# ============================================================
# ===================== OKNO / ROZMĚRY =======================
# ============================================================
# Zde je nastavení velikosti okna a herního prostoru.
# Důležité:
# - okno má vlastní rozměry
# - herní plocha má vlastní hranice
# - rámeček je jen vizuální ohraničení kolem hrací plochy
# ============================================================

SIRKA_OKNA = 600
VYSKA_OKNA = 700
VELIKOST_KROKU = 20          # had se pohybuje po 20 pixelech
MAX_XY = 290
POSUN_HRY_Y = -60            # posunutí hrací plochy níž kvůli hornímu HUDu

# ------------------------------------------------------------
# skutečná herní oblast
# sem se může had pohybovat
# sem se může spawnovat jídlo
# ------------------------------------------------------------
HRACI_MIN_X = -280
HRACI_MAX_X = 280
HRACI_MIN_Y = -280 + POSUN_HRY_Y
HRACI_MAX_Y = 280 + POSUN_HRY_Y

# ------------------------------------------------------------
# vizuální rámeček kolem herní plochy
# tohle je jen grafické ohraničení
# ------------------------------------------------------------
RAMECEK_PADDING = 10
MIN_X = HRACI_MIN_X - RAMECEK_PADDING
MAX_X = HRACI_MAX_X + RAMECEK_PADDING
MIN_Y = HRACI_MIN_Y - RAMECEK_PADDING
MAX_Y = HRACI_MAX_Y + RAMECEK_PADDING

# ------------------------------------------------------------
# validní grid pozice
# jídlo se spawní jen sem, ale s rezervou jednoho políčka
# od kraje, aby ikonka nepřetékala přes desku
# ------------------------------------------------------------
X_POZICE = list(range(HRACI_MIN_X + VELIKOST_KROKU, HRACI_MAX_X, VELIKOST_KROKU))
Y_POZICE = list(range(HRACI_MIN_Y + VELIKOST_KROKU, HRACI_MAX_Y, VELIKOST_KROKU))

# ------------------------------------------------------------
# vytvoření okna
# ------------------------------------------------------------
okno = turtle.Screen()
okno.title("Hadi hra")
okno.bgcolor(skin["bg"])
okno.setup(width=SIRKA_OKNA, height=VYSKA_OKNA)
okno.tracer(0)   # ruční update obrazovky pro plynulejší řízení

# ============================================================
# ======================== HERNÍ STAV ========================
# ============================================================

hra_bezi = False
pauza = False
skore = 0
high_score = nacti_high_score()
rychlost_ms = 90   # čím menší číslo, tím rychlejší hra

# ============================================================
# =========================== UI TEXT ========================
# ============================================================

skore_text = turtle.Turtle()
skore_text.speed(0)
skore_text.color(skin["text"])
skore_text.penup()
skore_text.hideturtle()
skore_text.goto(0, 310)

info_text = turtle.Turtle()
info_text.speed(0)
info_text.color(skin["text"])
info_text.penup()
info_text.hideturtle()
info_text.goto(0, 280)

hrac_text = turtle.Turtle()
hrac_text.speed(0)
hrac_text.penup()
hrac_text.hideturtle()
hrac_text.goto(0, -330)


def update_skore():
    skore_text.clear()
    skore_text.write(
        f"Skóre: {skore}   High Score: {high_score}",
        align="center",
        font=("Arial", 16, "bold")
    )


def update_info(text=""):
    info_text.clear()
    if text:
        info_text.write(text, align="center", font=("Arial", 12, "normal"))


def update_hrac_text():
    hrac_text.clear()
    username = nacti_prihlaseneho_hrace()
    hrac_text.color(skin["text"])

    if username:
        hrac_text.write(f"Hráč: {username}", align="center", font=("Arial", 11, "normal"))
    else:
        hrac_text.color("#888888")
        hrac_text.write(
            "Nepřihlášen – přihlas se na localhost:8000",
            align="center",
            font=("Arial", 11, "normal")
        )


# ============================================================
# ====================== RÁMEČEK A MŘÍŽKA ====================
# ============================================================

ramecek = turtle.Turtle()
ramecek.hideturtle()
ramecek.speed(0)
ramecek.pensize(4)
ramecek.penup()

mrizka = turtle.Turtle()
mrizka.hideturtle()
mrizka.speed(0)
mrizka.pensize(1)
mrizka.penup()


def kresli_ramecek():
    ramecek.clear()

    # vnější rámeček
    ramecek.color(skin["frame"])
    ramecek.pensize(4)
    ramecek.goto(MIN_X, MIN_Y)
    ramecek.setheading(0)
    ramecek.pendown()

    for _ in range(2):
        ramecek.forward(MAX_X - MIN_X)
        ramecek.left(90)
        ramecek.forward(MAX_Y - MIN_Y)
        ramecek.left(90)

    ramecek.penup()

    # vnitřní linka
    vnitrni = 6
    ramecek.pensize(2)
    ramecek.goto(MIN_X + vnitrni, MIN_Y + vnitrni)
    ramecek.setheading(0)
    ramecek.pendown()

    for _ in range(2):
        ramecek.forward((MAX_X - MIN_X) - 2 * vnitrni)
        ramecek.left(90)
        ramecek.forward((MAX_Y - MIN_Y) - 2 * vnitrni)
        ramecek.left(90)

    ramecek.penup()


def kresli_mrizku(krok=40):
    mrizka.clear()
    mrizka.color(skin["grid"])

    for x in range(HRACI_MIN_X, HRACI_MAX_X + 1, krok):
        mrizka.goto(x, HRACI_MIN_Y)
        mrizka.pendown()
        mrizka.goto(x, HRACI_MAX_Y)
        mrizka.penup()

    for y in range(HRACI_MIN_Y, HRACI_MAX_Y + 1, krok):
        mrizka.goto(HRACI_MIN_X, y)
        mrizka.pendown()
        mrizka.goto(HRACI_MAX_X, y)
        mrizka.penup()


# ============================================================
# ============================ MENU ==========================
# ============================================================

menu_napis = turtle.Turtle()
menu_napis.hideturtle()
menu_napis.penup()
menu_napis.goto(0, 80)

high_score_text = turtle.Turtle()
high_score_text.hideturtle()
high_score_text.penup()
high_score_text.goto(0, 20)

tlacitko = turtle.Turtle()
tlacitko.hideturtle()
tlacitko.penup()
tlacitko.pensize(3)

tlacitko_text = turtle.Turtle()
tlacitko_text.hideturtle()
tlacitko_text.penup()


def vykresli_menu():
    global high_score

    okno.bgcolor(skin["bg"])
    menu_napis.clear()
    high_score_text.clear()
    tlacitko.clear()
    tlacitko_text.clear()
    update_info("")
    skore_text.clear()

    kresli_mrizku()
    kresli_ramecek()

    high_score = nacti_high_score()

    menu_napis.color(skin["text"])
    high_score_text.color(skin["text"])
    tlacitko.color(skin["frame"])
    tlacitko_text.color(skin["text"])

    menu_napis.write("Hadi Gameska!", align="center", font=("Arial", 28, "bold"))
    high_score_text.write(f"High Score: {high_score}", align="center", font=("Arial", 18, "normal"))

    tlacitko.goto(-70, -90)
    tlacitko.setheading(0)
    tlacitko.pendown()
    tlacitko.begin_fill()
    tlacitko.fillcolor("#b6f2c3" if skin_id == 1 else "#2a2a3a" if skin_id == 2 else "#1d2a22")

    for _ in range(2):
        tlacitko.forward(140)
        tlacitko.left(90)
        tlacitko.forward(55)
        tlacitko.left(90)

    tlacitko.end_fill()
    tlacitko.penup()

    tlacitko_text.goto(0, -75)
    tlacitko_text.write("START", align="center", font=("Arial", 18, "bold"))

    update_info("Skins: 1 / 2 / 3   |   Pauza (P)   Restart (R)")
    update_hrac_text()


# ============================================================
# ======================== HERNÍ OBJEKTY =====================
# ============================================================

hlava = turtle.Turtle()
hlava.speed(0)
hlava.shape("square")
hlava.shapesize(1.10, 1.10)
hlava.color(skin["head"])
hlava.penup()
hlava.goto(0, POSUN_HRY_Y)
hlava.direction = "stop"
hlava.hideturtle()

jidlo = turtle.Turtle()
jidlo.speed(0)
jidlo.shape("circle")
jidlo.shapesize(0.8, 0.8)
jidlo.color(skin["food"])
jidlo.penup()
jidlo.goto(0, 100 + POSUN_HRY_Y)
jidlo.hideturtle()

jidlo_ikona = turtle.Turtle()
jidlo_ikona.hideturtle()
jidlo_ikona.penup()


def nastav_jidlo_ikonu():
    # menší ikonka, aby nepřetékala přes okraj
    jidlo_ikona.clear()
    jidlo_ikona.color(skin["food"])
    jidlo_ikona.goto(jidlo.xcor(), jidlo.ycor() - 8)
    jidlo_ikona.write(skin["food_icon"], align="center", font=("Arial", 14, "bold"))


oko_L = turtle.Turtle()
oko_L.hideturtle()
oko_L.speed(0)
oko_L.shape("circle")
oko_L.shapesize(0.22, 0.22)
oko_L.color("black")
oko_L.penup()

oko_P = turtle.Turtle()
oko_P.hideturtle()
oko_P.speed(0)
oko_P.shape("circle")
oko_P.shapesize(0.22, 0.22)
oko_P.color("black")
oko_P.penup()

jazyk = turtle.Turtle()
jazyk.hideturtle()
jazyk.speed(0)
jazyk.shape("square")
jazyk.shapesize(0.10, 0.55)
jazyk.color(skin["food"])
jazyk.penup()


def aktualizuj_oblicej_hada():
    if not hra_bezi:
        oko_L.hideturtle()
        oko_P.hideturtle()
        jazyk.hideturtle()
        return

    oko_L.showturtle()
    oko_P.showturtle()

    x, y = hlava.xcor(), hlava.ycor()

    if hlava.direction == "nahoru":
        oko_L.goto(x - 6, y + 6)
        oko_P.goto(x + 6, y + 6)
        jazyk.hideturtle()

    elif hlava.direction == "dolu":
        oko_L.goto(x - 6, y - 6)
        oko_P.goto(x + 6, y - 6)
        jazyk.hideturtle()

    elif hlava.direction == "doleva":
        oko_L.goto(x - 6, y + 6)
        oko_P.goto(x - 6, y - 6)
        if random.random() < 0.22:
            jazyk.showturtle()
            jazyk.setheading(180)
            jazyk.goto(x - 14, y)
        else:
            jazyk.hideturtle()

    elif hlava.direction == "doprava":
        oko_L.goto(x + 6, y + 6)
        oko_P.goto(x + 6, y - 6)
        if random.random() < 0.22:
            jazyk.showturtle()
            jazyk.setheading(0)
            jazyk.goto(x + 14, y)
        else:
            jazyk.hideturtle()

    else:
        oko_L.goto(x - 6, y + 6)
        oko_P.goto(x + 6, y + 6)
        jazyk.hideturtle()


telo = []
telo_smer = []


def vycisti_telo():
    global telo, telo_smer
    for seg in telo:
        seg.goto(1000, 1000)
        seg.hideturtle()
    telo = []
    telo_smer = []


def nahodna_pozice_na_mrizce():
    x = random.choice(X_POZICE)
    y = random.choice(Y_POZICE)
    return x, y


def spawn_jidlo():
    while True:
        x, y = nahodna_pozice_na_mrizce()

        if abs(hlava.xcor() - x) < 1 and abs(hlava.ycor() - y) < 1:
            continue

        ok = True
        for seg in telo:
            if abs(seg.xcor() - x) < 1 and abs(seg.ycor() - y) < 1:
                ok = False
                break

        if ok:
            jidlo.goto(x, y)
            nastav_jidlo_ikonu()
            return


def aplikuj_skin_na_objekty():
    okno.bgcolor(skin["bg"])
    skore_text.color(skin["text"])
    info_text.color(skin["text"])
    menu_napis.color(skin["text"])
    high_score_text.color(skin["text"])
    hrac_text.color(skin["text"])
    hlava.color(skin["head"])
    jidlo.color(skin["food"])
    jazyk.color(skin["food"])

    kresli_mrizku()
    kresli_ramecek()

    for i, seg in enumerate(telo):
        f = max(0.55, 1.0 - (i * 0.03))
        seg.color(ztmav_barvu(skin["body"], f))

    if hra_bezi:
        nastav_jidlo_ikonu()
        aktualizuj_oblicej_hada()
        update_skore()


def nastav_skin(nove_id: int):
    global skin_id, skin
    if nove_id not in SKINS:
        return
    skin_id = nove_id
    skin = SKINS[skin_id]
    aplikuj_skin_na_objekty()

    if not hra_bezi:
        vykresli_menu()


def skin_1():
    nastav_skin(1)


def skin_2():
    nastav_skin(2)


def skin_3():
    nastav_skin(3)


# ============================================================
# ========================== OVLÁDÁNÍ ========================
# ============================================================

def jdi_nahoru():
    if hlava.direction != "dolu":
        hlava.direction = "nahoru"


def jdi_dolu():
    if hlava.direction != "nahoru":
        hlava.direction = "dolu"


def jdi_doleva():
    if hlava.direction != "doprava":
        hlava.direction = "doleva"


def jdi_doprava():
    if hlava.direction != "doleva":
        hlava.direction = "doprava"


def toggle_pauza():
    global pauza
    if not hra_bezi:
        return
    pauza = not pauza
    update_info("PAUZA (P) • Restart (R) • Skins 1/2/3" if pauza else "Pauza (P) • Restart (R) • Skins 1/2/3")


def restart():
    if hra_bezi:
        game_over(do_menu=False)
        spustit_hru()


okno.listen()
okno.onkeypress(jdi_nahoru, "Up")
okno.onkeypress(jdi_dolu, "Down")
okno.onkeypress(jdi_doleva, "Left")
okno.onkeypress(jdi_doprava, "Right")
okno.onkeypress(jdi_nahoru, "w")
okno.onkeypress(jdi_dolu, "s")
okno.onkeypress(jdi_doleva, "a")
okno.onkeypress(jdi_doprava, "d")
okno.onkeypress(toggle_pauza, "p")
okno.onkeypress(restart, "r")
okno.onkeypress(skin_1, "1")
okno.onkeypress(skin_2, "2")
okno.onkeypress(skin_3, "3")

# ============================================================
# ========================= GAME FLOW ========================
# ============================================================

def klik_na_tlacitko(x, y):
    if not hra_bezi and (-70 <= x <= 70 and -90 <= y <= -35):
        spustit_hru()


okno.onclick(klik_na_tlacitko)


def spustit_hru():
    global hra_bezi, pauza, skore, rychlost_ms, high_score

    hra_bezi = True
    pauza = False
    skore = 0
    rychlost_ms = 90
    high_score = nacti_high_score()

    menu_napis.clear()
    tlacitko.clear()
    tlacitko_text.clear()
    high_score_text.clear()
    hrac_text.clear()

    aplikuj_skin_na_objekty()

    hlava.showturtle()
    jidlo.showturtle()

    hlava.goto(0, POSUN_HRY_Y)
    hlava.direction = "stop"

    vycisti_telo()
    spawn_jidlo()
    update_skore()
    update_info("Pauza (P) • Restart (R) • Skins 1/2/3")
    aktualizuj_oblicej_hada()

    tick()


def game_over(do_menu=True):
    global hra_bezi, skore, high_score

    if hra_bezi:
        uloz_skore(skore)

    high_score = nacti_high_score()
    hra_bezi = False
    hlava.direction = "stop"
    hlava.goto(0, POSUN_HRY_Y)
    hlava.hideturtle()
    jidlo.hideturtle()
    jidlo_ikona.clear()
    oko_L.hideturtle()
    oko_P.hideturtle()
    jazyk.hideturtle()
    vycisti_telo()
    update_skore()
    update_info("GAME OVER • klikni START pro novou hru • Skins 1/2/3")

    if do_menu:
        vykresli_menu()


def pohyb_hlavy():
    if hlava.direction == "nahoru":
        hlava.sety(hlava.ycor() + VELIKOST_KROKU)
    elif hlava.direction == "dolu":
        hlava.sety(hlava.ycor() - VELIKOST_KROKU)
    elif hlava.direction == "doleva":
        hlava.setx(hlava.xcor() - VELIKOST_KROKU)
    elif hlava.direction == "doprava":
        hlava.setx(hlava.xcor() + VELIKOST_KROKU)


def zrychli():
    global rychlost_ms
    rychlost_ms = max(45, 90 - (skore // 50) * 5)


def tick():
    global skore

    if not hra_bezi:
        okno.update()
        return

    if pauza:
        okno.update()
        okno.ontimer(tick, 80)
        return

    for i in range(len(telo) - 1, 0, -1):
        telo[i].goto(telo[i - 1].xcor(), telo[i - 1].ycor())
        telo_smer[i] = telo_smer[i - 1]

    if len(telo) > 0:
        telo[0].goto(hlava.xcor(), hlava.ycor())
        telo_smer[0] = hlava.direction

    for i, seg in enumerate(telo):
        seg.setheading(smer_na_heading(telo_smer[i]))

    pohyb_hlavy()
    aktualizuj_oblicej_hada()

    if (
        hlava.xcor() < HRACI_MIN_X or hlava.xcor() > HRACI_MAX_X or
        hlava.ycor() < HRACI_MIN_Y or hlava.ycor() > HRACI_MAX_Y
    ):
        game_over(do_menu=True)
        okno.update()
        return

    if hlava.distance(jidlo) < 1:
        skore += 10
        update_skore()
        zrychli()

        jidlo.shapesize(1.2, 1.2)
        okno.update()
        jidlo.shapesize(0.8, 0.8)

        f = max(0.55, 1.0 - (len(telo) * 0.03))
        barva = ztmav_barvu(skin["body"], f)

        novy = turtle.Turtle()
        novy.speed(0)
        novy.shape("square")
        novy.shapesize(0.70, 1.15)
        novy.color(barva)
        novy.penup()
        novy.setheading(smer_na_heading(hlava.direction))
        telo.append(novy)
        telo_smer.append(hlava.direction)

        spawn_jidlo()

    for seg in telo:
        if seg.distance(hlava) < 1:
            game_over(do_menu=True)
            okno.update()
            return

    okno.update()
    okno.ontimer(tick, rychlost_ms)


# ============================================================
# ======================= START PROGRAMU =====================
# ============================================================

vykresli_menu()
okno.mainloop()
# nekonečná smyčka okna - bez toho by se program hned ukončil
okno.mainloop()
