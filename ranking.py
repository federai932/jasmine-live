import cloudscraper
import pandas as pd
import io
import os

def prendi_ranking_wta_live():
    url = "https://live-tennis.eu/it/classifica-wta-live"
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
                    
                    # Selezione colonne corretta (quella che avevi tu)
                    ranking_finale = top_10.iloc[:, [0, 3, 5, 6]]
                    ranking_finale.columns = ['Rank', 'Giocatrice', 'Paese', 'Punti Totali']
                    
                    return ranking_finale

        return "Tabella WTA non trovata."
    except Exception as e:
        return f"Errore: {e}"

classifica_wta = prendi_ranking_wta_live()

if isinstance(classifica_wta, pd.DataFrame):
    # justify='center' aggiunge il comando di centratura nell'HTML
    html_string = classifica_wta.to_html(index=False, classes='wta-style', border=0, justify='center')
    
    output_path = r"C:\Users\fedec\OneDrive\Desktop\Sito Web\classifica_web.html"
    
    # Salvataggio UTF-8 per Iga Świątek
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_string)
        
    print(f"\n[OK] File aggiornato con colonne corrette e centratura!")
else:
    print(f"\n[AVVISO] {classifica_wta}")
