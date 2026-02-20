import os
import requests
from flask import Flask, render_template, request, jsonify
from supabase import create_client

app = Flask(__name__)

# --- SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- GOOGLE GEMINI (CHIAMATA DIRETTA CORRETTA) ---
API_KEY = os.environ.get("GOOGLE_API_KEY")

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
        return jsonify({"response": "Chiave API mancante su Render."})

    # URL CORRETTO (Nota il ? tra l'indirizzo e la chiave)
    url = f"https://generativelanguage.googleapis.com{API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Sei l'assistente di Jasmine Paolini. Rispondi in italiano. Domanda: {user_message}"
            }]
        }]
    }

    try:
        # Chiamata HTTP
        response = requests.post(url, json=payload, timeout=15)
        result = response.json()
        
        # LOGICA DI ESTRAZIONE CORRETTA PER GOOGLE API
        # Navighiamo dentro la struttura JSON di Google
        if 'candidates' in result and len(result['candidates']) > 0:
            answer = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"response": answer})
        else:
            print(f"RISPOSTA STRANA DA GOOGLE: {result}")
            return jsonify({"response": "Google non ha risposto correttamente. Controlla i log."})
    
    except Exception as e:
        print(f"ERRORE CHAT: {e}")
        return jsonify({"response": f"Il coach dice: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)



