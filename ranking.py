import cloudscraper
import pandas as pd
import io
import os

def prendi_ranking_wta_live():
    url = "https://live-tennis.eu"
    # Simuliamo un browser reale per non essere bloccati da Render
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome','platform': 'windows','mobile': False}
    )
    
    try:
        response = scraper.get(url, timeout=20)
        tabelle = pd.read_html(io.StringIO(response.text), keep_default_na=False)
        
        for df in tabelle:
            if len(df.columns) >= 10:
                nomi_test = df.iloc[:, 3].astype(str).to_string()
                
                if "Paolini" in nomi_test or "Swiatek" in nomi_test:
                    df_util = df[pd.to_numeric(df.iloc[:, 0], errors='coerce').notnull()].head(10).copy()
                    ranking_finale = df_util.iloc[:, [0, 3, 5, 6]]
                    ranking_finale.columns = ['Rank', 'Giocatrice', 'Paese', 'Punti Totali']
                    return ranking_finale
        return None
    except Exception as e:
        print(f"Errore Scraping: {e}")
        return None


