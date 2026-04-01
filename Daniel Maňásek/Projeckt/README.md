# 🃏 Pixel Blackjack — Webový Stand
### Školní maturitní projekt | Flask + SQLite + Python

---

## 📋 Obsah
1. [O projektu](#o-projektu)
2. [Technologie](#technologie)
3. [Instalace a spuštění](#instalace-a-spuštění)
4. [Struktura projektu](#struktura-projektu)
5. [Funkce](#funkce)
6. [Admin panel](#admin-panel)
7. [Přístup z mobilu / jiného počítače](#přístup-z-mobilu)
8. [Achievementy](#achievementy)

---

## O projektu

Pixel Blackjack je webová aplikace postavená na frameworku **Flask** (Python).
Slouží jako herní stand pro desktopovou pygame hru Pixel Blackjack.
Hráči se mohou registrovat, hrát blackjack přímo v prohlížeči,
sledovat statistiky, sbírat achievementy a porovnávat se na žebříčku.

---

## Technologie

| Technologie | Použití |
|-------------|---------|
| **Python 3.12** | Backend jazyk |
| **Flask 3.x** | Webový framework |
| **SQLite** | Databáze (soubor `stand.db`) |
| **Werkzeug** | Hashování hesel (bcrypt/scrypt) |
| **Jinja2** | HTML šablony |
| **Chart.js** | Graf statistik na profilu |
| **Web Audio API** | Zvukové efekty v prohlížeči |
| **Press Start 2P** | Pixel art font (Google Fonts) |

---

## Instalace a spuštění

### Požadavky
- Python 3.10 nebo novější
- pip (součást Pythonu)

### Kroky

**1. Nainstaluj Flask**
```bash
pip install flask
```

**2. Spusť aplikaci**
```bash
cd D:\2025\Projeckt
python app.py
```

**3. Otevři v prohlížeči**
```
http://127.0.0.1:5000
```

> ⚠️ Soubor `stand.db` se vytvoří automaticky při prvním spuštění.
> Admin účet se také vytvoří automaticky dle nastavení v `app.py`.

---

## Struktura projektu

```
Projeckt/
│
├── app.py                  # Hlavní Flask aplikace
├── stand.db                # SQLite databáze (auto-generovaná)
├── requirements.txt        # Závislosti
├── README.md               # Tato dokumentace
│
├── templates/              # HTML šablony (Jinja2)
│   ├── base.html           # Základní layout s navigací
│   ├── login.html          # Přihlášení a registrace
│   ├── game.html           # Herní stůl
│   ├── leaderboard.html    # Žebříček hráčů
│   ├── profile.html        # Profil, statistiky, achievementy
│   └── admin.html          # Admin panel
│
└── static/
    ├── css/
    │   └── style.css       # Veškeré styly
    ├── js/
    │   └── game.js         # Herní logika (JavaScript)
    └── img/
        ├── cards/          # Pixel art karty (52 + back)
        ├── chips/          # Pixel art žetony (10, 25, 50, 100)
        ├── casino_bg.png   # Pozadí přihlašovací stránky
        └── table_bg.png    # Dlaždice herního stolu
```

---

## Funkce

### 🎮 Hra
- Plná implementace pravidel Blackjacku
- Akce: **Hit**, **Stand**, **Double Down**
- Přirozený Blackjack s výplatou **3:2**
- Dealer hraje do 17 bodů
- Zvukové efekty přes Web Audio API
- Klávesové zkratky: `H` = Hit, `S` = Stand, `D` = Double, `Enter` = Deal

### 👤 Účty
- Registrace s heslem (min. 4 znaky)
- Přihlášení — hesla jsou hashována, nikdy se neukládají v čitelné podobě
- Každý hráč začíná s **500 žetony**
- Při bankrotu možnost dobití 500 žetonů

### 🎨 Profil
- Vlastní avatar — výběr z 16 emoji a 12 barev
- Graf výher / proher / remíz (Chart.js)
- Statistiky: hry, výhry, prohry, blackjacky, nejlepší výhra
- Historie posledních 20 her

### 🏆 Žebříček
- Top 20 hráčů seřazených podle počtu žetonů
- Zobrazení avataru, výher, úspěšnosti a počtu Blackjacků

---

## Admin panel

Admin účet se nastavuje přímo v `app.py`:

```python
ADMIN_USERNAME = 'tvoje_jmeno'
ADMIN_PASSWORD = 'tvoje_heslo'
```

> Po změně jména/hesla **restartuj** Flask — změna se projeví automaticky.

### Co admin může:

| Akce | Popis |
|------|-------|
| 🚫 Blokovat hráče | Hráč se nemůže přihlásit |
| ✅ Odblokovat hráče | Obnoví přístup |
| 💰 Reset žetonů | Nastaví hráči 500 žetonů |
| 🔄 Reset všeho | Smaže hry, achievementy, resetuje žetony |
| 🗑️ Smazat hráče | Nenávratně odstraní účet |

Admin panel je dostupný na `/admin` nebo přes tlačítko 👑 ADMIN v navigaci.

---

## Přístup z mobilu

Aby hra byla dostupná z mobilu nebo jiného počítače ve stejné WiFi síti:

**1.** V `app.py` změň poslední řádek:
```python
# Původní:
app.run(debug=True)

# Změň na:
app.run(debug=False, host='0.0.0.0', port=5000)
```

**2.** Zjisti svoji lokální IP adresu:
```bash
ipconfig
```
Hledej řádek **IPv4 Address** — např. `192.168.1.105`

**3.** Na mobilu nebo jiném počítači otevři:
```
http://192.168.1.105:5000
```

> ⚠️ Funguje pouze pokud jsou všechna zařízení na **stejné WiFi síti**.

---

## Achievementy

| Ikona | Název | Podmínka | Rarита |
|-------|-------|----------|--------|
| 🎮 | Začátečník | První hra | Běžné |
| ⚡ | Blackjack Mistr | Přirozený Blackjack | Vzácné |
| 💰 | Vysoký Sázkaře | Výhra 500+ žetonů | Epické |
| 🔥 | Vítězná série | 3 výhry za sebou | Vzácné |
| 🛡️ | Přeživší | Výhra s 21 (ne přirozený BJ) | Neobvyklé |
| ⭐ | Veterán | 10 odehraných her | Neobvyklé |
| 🔄 | Comeback | Výhra s méně než 100 žetony | Epické |
| ✌️ | Dvojnásobek | Výhra po zdvojení sázky | Neobvyklé |

---

## Autor

Školní maturitní projekt | 2025/2026
