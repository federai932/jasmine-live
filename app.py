import os
from flask import Flask, render_template, request, jsonify
from supabase import create_client
import google.generativeai as genai

app = Flask(__name__)

# --- CONFIGURAZIONE VARIABILI D'AMBIENTE ---
# Queste vengono lette da Render per la massima sicurezza
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Inizializza il client Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Inizializza Google AI (Gemini)
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def leggi_da_db(id_rank):
    """Funzione originale per recuperare il contenuto HTML dal database."""
    try:
        # Recupera la riga dal database dove l'id è 'singolo', 'doppio' o 'news'
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        
        # Se trova i dati, li restituisce; altrimenti, mostra un messaggio
        if res.data:
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non trovati nel database.</p>"
    except Exception as e:
        return f"<p>Errore di connessione al Database: {e}</p>"

@app.route('/')
def home():
    """Rotta principale che visualizza la pagina Home con i dati originali."""
    return render_template(
        'index.html', 
        tabella_html=leggi_da_db("singolo"), 
        tabella_doppio_html=leggi_da_db("doppio"), 
        news_html=leggi_da_db("news")
    )

@app.route('/chat', methods=['POST'])
def chat():
    """Nuova rotta per gestire i messaggi del chatbot."""
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"reply": "Non ho ricevuto alcun messaggio."}), 400

    try:
        # Istruzione di sistema per forzare l'italiano e il contesto
        prompt = f"Rispondi in modo cordiale e sempre in lingua italiana. Utente: {user_message}"
        response = model.generate_content(prompt)
        return jsonify({"reply": response.text})
    except Exception as e:
        print(f"Errore AI: {e}")
        return jsonify({"reply": "Scusa, ho difficoltà a connettermi al mio cervello digitale. Riprova più tardi!"}), 500

# Avvio su Render
if __name__ == "__main__":
    # Usa la porta dinamica fornita da Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

