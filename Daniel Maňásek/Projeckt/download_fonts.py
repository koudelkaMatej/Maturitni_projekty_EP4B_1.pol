"""
Spust jednou pro stazeni fontu:
  py download_fonts.py

Po spusteni bude hra fungovat plne offline.
"""
import urllib.request, os, re

FONTS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'fonts')
os.makedirs(FONTS_DIR, exist_ok=True)

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
JS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'js')

def get(url, path, label):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()
        with open(path, 'wb') as f:
            f.write(data)
        print(f'  OK  {label} ({len(data)//1024} kB)')
        return True
    except Exception as e:
        print(f'  CHYBA  {label}: {e}')
        return False

print('\nStahuji fonty a knihovny...\n')

# Chart.js
get('https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js',
    os.path.join(JS_DIR, 'chart.umd.min.js'), 'Chart.js')

# Fetch font CSS and extract woff2 URLs
css_url = 'https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Outfit:wght@400;600;700&display=swap'
req = urllib.request.Request(css_url, headers={'User-Agent': UA})
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        css = r.read().decode('utf-8')

    urls = re.findall(r'url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)', css)
    families = re.findall(r"font-family: '([^']+)'", css)

    local_css = css
    for i, url in enumerate(urls):
        fname = f'font_{i}.woff2'
        fpath = os.path.join(FONTS_DIR, fname)
        if get(url, fpath, f'font_{i}.woff2'):
            local_css = local_css.replace(url, f"../fonts/{fname}")

    with open(os.path.join(FONTS_DIR, 'fonts.css'), 'w', encoding='utf-8') as f:
        f.write(local_css)
    print('  OK  fonts.css (lokalni CSS)')
except Exception as e:
    print(f'  CHYBA  fonty: {e}')

print('\nHotovo! Restartuj Flask (py app.py) a hra pojede offline.\n')
