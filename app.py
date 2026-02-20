import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from supabase import create_client

app = Flask(__name__)

# --- CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CONFIGURAZIONE GOOGLE GEMINI (SOLUZIONE DEFINITIVA) ---
api_key = os.environ.get("GOOGLE_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # USIAMO QUESTO NOME SPECIFICO CHE È IL PIÙ STABILE
        model = genai.GenerativeModel('models/gemini-1.5-flash')
    except Exception as e:
        print(f"ERRORE INIZIALIZZAZIONE: {e}")
else:
    print("WARNING: API KEY MANCANTE")

def leggi_da_db(id_rank):
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non trovati.</p>"
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
    user_message = request.json.get("message")
    
    # Istruzioni in Italiano
    context = "Sei l'assistente di Jasmine Paolini. Rispondi in modo tecnico e amichevole."

    try:
        # Forza la chiamata sul modello stabile
        response = model.generate_content(f"{context}\n\nUtente: {user_message}")
        return jsonify({"response": response.text})
    except Exception as e:
        # Se fallisce, stampiamo l'errore esatto nei log di Render
        print(f"ERRORE GEMINI: {e}")
        return jsonify({"response": f"Errore tecnico (Coach in pausa): {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)




