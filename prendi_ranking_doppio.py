import cloudscraper
import pandas as pd
import io
import os
from bs4 import BeautifulSoup

def prendi_ranking_wta_doppio_live():
    url = "https://live-tennis.eu/it/classifica-wta-doppio-live"
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    
    try:
        response = scraper.get(url, timeout=25)
        soup = BeautifulSoup(response.text, 'html.parser')
        tabelle = pd.read_html(io.StringIO(str(soup.find_all('table'))), keep_default_na=False)
        
        for df in tabelle:
            if len(df.columns) >= 8:
                nomi_test = df.iloc[:, 3].astype(str).to_string()
                if any(x in nomi_test for x in ["Errani", "Paolini", "Hsieh"]):
                    df_util = df[pd.to_numeric(df.iloc[:, 0], errors='coerce').notnull()].head(10).copy()
                    
                    ranking_finale = df_util.iloc[:, [0, 3, 5, 6]]
                    ranking_finale.columns = ['Rank', 'Giocatrice', 'Paese', 'Punti Totali']
                    
                    output_path = os.path.join(os.path.dirname(__file__), "static", "classifica_doppio_web.html")
                    ranking_finale.to_html(output_path, index=False, classes='wta-style-doppio', border=0, justify='center')
                    return "Classifica Doppio Aggiornata"
        return "Tabella Doppio non trovata"
    except Exception as e:
        return f"Errore Doppio: {e}"


