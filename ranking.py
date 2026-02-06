import cloudscraper
import pandas as pd
import io
import os

def prendi_ranking_wta_live():
    url = "https://live-tennis.eu"
    # TRUCCO PER RENDER: Simuliamo un vero Chrome
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','mobile': False})
    
    try:
        response = scraper.get(url, timeout=20)
        tabelle = pd.read_html(io.StringIO(response.text), keep_default_na=False)
        
        for df in tabelle:
            if len(df.columns) >= 10:
                # La tua logica originale rimane identica
                df_util = df.copy()
                df_util = df_util[pd.to_numeric(df_util.iloc[:, 0], errors='coerce').notnull()]
                top_10 = df_util.head(10).copy()
                
                ranking_finale = top_10.iloc[:, [0, 3, 5, 6]]
                ranking_finale.columns = ['Rank', 'Giocatrice', 'Paese', 'Punti Totali']
                return ranking_finale
        return "Tabella non trovata"
    except Exception as e:
        return f"Errore: {e}"

# --- ESECUZIONE ---
classifica_wta = prendi_ranking_wta_live()

if isinstance(classifica_wta, pd.DataFrame):
    html_string = classifica_wta.to_html(index=False, classes='wta-style', border=0, justify='center')
    
    # PERCORSO UNIVERSALE (Funziona sia su PC che su Render)
    cartella_static = os.path.join(os.path.dirname(__file__), "static")
    if not os.path.exists(cartella_static):
        os.makedirs(cartella_static)
        
    output_path = os.path.join(cartella_static, "classifica_web.html")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_string)
    print("OK! File creato con successo.")
