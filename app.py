import os
import sys
import pandas as pd
from flask import Flask, render_template, jsonify

# Configurazione percorsi
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Import scraper
try:
    from ranking import prendi_ranking_wta_live
    from prendi_ranking_doppio import prendi_ranking_wta_doppio_live
    from news_scraper import cerca_notizie_jasmine
except ImportError as e:
    print(f"Errore import: {e}")

app = Flask(__name__)

def leggi_file(nome):
    path = os.path.join(BASE_DIR, "static", nome)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "<p style='color:grey; padding:20px;'>Dati in aggiornamento...</p>"

@app.route('/update')
def update():
    try:
        static_path = os.path.join(BASE_DIR, "static")
        if not os.path.exists(static_path):
            os.makedirs(static_path)

        # PULIZIA: Rimuoviamo i file vecchi per evitare che si sporchino
        for f in ["classifica_web.html", "classifica_doppio_web.html"]:
            p = os.path.join(static_path, f)
            if os.path.exists(p): os.remove(p)

        # Esecuzione scraper
        df_s = prendi_ranking_wta_live()
        df_d = prendi_ranking_wta_doppio_live()
        cerca_notizie_jasmine() # Le news si salvano da sole

        # Salvataggio Singolo
        if isinstance(df_s, pd.DataFrame):
            df_s.to_html(os.path.join(static_path, "classifica_web.html"), 
                         index=False, border=0, classes='wta-style')
        
        # Salvataggio Doppio
        if isinstance(df_d, pd.DataFrame):
            df_d.to_html(os.path.join(static_path, "classifica_doppio_web.html"), 
                         index=False, border=0, classes='wta-style')

        return jsonify({"status": "success", "message": "Dati puliti e rigenerati!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/')
def home():
    return render_template('index.html', 
                           tabella_html=leggi_file("classifica_web.html"),
                           tabella_doppio_html=leggi_file("classifica_doppio_web.html"),
                           news_html=leggi_file("news_section.html"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
