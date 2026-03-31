# Potápěč — Průvodce pro nové spolupracovníky

Vítejte v projektu Potápěč! Tento průvodce vám pomůže porozumět kódové základně, nastavení prostředí a tomu, jak efektivně přispět k vývoji hry.

---

## Obsah

1. [Přehled projektu](#project-overview)
2. [Nastavení prostředí](#environment-setup)
3. [Struktura projektu](#project-structure)
4. [Klíčové komponenty](#key-components)
5. [Pracovní postup vývoje](#development-workflow)
6. [Běžné úkoly](#common-tasks)
7. [Testování a QA](#testing--qa)
8. [Pracovní postup Gitu](#git-workflow)
9. [Komunikace a otázky](#communication--questions)

---

## Přehled projektu

**Potápěč** je roguelike arkádová hra s tématem potápění v hlubinách, postavená s využitím herního enginu **Pygame** a webového žebříčku **Flask**. Hra obsahuje:

- Tahovou navigaci v oceánu s řízením kyslíku
- Procedurálně generované překážky a setkání s tvory
- Rychlé události (QTE) pro úniky s vysokými sázkami
- Webový žebříček a ověřování hráčů
- Zvukový design s pohlcujícími zvukovými podněty

### Tech Stack
- **Hra**: Python 3.8+, Pygame 2.6+
- **Web**: Flask 3.1+, Werkzeug (autentizace), SQLite (databáze)
- **Prostředí**: PNG sprity, MP3/OGG ​​audio
- **Nasazení**: Připraveno pro Docker, běží na Windows/Mac/Linux

---

## Nastavení prostředí

### Předpoklady
- Python 3.8 nebo vyšší
- Git
- 2 GB volného místa na disku
- Textový editor nebo IDE (doporučeno VS Code)

### Krok 1: Klonování repozitáře
```bash
git clone <repository-url>
cd diveman
```

### Krok 2: Vytvoření virtuálního prostředí
```bash
python -m venv venv
source venv/bin/activate # macOS/Linux
# NEBO
venv\Scripts\Activate.ps1 # Windows PowerShell
```

### Krok 3: Instalace závislostí
```bash
pip install -r potapec/requirements.txt
```

### Krok 4: Ověření instalace
```bash
python -c "import pygame, flask; print('OK')"
```

### Krok 5: Spuštění hry (test)
```bash
python potapec/main.py
```
### Krok 6: Spuštění webového serveru (test)
```bash
cd potapec/web
python app.py
# Přejděte na http://127.0.0.1:5000
```

---

## Struktura projektu

```
diveman/
├── potapec/
│ ├── main.py # Vstupní bod hry
│ ├── settings.py # Globální konstanty (fyzika, míra objevování atd.)
│ ├── requirements.txt # Závislosti Pythonu
│ ├── MANUAL.md # Uživatelská příručka
│ ├── INVESTOR_PRESENTATION.md # Prezentace obchodních projektů
│ ├── database/
│ │ ├── __init__.py
│ │ └── database.py # SQLite ORM a správa skóre
│ ├── game/
│ │ ├── __init__.py
│ │ ├── game.py # Hlavní herní smyčka a stavový automat
│ │ ├── player.py # Logika hráčské postavy
│ │ ├── monsters.py # Umělá inteligence a chování tvorů
│ │ ├── bubbles.py # Generování kyslíkových bublin a fyzika
│ │ ├── obstacles.py # Generování útesů/stěn
│ │ ├── camera.py # Převod souřadnic obrazovky do světa
│ │ ├── collision.py # Detekce kolizí
│ │ ├── physics.py # Simulace pohybu a gravitace
│ │ ├── qte.py # Sekvence Quick Time Eventů
│ │ ├── sound.py # Správce zvuku
│ │ ├── environment.py # Barvy oceánu, přechody
│ │ ├── rasy.py # Vykreslení bioluminiscence (řas)
│ │ ├── menu.py # Hlavní menu UI
│ │ ├── savegame.py # Uložení/načtení stavu
│ │ └── settings.py # Konfigurace hry (fyzikální konstanty)
│ ├── web/
│ │ ├── app.py # Flask server
│ │ ├── static/
│ │ │ └── style.css # Styly webového rozhraní
│ │ └── templates/
│ │ └── index.html # Žebříček + přihlašovací UI
│ ├── assets/
│ │ ├── potápěč/ # Sprity hráče
│ │ ├── monstra/ # Sprity tvorů (žralok, chobotnice, želé atd.)
│ │ └── zvuky/ # Zvukové soubory (vodní bubliny, zvuky tvorů atd.)
│ └── test/
│ ├── test_player.py
│ ├── test_oxygen.py
│ ├── test_menu_cli.py
│ └── test_sound.py
└── [README.md, další kořenové soubory]
```
---

## Klíčové komponenty

### 1. Herní smyčka (`game/game.py`)

Srdce hry. Zvládá:
- Inicializaci a správu stavu
- Zpracování událostí (klávesnice, myš)
- Aktualizace fyziky (pohyb hráče, gravitace)
- Detekci kolizí
- Vznik monster a AI
- Logiku vyčerpání kyslíku
- Kreslení (renderování)

**Klíčové metody**:
- `run()`: Hlavní smyčka; odesílá do menu/game/gameover
- `game_loop(dt)`: Základní herní logika
- `reset_game()`: Inicializuje nový běh
- `draw()`: Renderuje všechny vizuální prvky

### 2. Hráč (`game/player.py`)

Představuje potápěče. Vlastnosti:
- Pozice (`world_x`, `world_y`)
- Rychlost (`velocity_x`, `velocity_y`)
- Hladina kyslíku
- Stav animace

**Klíčové metody**:
- `update()`: Použití fyzikálních omezení
- `rect()`: Ohraničující rámeček pro kolizi

### 3. Monstra (`game/monsters.py`)

3 typů tvorů:
- **Žralok**: Rychlý agresor, vysává kyslík
- **Chobotnice**: Střední hrozba, spouští QTE
- **Medúza**: Omráčí při kontaktu
**Klíčové metody**:
- `update(player)`: Logika a pohyb umělé inteligence
- `get_current_frame()`: Animační snímek pro vykreslování

### 4. Bubliny (`game/bubbles.py`)

Zóny pro regeneraci kyslíku. Vlastnosti:
- Generování procedur
- Detekce kolizí
- **NOVINKA**: Mechanika zmenšování (poloměr se zmenšuje, když je hráč uvnitř)

**Klíčové funkce**:
- `generate_bubbles()`: Vytvoření rozvržení bublin pro mapu
- `inside_bubble(player, bubble)`: Kontrola, zda je hráč v zóně

### 5. Webový server (`web/app.py`)

Backend Flask pro žebříček. Trasy:
- `/`: Vykreslení žebříčku + formuláře pro přihlášení/registraci
- `/signup`: Vytvoření uživatelského účtu
- `/login`: Ověření uživatele
- `/logout`: Vymazání relace
- `/submit`: Uložení herního skóre

**Databáze**: SQLite se schématem pro uživatele a skóre

### 6. Databáze (`database/database.py`)

ORM vrstva pro trvalá data:
- Ověřování uživatelů (hashovaná hesla)
- Ukládání skóre s časovými razítky
- Dotazy na žebříček
- Prořezávání dat (odstranění starých skóre)

---

## Vývojový postup

### 1. Vyberte úkol
- Zkontrolujte nástěnku **Problémy**, zda neobsahuje chyby, funkce nebo vylepšení
- Přiřaďte si úkol (nebo se zeptejte ve Slacku/Discord)
- Vytvořte větev: `git checkout -b feature/název-vaše-funkce`

### 2. Proveďte změny
- Upravte soubory ve svém editoru
- Často spusťte hru, abyste otestovali změny: `python potapec/main.py`
- Pro změny na webu, test serveru: `cd potapec/web && python app.py`

### 3. Zkontrolujte svou práci
- **Syntaxe**: `python -m py_compile potapec/game/game.py`
- **Jednotkové testy**: `python -m pytest potapec/test/` (pokud je k dispozici testovací sada)
- **Testování hry**: Zahrajte si hru a ověřte, zda vaše změny fungují podle očekávání

### 4. Potvrďte změny
```bash
git add .
git commit -m "feature: Přidat mechaniku zmenšování bublin"
```

### 5. Odeslat a vytvořit žádost o načtení
```bash
git push origin feature/název-vaše-funkce
```
- Vytvořit PR na GitHubu/GitLabu s jasným popisem
- Propojit všechny související problémy
- Požádat o kontrolu od hlavního vývojáře

### 6. Kontrola kódu a sloučení
- Reagovat na zpětnou vazbu a provést požadované změny
- Po schválení sloučit do větve `main`
- Smazat větev funkce

---

## Běžné úkoly

### Přidání nového typu monstra

1. **Definujte tvora v `game/monsters.py`**:
```python
class NewCreature(Monster):
def __init__(self, x, y):
super().__init__(x, y, 'new_creature')
self.speed = 2.5
self.o2_drain = 20

def update(self, player):
# Implementujte logiku AI
pass
```

2. **Vytvořte assets sprite**: Umístěte PNG do `assets/monsters/new_creature.png`

3. **Zaregistrujte v `game.py`**:
- Přidejte do `load_resources()` pro předběžné načtení sprite
- Přidejte do logiky spawnu `game_loop()`

4. **Test**: Spusťte hru a ověřte, zda se tvor zobrazuje a chová správně

### Úprava fyzikálních konstant

Všechny fyzikální hodnoty jsou v `game/settings.py`:
```python
GRAVITY_PX_PER_FRAME = ... # Jak rychle hráč padá
SWIM_UP_M_S = ... # Rychlost plavání nahoru
OXYGEN_DEPLETION_PER_S = ... # Rychlost odčerpávání kyslíku
BUBBLE_SHRINK_PER_SECOND = 15.0 # Rychlost zmenšování bubliny
```

Dolaďte, testujte a iterujte, dokud nebudete mít správný pocit. Vždy si všímejte změn ve zprávách commitu.

### Přidání nového zvukového efektu

1. **Export zvuku**: Vytvoření souboru MP3 nebo OGG

2. **Umístění do `assets/sounds/`**: Jasně pojmenování (např. `creature_roar.mp3`)

3. **Použití v kódu**:
```python
self.sound.play_sound('creature_roar')
```
4. **Test**: Spuštění hry a ověření přehrávání zvuku ve správný okamžik

### Aktualizace uživatelského rozhraní žebříčku

1. **Upravit `web/templates/index.html`**: Upravení struktury HTML

2. **Aktualizace `web/static/style.css`**: Přidání nebo úprava stylů

3. **Test lokálně**: `cd web && python app.py`, přejděte na `http://127.0.0.1:5000`
4. **Ověření responzivity**: Testování na různých velikostech obrazovky

---

## Testování a QA

### Spuštění testů
Pokud existují jednotkové testy:
```bash
cd potapec
python -m pytest test/ -v
```

### Kontrolní seznam manuálního QA

Před odesláním PR ověřte:
- [ ] Hra se spouští bez chyb
- [ ] Hráč se může pohybovat doleva/doprava/nahoru/dolů
- [ ] Kyslík se vyčerpává a obnovuje podle očekávání
- [ ] Příšery se objevují a chovají správně
- [ ] Bubliny se přiměřeně zvětšují a zmenšují
- [ ] Zvukové efekty se přehrávají na správné hlasitosti
- [ ] Navigace v menu funguje hladce
- [ ] Žebříček zobrazuje skóre správně
- [ ] Funkce přihlášení/registrace fungují
- [ ] Žádné chyby ani varování konzole (zkontrolujte výstup terminálu)

### Tipy pro výkon

- Profilujte se pomocí `cProfile`, pokud máte podezření na pomalý kód:
```python
import cProfile
cProfile.run('game.run()')
```
- Udržujte snímkovou frekvenci na 60 FPS; Vyhněte se náročným výpočtům v `game_loop()`
- Používejte `list.remove()` střídmě; pro filtrování upřednostňujte seznamové comprehensiony

---

## Git Workflow

### Pojmenování větví
- Funkce: `feature/add-new-monster`
- Opravy chyb: `bugfix/fix-oxygen-drain`
- Dokumentace: `docs/update-manual`

### Zprávy o potvrzení
```
[type]: Stručné shrnutí (imperativní, max. 50 znaků)

Delší vysvětlení, pokud je potřeba (72 znaků na řádek).
- Odrážky pro dílčí úkoly
- Referenční problémy: Opravy #123
```

Příklad:
```
funkce: Implementace mechaniky zmenšování bublin

- Bubliny se nyní zmenšují, když je hráč uvnitř
- Poloměr se snižuje o BUBBLE_SHRINK_PER_SECOND
- Bublina je odstraněna, když poloměr dosáhne minima
- Upravena BUBBLE_MIN_RADIUS v settings.py
```

---
## Komunikace a dotazy

### Kam se ptát
- **Slack/Discord**: #vývojový kanál pro rychlou pomoc
- **Problémy s GitHubem**: Pro diskuze o chybách nebo funkcích
- **Týdenní synchronizace**: Připojte se k našemu středečnímu stánku vývojářů (12:00 UTC)

### Klíčové kontakty
- **Vedoucí vývojář**: [Jméno] — Architektura, vyvážení hratelnosti
- **Umělec**: [Jméno] — Dotazy ohledně sprite a assetu
- **Zvuk**: [Jméno] — Integrace zvuku a SFX
- **Provoz**: [Jméno] — Server, databáze, nasazení

### Standardy pro kontrolu kódu

**Očekávané před sloučením**:
- ✅ Kód odpovídá stylu projektu (PEP 8 pro Python)
- ✅ Žádná nová varování ani chyby v IDE
- ✅ Zpráva o potvrzení je jasná a popisná
- ✅ Změny jsou testovány lokálně
- ✅ Popis PR odkazuje na související problémy

---

## Užitečné zdroje

- **Dokumentace Pygame**: https://www.pygame.org/docs/
- **Dokumentace k Flask**: https://flask.palletsprojects.com/
- **Průvodce stylem PEP 8**: https://www.python.org/dev/peps/pep-0008/
- **Git Cheat Sheet**: https://github.github.com/training-kit/

---

## Kontrolní seznam pro zaškolení

Do konce prvního týdne:
- [ ] Nastavení prostředí a lokální spuštění hry
- [ ] Prozkoumání struktury projektu a identifikace klíčových souborů
- [ ] Přečtení tohoto průvodce a souboru MANUAL.md
- [ ] Zadání a dokončení prvního snadného úkolu (např. „přidání nového zvukového efektu“)
- [ ] Odeslání prvního PR a obdržení zpětné vazby
- [ ] Seznámení s týmem a představení
- [ ] Připojení ke Slacku/Discord a účast na stand-upu

---

## Závěrečné poznámky

- **Buďte zvědaví**: Ptejte se a prozkoumávejte kódovou základnu
- **Testování často**: Během vývoje hru často spouštějte
- **Udržujte ji čistou**: Dodržujte styl kódu a udržujte commity atomické
- **Komunikujte**: Sdílejte pokrok v stand-upech a reagujte na zpětnou vazbu
- **Bavte se**: Toto je vášnivý projekt – užijte si cestu!

**Vítejte na palubě. Šťastné potápění! 🌊**

---

*Průvodce spolupracovníka Potápěč v1.0 | Poslední aktualizace: březen 2026*
