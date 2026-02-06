import cloudscraper
import pandas as pd
import io
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Percorsi per Render (usiamo la cartella static del progetto)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

def run_all_scrapers():
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    
    # --- 1. RANKING SINGOLO (Tuo codice funzionante) ---
    try:
        print("Scraping Singolo...")
        url_s = "https://live-tennis.eu"
        resp_s = scraper.get(url_s, timeout=20)
        tabs_s = pd.read_html(io.StringIO(resp_s.text), keep_default_na=False)
        for df in tabs_s:
            if len(df.columns) >= 10:
                nomi = df.iloc[:, 3].astype(str).to_string()
                if any(x in nomi for x in ["Paolini", "Swiatek", "Świątek"]):
                    df_util = df[pd.to_numeric(df.iloc[:, 0], errors='coerce').notnull()].head(10).copy()
                    # Selezione colonne 0,3,5,6 come richiesto
                    ranking = df_util.iloc[:, [0, 3, 5, 6]]
                    ranking.columns = ['Rank', 'Giocatrice', 'Paese', 'Punti Totali']
                    html = ranking.to_html(index=False, classes='wta-style', border=0, justify='center')
                    with open(os.path.join(STATIC_DIR, "classifica_web.html"), "w", encoding="utf-8") as f:
                        f.write(html)
                    print("OK Singolo!")
                    break
    except Exception as e: print(f"Errore Singolo: {e}")

    # --- 2. RANKING DOPPIO (Tuo codice funzionante) ---
    try:
        print("Scraping Doppio...")
        url_d = "https://live-tennis.eu/it/classifica-wta-doppio-live"
        resp_d = scraper.get(url_d, timeout=20)
        tabs_d = pd.read_html(io.StringIO(resp_d.text), keep_default_na=False)
        for df in tabs_d:
            if len(df.columns) >= 8:
                nomi = df.iloc[:, 3].astype(str).to_string()
                if any(x in nomi for x in ["Errani", "Paolini", "Hsieh"]):
                    df_util = df[pd.to_numeric(df.iloc[:, 0], errors='coerce').notnull()].head(10).copy()
                    # Selezione colonne 0,3,5,6 come richiesto
                    ranking = df_util.iloc[:, [0, 3, 5, 6]]
                    ranking.columns = ['Rank', 'Giocatrice', 'Paese', 'Punti Totali']
                    html = ranking.to_html(index=False, classes='wta-style-doppio', border=0, justify='center')
                    with open(os.path.join(STATIC_DIR, "classifica_doppio_web.html"), "w", encoding="utf-8") as f:
                        f.write(html)
                    print("OK Doppio!")
                    break
    except Exception as e: print(f"Errore Doppio: {e}")

    # --- 3. NEWS (Tuo codice funzionante) ---
    print("Scraping News...")
    notizie = []
    link_visti = set()
    fonti = [
        {"url": "https://www.oasport.it", "fonte": "OA Sport"},
        {"url": "https://www.sportmediaset.mediaset.it", "fonte": "SportMediaset"},
        {"url": "https://www.corrieredellosport.it", "fonte": "Corriere dello Sport"},
        {"url": "https://www.supertennis.tv", "fonte": "SuperTennis"},
        {"url": "https://www.ubitennis.com", "fonte": "Ubitennis"},
        {"url": "https://www.eurosport.it", "fonte": "Eurosport"}
    ]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    for f in fonti:
        try:
            r = requests.get(f['url'], headers=headers, timeout=12)
            r.encoding = 'utf-8'
            soup = BeautifulSoup(r.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                titolo = a.get_text().strip()
                link = a['href']
                if link.startswith('/'): link = requests.compat.urljoin(f['url'], link)
                if "paolini" in titolo.lower() or "paolini" in link.lower():
                    if any(x in link for x in ["/2024/", "/2025/11/"]): continue
                    if link not in link_visti and len(titolo) > 25:
                        img_url = "https://via.placeholder.com"
                        img_tag = a.find('img') or a.find_next('img')
                        if img_tag:
                            src = img_tag.get('data-src') or img_tag.get('src')
                            if src and not src.startswith('data:image'): img_url = requests.compat.urljoin(f['url'], src)
                        notizie.append({'titolo': titolo[:95], 'link': link, 'fonte': f['fonte'], 'data': datetime.now().strftime('%d %b %H:%M'), 'immagine': img_url})
                        link_visti.add(link)
        except: continue
    
    html_news = '<div class="news-grid">'
    for n in notizie[:10]:
        html_news += f'''
        <a href="{n['link']}" target="_blank" class="news-item">
            <div class="news-content">
                <span class="news-source">{n['fonte']}</span>
                <span class="news-title">{n['titolo']}</span>
                <span class="news-time">{n['data']}</span>
            </div>
            <div class="news-image-container"><img src="{n['immagine']}" alt="News" loading="lazy"></div>
        </a>'''
    html_news += '</div>'
    with open(os.path.join(STATIC_DIR, "news_section.html"), "w", encoding="utf-8") as f_out:
        f_out.write(html_news)
    print("Tutto completato con successo!")

if __name__ == "__main__":
    run_all_scrapers()
