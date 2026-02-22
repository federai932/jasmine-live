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
    """Funzione per recuperare il contenuto HTML dal database."""
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        if res.data:
            # FIX: Aggiunto [0] per estrarre il primo elemento della lista
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non trovati nel database.</p>"
    except Exception as e:
        return f"<p>Errore di connessione al Database: {e}</p>"

# --- ROTTA PROXY PER IFRAME ---
@app.route('/proxy/<path:url>')
def proxy(url):
    clean_url = url.replace('https:/', '').replace('http:/', '').replace(':/', '').lstrip('/')
    target_url = f"https://{clean_url}"
    try:
        headers_req = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        resp = requests.get(target_url, headers=headers_req, timeout=15)
        excluded_headers = ['x-frame-options', 'content-security-policy', 'content-encoding', 'transfer-encoding']
        headers = [(n, v) for (n, v) in resp.raw.headers.items() if n.lower() not in excluded_headers]
        content = resp.content
        if "wtatennis" in target_url:
            base_tag = b'<base href="https://www.wtatennis.com">'
            content = content.replace(b'<head>', b'<head>' + base_tag)
        return Response(content, resp.status_code, headers)
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
