import cloudscraper
import pandas as pd
import io
import os

def prendi_ranking_wta_doppio_live():
    # URL specifico per il doppio
    url = "https://live-tennis.eu/it/classifica-wta-doppio-live"
    scraper = cloudscraper.create_scraper()
    
    try:
        response = scraper.get(url)
        # Leggiamo la tabella
        tabelle = pd.read_html(io.StringIO(response.text), keep_default_na=False)
        
        for df in tabelle:
            # La tabella ranking solitamente ha molte colonne
            if len(df.columns) >= 8:
                # Verifichiamo se ci sono nomi noti del doppio (es. Errani o Hsieh)
                nomi_test = df.iloc[:, 3].astype(str).to_string()
                
                if "Errani" in nomi_test or "Paolini" in nomi_test or "Hsieh" in nomi_test:
                    df_util = df.copy()
                    
                    # Filtriamo le righe che non hanno un numero di ranking valido
                    df_util = df_util[pd.to_numeric(df_util.iloc[:, 0], errors='coerce').notnull()]
                    
                    # Prendiamo le prime 10 posizioni
                    top_10 = df_util.head(10).copy()
                    
                    # Selezione colonne per il doppio:
                    # 0: Rank, 3: Giocatrice, 5: Paese, 6: Punti
                    ranking_finale = top_10.iloc[:, [0, 3, 5, 6]]
                    ranking_finale.columns = ['Rank', 'Giocatrice', 'Paese', 'Punti Totali']
                    
                    return ranking_finale

        return "Tabella WTA Doppio non trovata."
    except Exception as e:
        return f"Errore: {e}"

# Esecuzione
classifica_doppio = prendi_ranking_wta_doppio_live()

if isinstance(classifica_doppio, pd.DataFrame):
    # Generazione HTML con lo stesso stile del singolare
    html_string = classifica_doppio.to_html(index=False, classes='wta-style-doppio', border=0, justify='center')
    
    # Percorso di output (cambiato nome per non sovrascrivere il singolare)
    output_path = r"C:\Users\fedec\OneDrive\Desktop\Sito Web\classifica_doppio_web.html"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_string)
        
    print(f"\n[OK] Classifica DOPPIO aggiornata correttamente!")
    print(classifica_doppio.head(5)) # Anteprima a video
else:
    print(f"\n[AVVISO] {classifica_doppio}")


