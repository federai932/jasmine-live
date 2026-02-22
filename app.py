import os
import requests
from flask import Flask, render_template, Response
from supabase import create_client

app = Flask(__name__)

# --- CONFIGURAZIONE SUPABASE ---
# Le chiavi vengono lette dalle Variabili d'Ambiente di Render (più sicuro)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Inizializza il client Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def leggi_da_db(id_rank):
    """Funzione per recuperare il contenuto HTML dal database."""
    try:
        # Recupera la riga dal database dove l'id è 'singolo', 'doppio' o 'news'
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        # Se trova i dati, li restituisce; altrimenti, mostra un messaggio
        if res.data:
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non trovati nel database.</p>"
    except Exception as e:
        return f"<p>Errore di connessione al Database: {e}</p>"

# --- NUOVA ROTTA PROXY PER IFRAME (Indispensabile per Render) ---
@app.route('/proxy/<path:url>')
def proxy(url):
    """Scarica il sito esterno e rimuove i blocchi X-Frame-Options."""
    # Gestisce l'URL evitando il raddoppio di https://
    target_url = url if url.startswith('http') else f"https://{url}"
    try:
        # Scarica la pagina dal sito originale (WTA o Notion)
        resp = requests.get(target_url, timeout=15)
        
        # Elimina gli header di sicurezza che bloccano la visualizzazione nell'app
        excluded_headers = [
            'content-encoding', 'content-length', 'transfer-encoding', 'connection',
            'x-frame-options', 'content-security-policy', 'strict-transport-security'
        ]
        headers = [
            (name, value) for (name, value) in resp.raw.headers.items()
            if name.lower() not in excluded_headers
        ]
        
        # Restituisce il sito "pulito" alla tua app
        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        return f"Errore nel caricamento del sito: {str(e)}", 500

@app.route('/')
def home():
    """Rotta principale che visualizza la pagina Home."""
    # Legge i contenuti direttamente dal DB e li passa al template
    return render_template('index.html', 
                           tabella_html=leggi_da_db("singolo"), 
                           tabella_doppio_html=leggi_da_db("doppio"), 
                           news_html=leggi_da_db("news"))

# Rotta di default per l'avvio su Render
if __name__ == "__main__":
    # Usa la porta dinamica fornita da Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
