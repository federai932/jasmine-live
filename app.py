import os
import requests
from flask import Flask, render_template, request, jsonify
from supabase import create_client

app = Flask(__name__)

# --- SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- GOOGLE AI ---
API_KEY = os.environ.get("GOOGLE_API_KEY", "").strip()

def leggi_da_db(id_rank):
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        # Correzione fondamentale: res.data è una LISTA
        if res.data and len(res.data) > 0:
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non disponibili.</p>"
    except Exception as e:
        return f"<p>Errore DB: {e}</p>"

@app.route('/')
def home():
    return render_template('index.html', 
                           tabella_html=leggi_da_db("singolo"),
                           tabella_doppio_html=leggi_da_db("doppio"),
                           news_html=leggi_da_db("news"))

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message", "")
    if not API_KEY:
        return jsonify({"response": "Manca la chiave API nelle impostazioni di Render."})

    # URL CORRETTO CON PUNTO INTERROGATIVO E SENZA SPAZI
    url = f"https://generativelanguage.googleapis.com{API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"Sei l'assistente di Jasmine Paolini. Rispondi in italiano: {user_input}"}]
        }]
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        result = r.json()
        
        # ESTRAZIONE SICURA PASSO-PASSO (Evita crash se Google cambia formato)
        if "candidates" in result:
            candidate = result["candidates"][0]
            if "content" in candidate:
                parts = candidate["content"]["parts"]
                if parts and len(parts) > 0:
                    return jsonify({"response": parts[0]["text"]})
        
        # Se arriviamo qui, Google ha risposto con un errore (es. chiave scaduta)
        return jsonify({"response": f"L'IA ha dato una risposta vuota. Errore: {result.get('error', {}).get('message', 'Sconosciuto')}"})

    except Exception as e:
        return jsonify({"response": f"Errore di connessione: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
