import os
from flask import Flask, render_template, request, jsonify
from supabase import create_client
import google.generativeai as genai

app = Flask(__name__)

# --- CONFIGURAZIONE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Inizializzazione Client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Inizializzazione IA (Modello aggiornato)
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def leggi_da_db(id_rank):
    """Recupera HTML da Supabase con il fix della lista [0]."""
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        # IL FIX CHE FA FUNZIONARE LE NEWS:
        if res.data and len(res.data) > 0:
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non trovati.</p>"
    except Exception as e:
        print(f"Errore DB: {e}")
        return "<p>Errore di connessione.</p>"

@app.route('/')
def home():
    return render_template('index.html', 
                           tabella_html=leggi_da_db("singolo"),
                           tabella_doppio_html=leggi_da_db("doppio"),
                           news_html=leggi_da_db("news"))

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")
    try:
        # Risposta IA veloce e sicura
        prompt = f"Sei l'assistente di Jasmine Paolini. Rispondi in italiano: {user_message}"
        response = model.generate_content(prompt)
        # Importante: usiamo 'reply' come nel tuo file index.html
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": "Scusa, ho un piccolo problema tecnico."}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

