import cloudscraper
import pandas as pd
import io
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Gestione percorsi per Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Assicuriamoci che la cartella static esista
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

def run_all_scrapers():
    # Browser simulato per non essere bloccati dai siti
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )
    
    # 1. RANKING (SINGOLO E DOPPIO)
    urls = {
        "singolo": "https://live-tennis.eu",
        "doppio": "https://live-tennis.eu"
    }
    
    for tipo, url in urls.items():
        try:
            print(f"Inizio scraping {tipo}...")
            r = scraper.get(url, timeout=20)
            tabelle = pd.read_html(io.StringIO(r.text), keep_default_na=False)
            
            for df in tabelle:
                # La tabella ranking ha solitamente molte colonne (almeno 10)
                if len(df.columns) >= 10:
                    # Filtriamo le righe che hanno un numero di ranking valido nella prima colonna
                    df_util = df[pd.to_numeric(df.iloc[:, 0], errors='coerce').notnull()].head(10).copy()
                    
                    if not df_util.empty:
                        # Selezioniamo le colonne: Rank, Giocatrice, Paese, Punti Totali
                        ranking_finale = df_util.iloc[:, [0, 3, 5, 6]]
                        ranking_finale.columns = ['Rank', 'Giocatrice', 'Paese', 'Punti Totali']
                        
                        nome_file = "classifica_web.html" if tipo == "singolo" else "classifica_doppio_web.html"
                        path_salvataggio = os.path.join(STATIC_DIR, nome_file)
                        
                        ranking_finale.to_html(path_salvataggio, index=False, classes='wta-style', border=0, justify='center')
                        print(f"Salvataggio {tipo} completato!")
                        break
        except Exception as e:
            print(f"Errore ranking {tipo}: {e}")

    # 2. NEWS SCRAPER (UBITENNIS)
    notizie_html = ""
    try:
        print("Inizio scraping news...")
        url_news = "https://www.ubitennis.com"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r_news = requests.get(url_news, headers=headers, timeout=15)
        soup = BeautifulSoup(r_news.text, 'html.parser')
        
        count = 0
        for a in soup.find_all('a', href=True):
            titolo = a.get_text().strip()
            link = a['href']
            
            # Filtro per Jasmine Paolini e lunghezza minima titolo
            if "paolini" in titolo.lower() and len(titolo) > 25:
                # Gestione link relativi
                if link.startswith('/'):
                    link = "https://www.ubitennis.com" + link
                
                notizie_html += f'''
                <a href="{link}" target="_blank" class="news-item">
                    <div class="news-content">
                        <span class="news-source">Ubitennis</span>
                        <span class="news-title">{titolo[:80]}...</span>
                        <span class="news-time">{datetime.now().strftime('%d %b')}</span>
                    </div>
                </a>'''
                count += 1
                if count >= 8: break # Limite a 8 notizie

        if not notizie_html:
            notizie_html = '<p style="color:white; padding:10px;">Nessuna notizia recente trovata.</p>'
            
        with open(os.path.join(STATIC_DIR, "news_section.html"), "w", encoding="utf-8") as f:
            f.write(notizie_html)
        print("Salvataggio news completato!")

    except Exception as e:
        print(f"Errore news: {e}")

if __name__ == "__main__":
    run_all_scrapers()
