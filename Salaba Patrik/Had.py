import turtle          # knihovna na jednoduchou grafiku a hry
import random          # kvůli náhodnému spawnování jídla
import sqlite3         # práce s databází SQLite
from datetime import datetime   # kvůli uložení aktuálního data a času

# =========================
#  Databáze
# =========================

# název databázového souboru
DB_NAME = "snake_game.db"

def vytvor_databazi():
    # připojení k databázi
    conn = sqlite3.connect(DB_NAME)

    # kurzor = přes něj posíláme SQL příkazy
    c = conn.cursor()

    # vytvoření tabulky hry, pokud ještě neexistuje
    # id = automatické číslo záznamu
    # skore = uložené skóre
    # datum = kdy byla hra dohraná
    c.execute("""
        CREATE TABLE IF NOT EXISTS hry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skore INTEGER NOT NULL,
            datum TEXT NOT NULL
        )
    """)

    # uloží změny do databáze
    conn.commit()

    # zavře spojení s databází
    conn.close()

def uloz_skore(skore: int):
    # otevře databázi
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # vloží do tabulky nové skóre a aktuální datum + čas
    c.execute("INSERT INTO hry (skore, datum) VALUES (?, ?)",
              (skore, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    # uloží změny
    conn.commit()

    # zavře databázi
    conn.close()

def nacti_high_score() -> int:
    # otevře databázi
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # najde nejvyšší skóre v tabulce
    # COALESCE zajistí, že když tam nic není, vrátí se 0 místo None
    c.execute("SELECT COALESCE(MAX(skore), 0) FROM hry")

    # fetchone vrátí jeden řádek, [0] vezme první hodnotu
    vysledek = c.fetchone()[0]

    # zavře databázi
    conn.close()

    # vrátí high score jako celé číslo
    return int(vysledek)

# hned při spuštění programu se vytvoří databáze a tabulka, pokud neexistují
vytvor_databazi()

# =========================
#  barva (gradient)
# =========================

def ztmav_barvu(hex_color: str, faktor: float) -> str:
    # tahle funkce ztmaví barvu
    # barva je zadaná jako hex, třeba "#00ff00"
    # faktor 1.0 = původní barva
    # faktor menší než 1 = tmavší verze

    # odstraní znak # z barvy
    hex_color = hex_color.lstrip("#")

    # rozseká barvu na RGB složky a převede z hex do čísla
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # každou složku ztmaví podle faktoru
    r = max(0, int(r * faktor))
    g = max(0, int(g * faktor))
    b = max(0, int(b * faktor))

    # vrátí znovu barvu jako hex string
    return f"#{r:02x}{g:02x}{b:02x}"

def smer_na_heading(direction: str) -> int:
    # převod textového směru na úhel otočení turtle objektu
    # nahoru = 90°, dolu = 270°, doleva = 180°, doprava = 0°
    return {"nahoru": 90, "dolu": 270, "doleva": 180, "doprava": 0}.get(direction, 0)

# =========================
#  Skins (1/2/3)
# =========================

# slovník všech skinů
# každý skin má svoje barvy pro pozadí, mřížku, hlavu hada, tělo, jídlo atd.
SKINS = {
    1: {  # klasický zelený styl
        "bg": "#f2e6c9",
        "grid": "#d6c8a3",
        "frame": "#1f3d2a",
        "head": "#0b5d3b",
        "body": "#2aa36b",
        "food": "#b30000",
        "food_icon": "🍎",
        "text": "#1f3d2a"
    },
    2: {  # neon styl
        "bg": "#101018",
        "grid": "#252545",
        "frame": "#7c5cff",
        "head": "#00ffd0",
        "body": "#00c8ff",
        "food": "#ff3df2",
        "food_icon": "✨",
        "text": "#d7d7ff"
    },
    3: {  # tmavý styl
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

# výchozí skin po spuštění hry
skin_id = 1

# sem se uloží aktuálně zvolený skin
skin = SKINS[skin_id]

# =========================
#  Okno
# =========================

# vytvoření hlavního okna hry
okno = turtle.Screen()

# název okna nahoře
okno.title("Hadi hra doufam ze si to nevytahnu")

# nastaví barvu pozadí podle skinu
okno.bgcolor(skin["bg"])

# velikost herního okna
okno.setup(width=600, height=600)

# tracer(0) vypne automatické překreslování
# obrazovka se pak obnovuje ručně přes okno.update()
# je to plynulejší a rychlejší
okno.tracer(0)

# =========================
#  Herní stav
# =========================

# o kolik pixelů se had posune při jednom kroku
VELIKOST_KROKU = 20

# hranice herního pole
MAX_XY = 290

# informace o tom, jestli hra běží
hra_bezi = False

# informace o tom, jestli je hra pozastavená
pauza = False

# aktuální skóre
skore = 0

# načtení nejlepšího skóre z databáze
high_score = nacti_high_score()

# rychlost hry v milisekundách
# menší číslo = rychlejší hra
rychlost_ms = 90

# =========================
#  UI text
# =========================

# želva, která vypisuje skóre nahoře
skore_text = turtle.Turtle()
skore_text.speed(0)
skore_text.color(skin["text"])
skore_text.penup()
skore_text.hideturtle()
skore_text.goto(0, 260)

# želva na informační text pod skóre
info_text = turtle.Turtle()
info_text.speed(0)
info_text.color(skin["text"])
info_text.penup()
info_text.hideturtle()
info_text.goto(0, 230)

def update_skore():
    # smaže starý text skóre
    skore_text.clear()

    # vypíše nové skóre a high score
    skore_text.write(f"Skóre: {skore}   High Score: {high_score}",
                     align="center", font=("Arial", 16, "bold"))

def update_info(text=""):
    # smaže starý informační text
    info_text.clear()

    # pokud je předaný nějaký text, vypíše ho
    if text:
        info_text.write(text, align="center", font=("Arial", 12, "normal"))

# želva na vykreslení rámečku okolo hřiště
ramecek = turtle.Turtle()
ramecek.hideturtle()
ramecek.speed(0)
ramecek.pensize(4)
ramecek.penup()

# želva na kreslení mřížky na pozadí
mrizka = turtle.Turtle()
mrizka.hideturtle()
mrizka.speed(0)
mrizka.pensize(1)
mrizka.penup()

def kresli_ramecek():
    # smaže starý rámeček
    ramecek.clear()

    # nastaví barvu rámečku podle skinu
    ramecek.color(skin["frame"])

    # přesune pero do levého dolního rohu herního pole
    ramecek.goto(-MAX_XY, -MAX_XY)

    # zapne kreslení
    ramecek.pendown()

    # nakreslí čtverec kolem celého hřiště
    for _ in range(4):
        ramecek.forward(MAX_XY * 2)
        ramecek.left(90)

    # zvedne pero, aby dál nekreslilo
    ramecek.penup()

def kresli_mrizku(krok=40):
    # smaže starou mřížku
    mrizka.clear()

    # nastaví barvu mřížky
    mrizka.color(skin["grid"])

    # kreslení svislých čar
    for x in range(-MAX_XY, MAX_XY + 1, krok):
        mrizka.goto(x, -MAX_XY)
        mrizka.pendown()
        mrizka.goto(x, MAX_XY)
        mrizka.penup()

    # kreslení vodorovných čar
    for y in range(-MAX_XY, MAX_XY + 1, krok):
        mrizka.goto(-MAX_XY, y)
        mrizka.pendown()
        mrizka.goto(MAX_XY, y)
        mrizka.penup()

# =========================
#  Menu
# =========================

# text s názvem hry v menu
menu_napis = turtle.Turtle()
menu_napis.hideturtle()
menu_napis.penup()
menu_napis.goto(0, 100)

# text pro high score v menu
high_score_text = turtle.Turtle()
high_score_text.hideturtle()
high_score_text.penup()
high_score_text.goto(0, 30)

# želva na vykreslení tlačítka START
tlacitko = turtle.Turtle()
tlacitko.hideturtle()
tlacitko.penup()
tlacitko.pensize(3)

# text uvnitř tlačítka
tlacitko_text = turtle.Turtle()
tlacitko_text.hideturtle()
tlacitko_text.penup()

def vykresli_menu():
    global high_score

    # nastaví pozadí podle skinu
    okno.bgcolor(skin["bg"])

    # vymaže staré menu prvky
    menu_napis.clear()
    high_score_text.clear()
    tlacitko.clear()
    tlacitko_text.clear()

    # vymaže info text
    update_info("")

    # smaže text skóre
    skore_text.clear()

    # znovu nakreslí pozadí hřiště
    kresli_mrizku()
    kresli_ramecek()

    # z databáze se načte aktuální high score
    high_score = nacti_high_score()

    # nastaví barvy textů a tlačítka
    menu_napis.color(skin["text"])
    high_score_text.color(skin["text"])
    tlacitko.color(skin["frame"])
    tlacitko_text.color(skin["text"])

    # nadpis hry
    menu_napis.write(" Hadi Gameska! ", align="center", font=("Arial", 28, "bold"))

    # výpis nejvyššího skóre
    high_score_text.write(f"High Score: {high_score}", align="center", font=("Arial", 18, "normal"))

    # nastaví pozici tlačítka start
    tlacitko.goto(-70, -70)

    # začne kreslit obdélník tlačítka
    tlacitko.pendown()
    tlacitko.begin_fill()

    # výplň tlačítka podle skinu
    tlacitko.fillcolor("#b6f2c3" if skin_id == 1 else "#2a2a3a" if skin_id == 2 else "#1d2a22")

    # nakreslí obdélník
    for _ in range(2):
        tlacitko.forward(140)
        tlacitko.left(90)
        tlacitko.forward(55)
        tlacitko.left(90)

    # ukončí výplň tlačítka
    tlacitko.end_fill()
    tlacitko.penup()

    # text START do tlačítka
    tlacitko_text.goto(0, -55)
    tlacitko_text.write("START", align="center", font=("Arial", 18, "bold"))

    # malá nápověda dole
    update_info("Skins: 1 / 2 / 3   |   Pauza (P)  Restart (R)")

# =========================
#  Herní objekty
# =========================

# hlavní objekt hada - hlava
hlava = turtle.Turtle()
hlava.speed(0)
hlava.shape("square")
hlava.shapesize(1.10, 1.10)
hlava.color(skin["head"])
hlava.penup()
hlava.goto(0, 0)

# sem se ukládá směr pohybu hlavy
hlava.direction = "stop"

# na začátku je hlava schovaná, protože se nejdřív zobrazí menu
hlava.hideturtle()

# objekt jídla
jidlo = turtle.Turtle()
jidlo.speed(0)
jidlo.shape("circle")
jidlo.shapesize(0.8, 0.8)
jidlo.color(skin["food"])
jidlo.penup()
jidlo.goto(0, 100)
jidlo.hideturtle()

# zvláštní želva na ikonku jídla
# třeba jablko, hvězdička nebo lebka
jidlo_ikona = turtle.Turtle()
jidlo_ikona.hideturtle()
jidlo_ikona.penup()

def nastav_jidlo_ikonu():
    # smaže starou ikonku
    jidlo_ikona.clear()

    # nastaví barvu textu
    jidlo_ikona.color(skin["food"])

    # přesune ikonku na pozici jídla
    # -10 v ose y je jen kvůli tomu, aby text seděl opticky líp
    jidlo_ikona.goto(jidlo.xcor(), jidlo.ycor() - 10)

    # vypíše ikonku jídla
    jidlo_ikona.write(skin["food_icon"], align="center", font=("Arial", 18, "bold"))

# Oči hada

# levé oko
oko_L = turtle.Turtle()
oko_L.hideturtle()
oko_L.speed(0)
oko_L.shape("circle")
oko_L.shapesize(0.22, 0.22)
oko_L.color("black")
oko_L.penup()

# pravé oko
oko_P = turtle.Turtle()
oko_P.hideturtle()
oko_P.speed(0)
oko_P.shape("circle")
oko_P.shapesize(0.22, 0.22)
oko_P.color("black")
oko_P.penup()

# Jazyk hada
jazyk = turtle.Turtle()
jazyk.hideturtle()
jazyk.speed(0)
jazyk.shape("square")
jazyk.shapesize(0.10, 0.55)
jazyk.color(skin["food"])
jazyk.penup()

def aktualizuj_oblicej_hada():
    # když hra neběží, obličej hada nebude vidět
    if not hra_bezi:
        oko_L.hideturtle()
        oko_P.hideturtle()
        jazyk.hideturtle()
        return

    # když hra běží, oči se zobrazí
    oko_L.showturtle()
    oko_P.showturtle()

    # vezme aktuální souřadnice hlavy
    x, y = hlava.xcor(), hlava.ycor()

    # podle směru pohybu nastaví pozice očí
    # tím pádem to vypadá, že se had kouká směrem, kam jede
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

        # náhodně se občas ukáže jazyk
        if random.random() < 0.22:
            jazyk.showturtle()
            jazyk.setheading(180)
            jazyk.goto(x - 14, y)
        else:
            jazyk.hideturtle()

    elif hlava.direction == "doprava":
        oko_L.goto(x + 6, y + 6)
        oko_P.goto(x + 6, y - 6)

        # náhodně se občas ukáže jazyk
        if random.random() < 0.22:
            jazyk.showturtle()
            jazyk.setheading(0)
            jazyk.goto(x + 14, y)
        else:
            jazyk.hideturtle()

    else:
        # když had stojí, oči budou klasicky nahoře
        oko_L.goto(x - 6, y + 6)
        oko_P.goto(x + 6, y + 6)
        jazyk.hideturtle()

# seznam všech segmentů těla
telo = []

# seznam směrů pro jednotlivé segmenty těla
# je to kvůli tomu, aby se každý segment správně natočil
telo_smer = []

def vycisti_telo():
    global telo, telo_smer

    # všechny segmenty odsuneme mimo obrazovku a schováme
    for seg in telo:
        seg.goto(1000, 1000)
        seg.hideturtle()

    # vynulují se seznamy
    telo = []
    telo_smer = []

def nahodna_pozice_na_mrizce():
    # vybere náhodnou pozici na mřížce
    # krok je 20 pixelů, aby vše sedělo přesně do políček
    x = random.randrange(-MAX_XY + 10, MAX_XY - 10, VELIKOST_KROKU)
    y = random.randrange(-MAX_XY + 10, MAX_XY - 10, VELIKOST_KROKU)
    return x, y

def spawn_jidlo():
    while True:
        # zkusí náhodnou pozici
        x, y = nahodna_pozice_na_mrizce()

        # jídlo nesmí spawnout přímo na hlavě
        if abs(hlava.xcor() - x) < 1 and abs(hlava.ycor() - y) < 1:
            continue

        ok = True

        # jídlo nesmí spawnout ani na těle
        for seg in telo:
            if abs(seg.xcor() - x) < 1 and abs(seg.ycor() - y) < 1:
                ok = False
                break

        # pokud je pozice v pohodě, nastaví se tam jídlo
        if ok:
            jidlo.goto(x, y)
            nastav_jidlo_ikonu()
            return

def aplikuj_skin_na_objekty():
    # přebarví všechno podle nově zvoleného skinu
    okno.bgcolor(skin["bg"])
    skore_text.color(skin["text"])
    info_text.color(skin["text"])
    menu_napis.color(skin["text"])
    high_score_text.color(skin["text"])

    hlava.color(skin["head"])
    jidlo.color(skin["food"])
    jazyk.color(skin["food"])

    # překreslí pozadí
    kresli_mrizku()
    kresli_ramecek()

    # přebarví tělo hada
    # každý další dílek je trochu tmavší
    for i, seg in enumerate(telo):
        f = max(0.55, 1.0 - (i * 0.03))
        seg.color(ztmav_barvu(skin["body"], f))

    # pokud hra běží, překreslí se i další věci
    if hra_bezi:
        nastav_jidlo_ikonu()
        aktualizuj_oblicej_hada()
        update_skore()

def nastav_skin(nove_id: int):
    global skin_id, skin

    # když skin neexistuje, nic se nestane
    if nove_id not in SKINS:
        return

    # uloží nové id skinu
    skin_id = nove_id

    # načte nový skin ze slovníku
    skin = SKINS[skin_id]

    # přebarví herní objekty
    aplikuj_skin_na_objekty()

    # když hra neběží, znovu vykreslí menu
    if not hra_bezi:
        vykresli_menu()

# zkratky pro klávesy 1, 2, 3
def skin_1(): nastav_skin(1)
def skin_2(): nastav_skin(2)
def skin_3(): nastav_skin(3)

# =========================
#  Ovládání
# =========================

def jdi_nahoru():
    # had nesmí otočit rovnou do opačného směru
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

    # když hra neběží, pauza nedává smysl
    if not hra_bezi:
        return

    # přepne stav pauzy
    pauza = not pauza

    # vypíše info podle toho, jestli je hra pauznutá
    update_info("PAUZA (P) • Restart (R) • Skins 1/2/3" if pauza else "Pauza (P) • Restart (R) • Skins 1/2/3")

def restart():
    # restart funguje jen během hry
    if hra_bezi:
        game_over(do_menu=False)
        spustit_hru()

# začne poslouchat klávesnici
okno.listen()

# šipky
okno.onkeypress(jdi_nahoru, "Up")
okno.onkeypress(jdi_dolu, "Down")
okno.onkeypress(jdi_doleva, "Left")
okno.onkeypress(jdi_doprava, "Right")

# WASD
okno.onkeypress(jdi_nahoru, "w")
okno.onkeypress(jdi_dolu, "s")
okno.onkeypress(jdi_doleva, "a")
okno.onkeypress(jdi_doprava, "d")

# další ovládání
okno.onkeypress(toggle_pauza, "p")
okno.onkeypress(restart, "r")
okno.onkeypress(skin_1, "1")
okno.onkeypress(skin_2, "2")
okno.onkeypress(skin_3, "3")

# =========================
#  Game flow
# =========================

def klik_na_tlacitko(x, y):
    # kliknutí myší do oblasti tlačítka START
    # pokud hra neběží a klikneš do tlačítka, spustí se hra
    if not hra_bezi and (-70 <= x <= 70 and -70 <= y <= -15):
        spustit_hru()

# registrace kliknutí myší
okno.onclick(klik_na_tlacitko)

def spustit_hru():
    global hra_bezi, pauza, skore, rychlost_ms, high_score

    # nastaví výchozí stav nové hry
    hra_bezi = True
    pauza = False
    skore = 0
    rychlost_ms = 90
    high_score = nacti_high_score()

    # smaže menu
    menu_napis.clear()
    tlacitko.clear()
    tlacitko_text.clear()
    high_score_text.clear()

    # použije aktuální skin
    aplikuj_skin_na_objekty()

    # zobrazí hlavu a jídlo
    hlava.showturtle()
    jidlo.showturtle()

    # nastaví hada do výchozí pozice
    hlava.goto(0, 0)
    hlava.direction = "stop"

    # smaže staré tělo
    vycisti_telo()

    # spawnne nové jídlo
    spawn_jidlo()

    # překreslí texty
    update_skore()
    update_info("Pauza (P) • Restart (R) • Skins 1/2/3")

    # překreslí oči a jazyk
    aktualizuj_oblicej_hada()

    # spustí hlavní herní smyčku
    tick()

def game_over(do_menu=True):
    global hra_bezi, skore, high_score

    # když hra běžela, uloží se skóre do databáze
    if hra_bezi:
        uloz_skore(skore)

    # znovu načte high score
    high_score = nacti_high_score()

    # hra už neběží
    hra_bezi = False

    # had se zastaví
    hlava.direction = "stop"

    # vrátí hlavu na střed
    hlava.goto(0, 0)

    # schová herní objekty
    hlava.hideturtle()
    jidlo.hideturtle()
    jidlo_ikona.clear()

    # schová oči a jazyk
    oko_L.hideturtle()
    oko_P.hideturtle()
    jazyk.hideturtle()

    # smaže tělo
    vycisti_telo()

    # update textů
    update_skore()
    update_info("GAME OVER • klikni START pro novou hru • Skins 1/2/3")

    # pokud je zapnuté do_menu, vykreslí se zpátky menu
    if do_menu:
        vykresli_menu()

def pohyb_hlavy():
    # posune hlavu podle aktuálního směru
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

    # čím vyšší skóre, tím rychlejší hra
    # ale hra se nezrychlí pod 45 ms
    rychlost_ms = max(45, 90 - (skore // 50) * 5)

def tick():
    global skore

    # když hra neběží, jen překreslí okno a skončí
    if not hra_bezi:
        okno.update()
        return

    # když je pauza, nic se nehýbe, ale funkce se znovu zavolá za chvíli
    if pauza:
        okno.update()
        okno.ontimer(tick, 80)
        return

    # -------------------------
    # pohyb těla hada
    # -------------------------

    # pohyb segmentů od konce směrem dopředu
    # každý dílek převezme pozici předchozího
    for i in range(len(telo) - 1, 0, -1):
        telo[i].goto(telo[i - 1].xcor(), telo[i - 1].ycor())
        telo_smer[i] = telo_smer[i - 1]

    # první segment těla jde na předchozí pozici hlavy
    if len(telo) > 0:
        telo[0].goto(hlava.xcor(), hlava.ycor())
        telo_smer[0] = hlava.direction

    # nastaví natočení všech segmentů podle směru
    for i, seg in enumerate(telo):
        seg.setheading(smer_na_heading(telo_smer[i]))

    # posune hlavu
    pohyb_hlavy()

    # aktualizuje oči a jazyk
    aktualizuj_oblicej_hada()

    # -------------------------
    # kolize se stěnou
    # -------------------------

    # když had vyjede mimo rámeček, je konec hry
    if abs(hlava.xcor()) > MAX_XY or abs(hlava.ycor()) > MAX_XY:
        game_over(do_menu=True)
        okno.update()
        return

    # -------------------------
    # sebrání jídla
    # -------------------------

    # distance < 1 znamená, že had je prakticky přesně na jídle
    if hlava.distance(jidlo) < 1:
        # přičte body
        skore += 10

        # překreslí skóre
        update_skore()

        # případně zrychlí hru
        zrychli()

        # malý vizuální efekt, že jídlo "pukne"
        jidlo.shapesize(1.2, 1.2)
        okno.update()
        jidlo.shapesize(0.8, 0.8)

        # barva nového segmentu těla
        # každý další dílek je trochu tmavší
        f = max(0.55, 1.0 - (len(telo) * 0.03))
        barva = ztmav_barvu(skin["body"], f)

        # vytvoří nový segment těla
        novy = turtle.Turtle()
        novy.speed(0)
        novy.shape("square")

        # shapesize(výška, šířka)
        # proto je tělo spíš jako kapsle / obdélník
        novy.shapesize(0.70, 1.15)
        novy.color(barva)
        novy.penup()

        # nastaví otočení podle směru hlavy
        novy.setheading(smer_na_heading(hlava.direction))

        # přidá segment do seznamu těla
        telo.append(novy)

        # uloží se i jeho směr
        telo_smer.append(hlava.direction)

        # spawnne nové jídlo
        spawn_jidlo()

    # -------------------------
    # kolize s tělem
    # -------------------------

    # když hlava narazí do jakéhokoliv segmentu, konec hry
    for seg in telo:
        if seg.distance(hlava) < 1:
            game_over(do_menu=True)
            okno.update()
            return

    # překreslí celé okno
    okno.update()

    # za určitou dobu znovu zavolá tick()
    # to je vlastně hlavní smyčka celé hry
    okno.ontimer(tick, rychlost_ms)

# =========================
#  Start programu
# =========================

# po spuštění se nejdřív vykreslí menu
vykresli_menu()

# nekonečná smyčka okna - bez toho by se program hned ukončil
okno.mainloop()
