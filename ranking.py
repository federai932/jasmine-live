import cloudscraper
import pandas as pd
import io

def prendi_ranking_wta_live():
    url = "https://live-tennis.eu"
    # User-Agent reale per evitare il blocco 403 su Render
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome','platform': 'windows','mobile': False}
    )
    
    try:
        response = scraper.get(url, timeout=20)
        # Usiamo lxml come parser perché è più robusto su Render
        tabelle = pd.read_html(io.StringIO(response.text), engine='lxml')
        
        for df in tabelle:
            if len(df.columns) >= 10:
                # Seleziona colonne: 0 (Rank), 3 (Nome), 5 (Paese), 6 (Punti)
                df_util = df[pd.to_numeric(df.iloc[:, 0], errors='coerce').notnull()].head(10).copy()
                ranking_finale = df_util.iloc[:, [0, 3, 5, 6]]
                ranking_finale.columns = ['Rank', 'Giocatrice', 'Paese', 'Punti Totali']
                return ranking_finale
        return "Tabella non trovata"
    except Exception as e:
        return f"Errore: {e}"


