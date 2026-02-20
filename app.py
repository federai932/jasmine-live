import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from supabase import create_client

app = Flask(__name__)

# --- SUPABASE CONFIGURATION ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- GOOGLE GEMINI CONFIGURATION (Version 1.5 Flash - STABLE) ---
api_key = os.environ.get("GOOGLE_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # Use the 1.5 flash model, which is the most current and fast
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"GEMINI INITIALIZATION ERROR: {e}")
else:
    print("WARNING: GOOGLE_API_KEY not found in environment variables!")

def leggi_da_db(id_rank):
    """Retrieves the HTML content saved in the Supabase database."""
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        # Verify if data exists before accessing index [0]
        if res.data and len(res.data) > 0:
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non trovati nel database.</p>"
    except Exception as e:
        print(f"ERRORE DATABASE: {e}")
        return f"<p>Errore di connessione al database.</p>"

@app.route('/')
def home():
    """Main route that loads the app interface."""
    return render_template('index.html', 
                           tabella_html=leggi_da_db("singolo"),
                           tabella_doppio_html=leggi_da_db("doppio"),
                           news_html=leggi_da_db("news"))

@app.route('/chat', methods=['POST'])
def chat():
    """Handles the Chatbot IA logic on Jasmine Paolini."""
    if not api_key:
        return jsonify({"response": "Configurazione chat non trovata sul server."})

    user_message = request.json.get("message")
    
    # Context instructions (Prompt Engineering) in Italiano
    context = (
        "Sei l'assistente virtuale ufficiale dell'app 'Game Set Jasmine'. "
        "Rispondi a domande su Jasmine Paolini, tennista italiana top 10 mondiale. "
        "Sii tecnico, amichevole e parla come se fossi parte del suo team. "
        "Usa le informazioni della sua bio: nata il 4 gen 1996, alta 1.63m, coach Danilo Pizzorno e Sara Errani."
    )

    try:
        # Generazione della risposta
        response = model.generate_content(f"{context}\n\nDomanda utente: {user_message}")
        return jsonify({"response": response.text})
    except Exception as e:
        print(f"GEMINI ERROR: {e}")
        return jsonify({"response": f"Il coach dice che c'è un problema tecnico: {str(e)}"})

# Startup for Render
if __name__ == "__main__":
    # Render assigns the port automatically
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)



