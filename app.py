import os
from flask import Flask, render_template
from supabase import create_client

app = Flask(__name__)

# --- CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def leggi_da_db(id_rank):
    """Recupera il contenuto HTML (Ranking e News)."""
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        if res.data:
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non trovati.</p>"
    except Exception:
        return f"<p>Errore Database {id_rank}</p>"

def leggi_torneo():
    """Recupera i dati specifici per la card del calendario."""
    try:
        # Cerchiamo la riga con id 'next_tournament'
        res = supabase.table("ranking_data").select("*").eq("id", "next_tournament").execute()
        if res.data:
            return res.data[0] # Restituisce l'intero dizionario con nome, data, status
        return {"tournament_name": "In aggiornamento...", "tournament_date": "Entry List WTA", "tournament_status": "Checking"}
    except Exception:
        return {"tournament_name": "Errore Connessione", "tournament_date": "-", "tournament_status": "Error"}

@app.route('/')
def home():
    """Rotta principale."""
    # Recuperiamo i dati del torneo
    torneo = leggi_torneo()
    
    return render_template('index.html', 
                           tabella_html=leggi_da_db("singolo"), 
                           tabella_doppio_html=leggi_da_db("doppio"), 
                           news_html=leggi_da_db("news"),
                           # --- NUOVE VARIABILI PER IL CALENDARIO ---
                           tournament_name=torneo.get('tournament_name'),
                           tournament_date=torneo.get('tournament_date'),
                           tournament_status=torneo.get('tournament_status'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

