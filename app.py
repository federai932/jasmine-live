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
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        if res.data:
            # Ritorna il contenuto corretto
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non trovati.</p>"
    except Exception as e:
        return f"<p>Errore DB: {e}</p>"

# --- PROXY FIX: RISOLVE ERRORE "NO HOST SUPPLIED" ---
@app.route('/proxy/<path:url>')
def proxy(url):
    # Elimina QUALSIASI protocollo già presente per evitare il raddoppio https://://
    clean_url = url.replace('https:/', '').replace('http:/', '').replace(':/', '').lstrip('/')
    target_url = f"https://{clean_url}"
    
    try:
        headers_request = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(target_url, headers=headers_request, timeout=15)
        
        excluded_headers = [
            'content-encoding', 'content-length', 'transfer-encoding', 'connection',
            'x-frame-options', 'content-security-policy', 'strict-transport-security'
        ]
        headers = [(n, v) for (n, v) in resp.raw.headers.items() if n.lower() not in excluded_headers]
        
        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        return f"Errore Proxy: {str(e)}", 500

@app.route('/')
def home():
    return render_template('index.html', 
                           tabella_html=leggi_da_db("singolo"), 
                           tabella_doppio_html=leggi_da_db("doppio"), 
                           news_html=leggi_da_db("news"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
