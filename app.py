import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from supabase import create_client

app = Flask(__name__)

# --- CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CONFIGURAZIONE GEMINI (FIX 404) ---
api_key = os.environ.get("GOOGLE_API_KEY")
if api_key:
    # Forza la configurazione sulla versione v1 stabile
    genai.configure(api_key=api_key)
    # IMPORTANTE: Usiamo 'gemini-1.5-flash' senza prefissi strani
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    print("ATTENZIONE: GOOGLE_API_KEY non trovata!")

def leggi_da_db(id_rank):
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non trovati.</p>"
    except Exception as e:
        return "<p>Dati momentaneamente non disponibili.</p>"

@app.route('/')
def home():
    return render_template('index.html', 
                           tabella_html=leggi_da_db("singolo"),
                           tabella_doppio_html=leggi_da_db("doppio"),
                           news_html=leggi_da_db("news"))

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")
    if not api_key:
        return jsonify({"response": "Chat non configurata."})
    
    # Istruzioni di contesto
    context = "Sei l'assistente di Jasmine Paolini. Rispondi in italiano."
    
    try:
        # Chiamata pulita al modello
        response = model.generate_content(f"{context}\n\nDomanda: {user_message}")
        return jsonify({"response": response.text})
    except Exception as e:
        # Se vedi ancora 404, stampiamo l'errore nei log di Render
        print(f"ERRORE GEMINI DETTAGLIATO: {e}")
        return jsonify({"response": f"Errore tecnico: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)




