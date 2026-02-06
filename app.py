import os
import sys
from flask import Flask, render_template, jsonify

# Aggiunge la cartella corrente al percorso di ricerca di Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importiamo le funzioni usando i nomi esatti dei tuoi file
try:
    from ranking import prendi_ranking_wta_live
    from prendi_ranking_doppio import prendi_ranking_wta_doppio_live
    from news_scraper import cerca_notizie_jasmine
except ImportError as e:
    print(f"Errore di importazione: {e}")

app = Flask(__name__)

# Funzione per leggere i file generati dagli scraper
def leggi_file(nome):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", nome)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "<p style='color:white; padding:20px;'>Dati in fase di aggiornamento... Visita /update per generare le tabelle.</p>"

@app.route('/update')
def update():
    try:
        # Eseguiamo i tre script uno dopo l'altro
        res_s = prendi_ranking_wta_live()
        res_d = prendi_ranking_wta_doppio_live()
        res_n = cerca_notizie_jasmine()
        
        return jsonify({
            "status": "success", 
            "results": {
                "singolo": res_s,
                "doppio": res_d,
                "news": res_n
            }
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
    # Porta dinamica per Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

