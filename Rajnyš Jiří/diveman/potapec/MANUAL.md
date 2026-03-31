# Potápěč — Uživatelská příručka

## Vítejte v hlubinách

Potápěč je dobrodružná hra s potápěním v hlubinách, kde se ponoříte do nejtemnějších hlubin oceánu. Spravujte svůj kyslík, vyhýbejte se nebezpečným tvorům a objevujte, jak hluboko se můžete ponořit.

---

## Začínáme

### Systémové požadavky
- **OS**: Windows, macOS nebo Linux
- **Python**: 3.8+
- **RAM**: minimálně 2 GB
- **Displej**: doporučeno 1920×1080 nebo vyšší

### Instalace

1. **Naklonujte nebo extrahujte projekt**
```bash
cd potapec
```

2. **Vytvořte virtuální prostředí**
```bash
python -m venv venv
source venv/bin/activate # Ve Windows: venv\Scripts\Activate.ps1
```

3. **Nainstalujte závislosti**
```bash
pip install -r requirements.txt
```

4. **Spusťte hru**
```bash
python potapec/main.py
```

---

## Ovládání hry

| Klávesa | Akce |
|-----|--------|
| **Šipky** | Pohyb vlevo/vpravo (mělká voda), nahoru/dolů (hluboká voda) |
| **Mezerník** | Nabití silového skoku (podržet a uvolnit v cílové hloubce) |
| **Myš** | Zaměření směru útoku (pohnout myší před uvolněním mezerníku) |
| **Šipky (v QTE)** | Postupujte podle pokynů na obrazovce během událostí Quick Time |
| **Esc** | Ukončení hry |
---

## Základní mechanika

### Správa kyslíku
- **Začátek**: 100 bodů kyslíku
- **Rychlost vyčerpání**: 2 body za sekundu ve vodě (vnější vzduchové bubliny)
- **Rychlost regenerace**: 7 bodů za sekundu ve vzduchových bublinách
- **Nebezpečí**: Kyslík dosáhne 0 → Konec hry

**Tip**: Sbírejte vzduchové bubliny pro dýchání a regeneraci kyslíku.

### Vzduchové bubliny
- **Vzhled**: Kulovité zóny ve vodě, které jemně září
- **Efekt**: Obnovují kyslík uvnitř
- **Zmenšují se**: Bubliny se zmenšují, čím déle v nich zůstáváte (nakonec zmizí)
- **Strategie**: Používejte je moudře – nezůstávejte příliš dlouho, jinak je ztratíte

### Bodování hloubky
- **Výpočet skóre**: Na základě maximální dosažené hloubky (v metrech)
- **Žebříček**: Sledují se a ukládají nejlepší skóre
- **Nejlepší hloubka**: Váš osobní rekord se ukládá pro budoucí pokusy

### Příšery a hrozby

#### Žralok
- **Chování**: Agresivní lovec; pronásleduje hráče vysokou rychlostí
- **Trest**: 15 bodů odvodu kyslíku za útok
- **Útěk**: Pohybujte se chaoticky, používejte překážky k narušení zorného pole

#### Chobotnice
- **Chování**: Inteligentní; pokusy o chycení a zdržení hráče
- **Výzva**: Spustí událost Quick Time (QTE) při chycení
- **Trest**: Ztráta 25 kyslíku, pokud je QTE neúspěšné
- **Zotavení**: Vyhrajte QTE a unikněte s minimálním poškozením

#### Medúza
- **Chování**: Pomalu se vznáší, ale při přiblížení rychle udeří
- **Efekt**: Omráčí hráče na 3–5 sekund
- **Dopad**: Během omráčení se nemůžete pohybovat; použijte to k úkrytu nebo plánování útěku

#### Ostatní tvorové
- **Fialové a červené druhy**: Další hrozby ve větších hloubkách
- **Mechanika**: Podobná výše uvedené; pozorujte chování a přizpůsobte se

---

