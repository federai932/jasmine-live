import cloudscraper
import pandas as pd
import io
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Cartella di output per il cloud
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)

def run_all_scrapers():
    scraper = cloudscraper.create_scraper()
    
    # 1. RANKING SINGOLO E DOPPIO
    urls = {
        "singolo": "https://live-tennis.eu",
        "doppio": "https://live-tennis.eu"
    }
    
    for tipo, url in urls.items():
        try:
            r = scraper.get(url)
            tabelle = pd.read_html(io.StringIO(r.text), keep_default_na=False)
            for df in tabelle:
                if len(df.columns) >= 10:
                    df_util = df[pd.to_numeric(df.iloc[:, 0], errors='coerce').notnull()].head(10).copy()
                    ranking_finale = df_util.iloc[:, [0, 3, 5, 6]]
                    ranking_finale.columns = ['Rank', 'Giocatrice', 'Paese', 'Punti']
                    fname = "classifica_web.html" if tipo == "singolo" else "classifica_doppio_web.html"
                    ranking_finale.to_html(os.path.join(STATIC_DIR, fname), index=False, classes='wta-style', border=0, justify='center')
                    break
        except Exception as e: print(f"Errore {tipo}: {e}")

    # 2. NEWS SCRAPER
    notizie = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    fonte_url = "https://www.ubitennis.com" # Esempio singola fonte per velocità
    try:
        r = requests.get(fonte_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            titolo = a.get_text().strip()
            if "paolini" in titolo.lower() and len(titolo) > 20:
                notizie.append(f'<a href="{a["href"]}" target="_blank" class="news-item">{titolo}</a>')
        with open(os.path.join(STATIC_DIR, "news_section.html"), "w", encoding="utf-8") as f:
            f.write("".join(notizie[:10]))
    except Exception as e: print(f"Errore News: {e}")

if __name__ == "__main__":
    run_all_scrapers()