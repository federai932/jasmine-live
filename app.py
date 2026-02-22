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
            # Ritorna il campo html_content dalla prima riga trovata
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non trovati nel database.</p>"
    except Exception as e:
        return f"<p>Errore di connessione al Database: {e}</p>"

# --- AGGIUNTA: ROTTA PROXY PER IFRAME ---
@app.route('/proxy/<path:url>')
def proxy(url):
    """Scarica il sito esterno e rimuove i blocchi di sicurezza (X-Frame-Options)."""
    # Pulizia dell'URL per evitare errori di protocollo raddoppiato (es. https://://)
    clean_url = url.replace('https://', '').replace('http://', '')
    target_url = f"https://{clean_url}"
    
    try:
        # Simula un browser normale per evitare blocchi dal server esterno
        headers_request = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(target_url, headers=headers_request, timeout=15)
        
        # Header da rimuovere per permettere la visualizzazione nell'iframe
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
        return f"Errore nel caricamento tramite Proxy: {str(e)}", 500

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
