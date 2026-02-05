import cloudscraper
import pandas as pd
import io
import os

# Definiamo il percorso statico in modo che Flask lo veda sempre
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

def run_all_scrapers():
    if not os.path.exists(STATIC_DIR):
        os.makedirs(STATIC_DIR)

    scraper = cloudscraper.create_scraper()
    
    # URL Classifica Singolare
    url = "https://live-tennis.eu"
    
    try:
        print("Scaricamento dati...")
        response = scraper.get(url, timeout=30)
        # Cerchiamo la tabella specifica per ID (più veloce e sicuro)
        tabelle = pd.read_html(io.StringIO(response.text))
        
        for df in tabelle:
            # Cerchiamo la tabella che ha almeno 10 colonne
            if len(df.columns) >= 10:
                # Pulizia righe: teniamo solo quelle con un numero di rank
                df = df[pd.to_numeric(df.iloc[:, 0], errors='coerce').notnull()].head(10)
                
                # Selezioniamo e rinominiamo le colonne fondamentali
                ranking = df.iloc[:, [0, 3, 5, 6]]
                ranking.columns = ['Rank', 'Giocatrice', 'Paese', 'Punti']
                
                # Salvataggio HTML
                path = os.path.join(STATIC_DIR, "classifica_web.html")
                ranking.to_html(path, index=False, border=0, classes='wta-style')
                print("File salvato con successo!")
                return True
        return False
    except Exception as e:
        print(f"Errore durante lo scraping: {e}")
        return False

if __name__ == "__main__":
    run_all_scrapers()
