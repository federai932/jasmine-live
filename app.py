import os
from flask import Flask, render_template
from supabase import create_client

app = Flask(__name__)

# Recupera le chiavi dalle Variabili d'Ambiente di Render (scelta sicura)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def leggi_da_db(record_id):
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", record_id).execute()
        if res.data:
            return res.data[0]['html_content']
        return "<p>Dati non trovati nel database.</p>"
    except Exception as e:
        return f"<p>Errore connessione DB: {e}</p>"

@app.route('/')
def home():
    return render_template('index.html', 
                           tabella_html=leggi_da_db("singolo"),
                           tabella_doppio_html=leggi_da_db("doppio"),
                           news_html="<p>News in fase di configurazione...</p>")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)






