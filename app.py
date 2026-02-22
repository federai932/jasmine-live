import os
import requests
from flask import Flask, render_template, Response
from supabase import create_client

app = Flask(__name__)

# --- CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def leggi_da_db(id_rank):
    """Recupera il contenuto HTML dal database Supabase."""
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        if res.data:
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non trovati.</p>"
    except Exception as e:
        return f"<p>Errore DB: {e}</p>"

# --- ROTTA PROXY PER IFRAME ---
@app.route('/proxy/<path:url>')
def proxy(url):
    """Scarica il sito esterno e rimuove i blocchi di sicurezza per l'iframe."""
    target_url = f"https://{url}"
    try:
        # Effettua la richiesta al sito esterno
        resp = requests.get(target_url, timeout=10)
        
        # Escludiamo gli header che bloccano gli iframe (X-Frame-Options e CSP)
        excluded_headers = [
            'content-encoding', 'content-length', 'transfer-encoding', 'connection',
            'x-frame-options', 'content-security-policy', 'strict-transport-security'
        ]
        headers = [
            (name, value) for (name, value) in resp.raw.headers.items()
            if name.lower() not in excluded_headers
        ]
        
        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        return f"Errore nel caricamento del sito: {str(e)}", 500

@app.route('/')
def home():
    """Visualizza la pagina principale."""
    return render_template('index.html', 
                           tabella_html=leggi_da_db("singolo"), 
                           tabella_doppio_html=leggi_da_db("doppio"), 
                           news_html=leggi_da_db("news"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

