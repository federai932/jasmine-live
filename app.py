import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from supabase import create_client

app = Flask(__name__)

# --- CONFIGURAZIONE SUPABASE ---
# Assicurati che queste variabili siano impostate su Render
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CONFIGURAZIONE GOOGLE GEMINI (Versione 1.5 Flash) ---
# Recupera la chiave dalle Environment Variables di Render
api_key = os.environ.get("GOOGLE_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    # Aggiornato a 'gemini-1.5-flash' per evitare l'errore 404 del vecchio 'gemini-pro'
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    print("ATTENZIONE: GOOGLE_API_KEY non trovata nelle variabili d'ambiente!")

def leggi_da_db(id_rank):
    """Recupera il contenuto HTML salvato nel database Supabase."""
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        if res.data:
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non trovati nel database.</p>"
    except Exception as e:
        print(f"ERRORE DATABASE: {e}")
        return f"<p>Errore di connessione al Database.</p>"

@app.route('/')
def home():
    """Rotta principale che carica l'interfaccia dell'app."""
    return render_template('index.html', 
                           tabella_html=leggi_da_db("singolo"),
                           tabella_doppio_html=leggi_da_db("doppio"),
                           news_html=leggi_da_db("news"))

@app.route('/chat', methods=['POST'])
def chat():
    """Gestisce la logica del Chatbot IA su Jasmine Paolini."""
    if not api_key:
        return jsonify({"response": "Errore di configurazione: API Key mancante su Render."})

    user_message = request.json.get("message")
    
    # Istruzioni di contesto per dare personalità al bot
    context = (
        "Sei l'assistente virtuale ufficiale dell'app 'Game Set Jasmine'. "
        "Rispondi a domande su Jasmine Paolini, tennista italiana numero 8 del mondo. "
        "Sii tecnico, amichevole e appassionato. Se non conosci un dettaglio specifico, "
        "consiglia di controllare la sezione Match o il Calendario WTA."
    )

    try:
        # Generazione della risposta con il nuovo modello 1.5 Flash
        response = model.generate_content(f"{context}\n\nUtente: {user_message}")
        return jsonify({"response": response.text})
    except Exception as e:
        print(f"GEMINI ERROR: {e}")
        return jsonify({"response": f"Il coach dice che c'è un problema tecnico: {str(e)}"})

# Avvio per Render
if __name__ == "__main__":
    # Render assegna una porta dinamica tramite la variabile d'ambiente PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)






