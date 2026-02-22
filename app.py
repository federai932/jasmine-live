import os
from flask import Flask, render_template
from supabase import create_client

app = Flask(__name__)

# --- CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Inizializza il client Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def leggi_da_db(id_rank):
    """Funzione per recuperare il contenuto HTML dal database."""
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        if res.data:
            # Accede correttamente alla lista ritornata da Supabase
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non trovati nel database.</p>"
    except Exception as e:
        return f"<p>Errore di connessione al Database: {e}</p>"

@app.route('/')
def home():
    """Rotta principale che visualizza la pagina Home."""
    return render_template('index.html', 
                           tabella_html=leggi_da_db("singolo"), 
                           tabella_doppio_html=leggi_da_db("doppio"), 
                           news_html=leggi_da_db("news"))

if __name__ == "__main__":
    # Porta dinamica per Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

