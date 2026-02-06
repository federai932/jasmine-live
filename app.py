import os
import sys
import pandas as pd
from flask import Flask, render_template, jsonify

# Aggiunge la cartella corrente al percorso di ricerca di Python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Importiamo le funzioni dai tuoi file originali
try:
    from ranking import prendi_ranking_wta_live
    from prendi_ranking_doppio import prendi_ranking_wta_doppio_live
    from news_scraper import cerca_notizie_jasmine
except ImportError as e:
    print(f"Errore di importazione moduli: {e}")

app = Flask(__name__)

# Funzione per leggere i file generati dagli scraper
def leggi_file(nome):
    path = os.path.join(BASE_DIR, "static", nome)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "<p style='color:white; padding:20px;'>Dati in fase di aggiornamento... Visita /update per generare le tabelle.</p>"

@app.route('/update')
def update():
    try:
        # 1. Creiamo la cartella static se non esiste (fondamentale su Render)
        static_path = os.path.join(BASE_DIR, "static")
        if not os.path.exists(static_path):
            os.makedirs(static_path)

        # 2. Eseguiamo gli scraper e prendiamo i DataFrame
        df_singolo = prendi_ranking_wta_live()
        df_doppio = prendi_ranking_wta_doppio_live()
        
        # 3. Eseguiamo lo scraper delle news (che di solito scrive già il file)
        cerca_notizie_jasmine()

        # 4. TRASFORMAZIONE DATAFRAME -> HTML (Questo scrive i file su Render)
        if isinstance(df_singolo, pd.DataFrame):
            df_singolo.to_html(os.path.join(static_path, "classifica_web.html"), 
                               index=False, classes='wta-style', border=0, justify='center')
        
        if isinstance(df_doppio, pd.DataFrame):
            df_doppio.to_html(os.path.join(static_path, "classifica_doppio_web.html"), 
                               index=False, classes='wta-style', border=0, justify='center')

        return jsonify({
            "status": "success", 
            "message": "File rigenerati correttamente nella cartella static!"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/')
def home():
    # Passiamo i contenuti dei file HTML al template index.html
    return render_template('index.html', 
                           tabella_html=leggi_file("classifica_web.html"),
                           tabella_doppio_html=leggi_file("classifica_doppio_web.html"),
                           news_html=leggi_file("news_section.html"))

if __name__ == "__main__":
    # Configurazione porta per Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
