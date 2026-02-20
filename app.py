import os
import requests
from flask import Flask, render_template, request, jsonify
from supabase import create_client

app = Flask(__name__)

# --- SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- GOOGLE GEMINI (CHIAMATA DIRETTA E SICURA) ---
# Puliamo la chiave da eventuali spazi che possono rompere l'URL
API_KEY = os.environ.get("GOOGLE_API_KEY", "").strip()

def leggi_da_db(id_rank):
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non trovati.</p>"
    except Exception as e:
        return "<p>Errore caricamento dati.</p>"

@app.route('/')
def home():
    return render_template('index.html', 
                           tabella_html=leggi_da_db("singolo"),
                           tabella_doppio_html=leggi_da_db("doppio"),
                           news_html=leggi_da_db("news"))

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")
    
    if not API_KEY:
        return jsonify({"response": "Manca la chiave API su Render!"})

    # URL PULITO: L'URL finisce con :generateContent e i parametri iniziano dopo il ?
    url = "https://generativelanguage.googleapis.com"
    params = {'key': API_KEY}
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Sei l'assistente di Jasmine Paolini. Rispondi in italiano. Domanda: {user_message}"
            }]
        }]
    }

    try:
        # Usiamo 'params' così requests mette il '?' e la chiave nel modo giusto
        response = requests.post(url, params=params, json=payload, timeout=15)
        result = response.json()
        
        # Navighiamo nel JSON di risposta di Google
        if 'candidates' in result and len(result['candidates']) > 0:
            # La risposta è sepolta qui dentro:
            answer = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"response": answer})
        else:
            print(f"DEBUG GOOGLE: {result}")
            return jsonify({"response": "Google non ha risposto. Forse la chiave è sbagliata?"})
    
    except Exception as e:
        print(f"ERRORE CHAT: {e}")
        return jsonify({"response": f"Errore tecnico: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


