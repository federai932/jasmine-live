from flask import Flask, render_template, jsonify
import os
from scrapers import run_all_scrapers

app = Flask(__name__)

@app.route('/update')
def update():
    run_all_scrapers()
    return jsonify({"status": "success"})

@app.route('/')
def home():
    def leggi(name):
        p = os.path.join("static", name)
        return open(p, "r", encoding="utf-8").read() if os.path.exists(p) else "Caricamento..."
    
    return render_template('index.html', 
                           tabella_html=leggi("classifica_web.html"),
                           tabella_doppio_html=leggi("classifica_doppio_web.html"),
                           news_html=leggi("news_section.html"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

