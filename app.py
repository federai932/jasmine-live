import os
import requests
from flask import Flask, render_template, request, jsonify
from supabase import create_client

app = Flask(__name__)

# --- CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CHIAVE GOOGLE ---
API_KEY = os.environ.get("GOOGLE_API_KEY", "").strip()

def leggi_da_db(id_rank):
    """Recupera HTML da Supabase. Corretto per evitare crash."""
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        # Se trova i dati (res.data è una lista), prendi il primo
        if res.data and len(res.data) > 0:
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non trovati.</p>"
    except Exception as e:
        print(f"ERRORE DB {id_rank}: {e}")
        return "<p>Dati momentaneamente non disponibili.</p>"

@app.route('/')
def home():
    """Pagina principale dell'app."""
    return render_template('index.html',
                           tabella_html=leggi_da_db("singolo"),
                           tabella_doppio_html=leggi_da_db("doppio"),
                           news_html=leggi_da_db("news"))

@app.route('/chat', methods=['POST'])
def chat():
    """Chatbot con chiamata diretta a Google Gemini."""
    if not API_KEY:
        return jsonify({"response": "Manca la chiave API!"})

    data = request.json
    user_message = data.get("message", "")

    # URL corretto per Gemini 1.5 Flash
    url = f"https://generativelanguage.googleapis.com{API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Sei l'assistente di Jasmine Paolini. Rispondi in italiano. Domanda: {user_message}"
            }]
        }]
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        result = r.json()
        # Navigazione nel JSON di Google (Percorso Corretto)
        answer = result['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"response": answer})
    except Exception as e:
        print(f"ERRORE CHAT: {e}")
        return jsonify({"response": f"Il coach dice: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
