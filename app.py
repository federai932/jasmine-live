import os
import requests
from flask import Flask, render_template, Response
from supabase import create_client

app = Flask(__name__)

# --- CONFIGURAZIONE SUPABASE (Tua parte originale) ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def leggi_da_db(id_rank):
    """Funzione per recuperare il contenuto HTML dal database."""
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        if res.data:
            # Ritorna il campo html_content dalla riga trovata
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non trovati nel database.</p>"
    except Exception as e:
        return f"<p>Errore di connessione al Database: {e}</p>"

# --- AGGIUNTA: FUNZIONE PROXY PER IFRAME (Risolve grafica e blocchi) ---
@app.route('/proxy/<path:url>')
def proxy(url):
    # Pulisce l'URL per evitare errori di host o protocolli doppi
    clean_url = url.replace('://', '').replace('https:', '').replace('http:', '').lstrip('/')
    target_url = f"https://{clean_url}"
    
    try:
        headers_request = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(target_url, headers=headers_request, timeout=15)
        
        # Rimuove i blocchi di sicurezza x-frame e csp
        excluded_headers = ['x-frame-options', 'content-security-policy', 'content-encoding', 'transfer-encoding']
        headers = [(n, v) for (n, v) in resp.raw.headers.items() if n.lower() not in excluded_headers]
        
        # Correzione grafica: trasforma i link relativi in assoluti per caricare i CSS
        content = resp.content
        if "text/html" in resp.headers.get("Content-Type", ""):
            base_parts = clean_url.split('/')
            domain_url = f"https://{base_parts[0]}"
            content = content.replace(b'href="/', b'href="' + domain_url.encode() + b'/')
            content = content.replace(b'src="/', b'src="' + domain_url.encode() + b'/')
            
        return Response(content, resp.status_code, headers)
    except Exception as e:
        return f"Errore Proxy: {str(e)}", 500

@app.route('/')
def home():
    """Rotta principale che visualizza la pagina Home."""
    return render_template('index.html', 
                           tabella_html=leggi_da_db("singolo"), 
                           tabella_doppio_html=leggi_da_db("doppio"), 
                           news_html=leggi_da_db("news"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