## Strategie pro úspěch
### Počáteční fáze hry (0–50 m)
- Zvládněte ovládání před ponorem do hloubky
- Sbírejte všechny kyslíkové bubliny, na které narazíte
- Vyhýbejte se zbytečným setkáním s monstry
- Získejte sebevědomí pomocí mechaniky skoku

### Střední fáze hry (50–200 m)
- Monstra se objevují častěji
- Bubliny jsou vzácnější, proto je používejte strategicky
- Naučte se vzorce chování monster
- Používejte překážky (útesy) jako úkryt

### Hluboká fáze hry (200 m+)
- Zdroje jsou vzácné; plánujte každý pohyb
- Setkání s monstry jsou neustálá
- Řízení kyslíku je kritické
- Jedna chyba může ukončit váš běh

---

## Tipy a triky

1. **Míření při vysokých skokech**: Použijte systém míření myší k plánování silových skoků – podržte mezerník, pohněte myší na cíl, uvolněte.
2. **Načasování bublin**: Vstupujte do bublin pouze tehdy, když je kyslík pod 50 %, abyste maximalizovali regeneraci.
3. **Povědomí o monstrech**: Poslouchejte zvukové signály; často signalizují blízké hrozby.

4. **Sebevědomí QTE**: Během QTE v chobotnici zachovejte klid a přesně dodržujte sekvenci šipek.
5. **Používání překážek**: Útesy a skály poskytují přirozené bariéry – využijte je k úniku před predátory.
6. **Preference hudby**: V nastavení přepněte hudbu ve hře/v nabídce.

---

## Navigace v menu

### Hlavní menu
- **Přihlášení**: Přihlaste se pro uložení skóre do svého účtu
- **Registrace**: Vytvoření nového účtu
- **Nastavení**: Přepínání hudby, zvukových efektů a dalších možností
- **Žebříček**: Zobrazení nejlepších skóre a vašich osobních statistik

### Pozastavení během hry
- Stisknutím **Esc** se vrátíte do menu (aktuální relace je ztracena)
- Žádná funkce pozastavení ve hře – oceán na nikoho nečeká

---

## Konec hry a bodování

Když váš kyslík dosáhne 0:
- Obrazovka **Konec hry** zobrazuje vaši konečnou hloubku a skóre
- **Nejlepší skóre**: Zobrazí se váš osobní rekord
- **Stisknutím libovolné klávesy** se vrátíte do menu

### Odeslání žebříčku
- Vaše skóre se automaticky uloží, pokud jste přihlášeni
- Anonymní skóre vyžadují platný token API (pro webovou integraci)
- Zkontrolujte žebříček na webovém portálu pro globální žebříčky
---
## Řešení problémů

### Hra padá nebo se nespustí
1. Ověřte, zda je nainstalován Python 3.8+: `python --version`
2. Ujistěte se, že je nainstalován Pygame: `pip install pygame`
3. Zkontrolujte, zda jsou všechny soubory (obrázky, zvuky) v `potapec/assets/`

### Problémy se zvukem
- Ověřte, zda zvukové soubory existují v `potapec/assets/sounds/`
- Přepněte zvuk v nabídce, pokud dochází k závadám zvuku

### Problémy se zpožděním nebo výkonem
1. Zavřete aplikace na pozadí, abyste uvolnili RAM
2. V případě potřeby snižte rozlišení obrazovky
3. Aktualizujte ovladače grafické karty

### Webový portál se nenačítá
- Ujistěte se, že server Flask běží: `python potapec/web/app.py`
- Výchozí URL: `http://127.0.0.1:5000`
- Zkontrolujte, zda port 5000 není používán jinou aplikací

---

## Zpětná vazba a podpora

Pro problémy, návrhy nebo hlášení chyb:
- Zkontrolujte repozitář projektu nebo stránka s problémy na GitHubu
- Přispěvatelé a vývojáři rádi pomohou

---

**Hodně štěstí, potápěči. Hlubina čeká.**

*Potápěč — © 2026*