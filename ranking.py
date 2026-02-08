import cloudscraper
import pandas as pd
import io

def prendi_ranking_wta_live():
    url = "https://live-tennis.eu"
    # User-Agent super realistico per bypassare i blocchi 403
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )
    
    try:
        response = scraper.get(url, timeout=25)
        # Forza il parser lxml (più veloce su Render)
        tabelle = pd.read_html(io.StringIO(response.text), engine='lxml')
        
        for df in tabelle:
            # Cerchiamo la tabella che ha almeno 10 colonne (quella del ranking)
            if len(df.columns) >= 10:
                df_util = df.copy()
                # Pulizia righe: teniamo solo quelle con un numero di rank
                df_util = df_util[pd.to_numeric(df_util.iloc[:, 0], errors='coerce').notnull()].head(10)
                
                # Selezioniamo le tue colonne originali (0, 3, 5, 6)
                ranking_finale = df_util.iloc[:, [0, 3, 5, 6]]
                ranking_finale.columns = ['Rank', 'Giocatrice', 'Paese', 'Punti Totali']
                return ranking_finale
        return "Tabella non trovata"
    except Exception as e:
        return f"Errore: {e}"

    except Exception as e:
        return f"Errore: {e}"



