import cloudscraper
import pandas as pd
import io
import os

def prendi_ranking_wta_live():
    url = "https://live-tennis.eu/it/classifica-wta-live"
    # Creiamo lo scraper
    scraper = cloudscraper.create_scraper()
    
    try:
        response = scraper.get(url)
        # Leggiamo con StringIO per evitare avvisi
        tabelle = pd.read_html(io.StringIO(response.text), keep_default_na=False)
        
        for df in tabelle:
            if len(df.columns) >= 10:
                nomi_test = df.iloc[:, 3].astype(str).to_string()
                
                if "Paolini" in nomi_test or "Swiatek" in nomi_test or "Świątek" in nomi_test:
                    df_util = df.copy()
                    df_util = df_util[pd.to_numeric(df_util.iloc[:, 0], errors='coerce').notnull()]
                    top_10 = df_util.head(10).copy()
                    
                    # Selezione colonne originale
                    ranking_finale = top_10.iloc[:, [0, 3, 5, 6]]
                    ranking_finale.columns = ['Rank', 'Giocatrice', 'Paese', 'Punti Totali']
                    
                    return ranking_finale

        return "Tabella WTA non trovata."
    except Exception as e:
        return f"Errore: {e}"

# --- PARTE ADATTATA PER RENDER ---
classifica_wta = prendi_ranking_wta_live()

if isinstance(classifica_wta, pd.DataFrame):
    html_string = classifica_wta.to_html(index=False, classes='wta-style', border=0, justify='center')
    
    # 1. Definiamo il percorso relativo alla cartella 'static' del server
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(BASE_DIR, "static", "classifica_web.html")
    
    # 2. Creiamo la cartella static se non esiste (fondamentale su Render)
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))
    
    # 3. Salvataggio UTF-8
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_string)
        
    print(f"\n[OK] File aggiornato su Render in: {output_path}")
else:
    print(f"\n[AVVISO] {classifica_wta}")


