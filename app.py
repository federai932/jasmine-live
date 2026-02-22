import os
import requests
from flask import Flask, render_template, Response, request
from supabase import create_client
from urllib.parse import urljoin

app = Flask(__name__)

# --- CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def leggi_da_db(id_rank):
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        return res.data[0]['html_content'] if res.data else f"<p>{id_rank} non trovato.</p>"
    except: return "<p>Errore DB</p>"

# --- PROXY PROFESSIONALE PER IFRAME ---
@app.route('/proxy/<path:url>')
def proxy(url):
    target_url = f"https://{url}"
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(target_url, headers=headers, timeout=15)
        
        # Rimuove i blocchi di sicurezza
        excluded_headers = ['x-frame-options', 'content-security-policy', 'content-encoding', 'transfer-encoding']
        res_headers = [(n, v) for (n, v) in resp.raw.headers.items() if n.lower() not in excluded_headers]
        
        # RISCRITTURA PER LA GRAFICA (Sostituisce i link relativi con quelli assoluti)
        content = resp.content
        if "text/html" in resp.headers.get("Content-Type", ""):
            base_url = f"https://{url.split('/')[0]}"
            content = content.replace(b'href="/', b'href="' + base_url.encode() + b'/')
            content = content.replace(b'src="/', b'src="' + base_url.encode() + b'/')

        return Response(content, resp.status_code, res_headers)
    except Exception as e:
        return f"Errore: {str(e)}", 500

@app.route('/')
def home():
    return render_template('index.html', 
                           tabella_html=leggi_da_db("singolo"), 
                           tabella_doppio_html=leggi_da_db("doppio"), 
                           news_html=leggi_da_db("news"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

