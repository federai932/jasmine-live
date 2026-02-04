import subprocess
from flask import Flask, render_template
import os

app = Flask(__name__)

def esegui_scraper():
    # Usiamo sys.executable per essere sicuri di usare il Python di Render
    import sys
    scripts = ["news_scraper.py", "ranking.py", "prendi_ranking_doppio.py"]
    for script in scripts:
        try:
            print(f"Avvio {script}...")
            subprocess.run([sys.executable, script], check=True)
        except Exception as e:
            print(f"Errore su {script}: {e}")

@app.route('/')
def index():
    esegui_scraper() # Si aggiorna ogni volta che apri l'app
    # Qui carica i tuoi file html (es. news_html = open('news.html').read())
    # ... (inserisci qui la logica originale del tuo file app.py)
    return render_template('index.html', ...)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
