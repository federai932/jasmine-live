import os
import sys
from flask import Flask, render_template, jsonify

# Assicura che Render trovi scrapers.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scrapers import run_all_scrapers

app = Flask(__name__)

def leggi_file(nome):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", nome)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "<p style='color:white;'>Dati in fase di aggiornamento... visita /update</p>"

@app.route('/update')
def update():
    try:
        run_all_scrapers()
        return jsonify({"status": "success", "message": "Dati aggiornati correttamente"})
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

