import os
import sys
import pandas as pd
from flask import Flask, render_template, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from ranking import prendi_ranking_wta_live
from prendi_ranking_doppio import prendi_ranking_wta_doppio_live
from news_scraper import cerca_notizie_jasmine

app = Flask(__name__)

def leggi_file(nome):
    path = os.path.join(BASE_DIR, "static", nome)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "<p>Dati in aggiornamento... clicca /update</p>"

@app.route('/update')
def update():
    try:
        # Crea cartella static se manca
        static_path = os.path.join(BASE_DIR, "static")
        os.makedirs(static_path, exist_ok=True)

        # Esegui e SALVA fisicamente
        df_s = prendi_ranking_wta_live()
        if isinstance(df_s, pd.DataFrame):
            df_s.to_html(os.path.join(static_path, "classifica_web.html"), index=False, border=0)
        
        df_d = prendi_ranking_wta_doppio_live()
        if isinstance(df_d, pd.DataFrame):
            df_d.to_html(os.path.join(static_path, "classifica_doppio_web.html"), index=False, border=0)
            
        cerca_notizie_jasmine()

        return jsonify({"status": "success"})
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




