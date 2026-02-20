import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from supabase import create_client

app = Flask(__name__)

# --- CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Inizializzazione sicura del client
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"ERRORE CONFIGURAZIONE SUPABASE: {e}")

# --- CONFIGURAZIONE GOOGLE GEMINI ---
api_key = os.environ.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    # Usiamo il modello flash che è il più compatibile
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    print("ATTENZIONE: GOOGLE_API_KEY non trovata!")

def leggi_da_db(id_rank):
    """Recupera il contenuto HTML da Supabase con gestione errori migliorata."""
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        # Controllo se res ha l'attributo data (standard per il client python di supabase)
        if hasattr(res, 'data') and res.data:
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non trovati.</p>"
    except Exception as e:
        print(f"ERRORE DB {id_rank}: {e}")
        return f"<p>Dati {id_rank} momentaneamente non disponibili.</p>"

@app.route('/')
def home():
    """Rotta principale."""
    return render_template('index.html', 
                           tabella_html=leggi_da_db("singolo"),
                           tabella_doppio_html=leggi_da_db("doppio"),
                           news_html=leggi_da_db("news"))

@app.route('/chat', methods=['POST'])
def chat():
    """Gestione Chatbot."""
    user_message = request.json.get("message")
    if not api_key:
        return jsonify({"response": "Servizio chat non configurato."})
    
    context = "Sei l'assistente di Jasmine Paolini. Rispondi in italiano."
    try:
        response = model.generate_content(f"{context}\n\nDomanda: {user_message}")
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"Errore tecnico: {str(e)}"})

# AVVIO PER RENDER (CRUCIALE)
if __name__ == "__main__":
    # Render richiede l'ascolto su 0.0.0.0 e sulla porta PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


