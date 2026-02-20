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
    """Recupera HTML da Supabase con gestione errori robusta."""
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        # Verifica se res.data esiste ed è una lista con almeno un elemento
        if hasattr(res, 'data') and len(res.data) > 0:
            return res.data[0].get('html_content', f"<p>Dati {id_rank} vuoti.</p>")
        return f"<p>Dati {id_rank} non trovati nel database.</p>"
    except Exception as e:
        print(f"ERRORE DB {id_rank}: {e}")
        return f"<p>Dati {id_rank} momentaneamente non disponibili.</p>"

@app.route('/')
def home():
    """Pagina principale dell'app."""
    return render_template('index.html',
                           tabella_html=leggi_da_db("singolo"),
                           tabella_doppio_html=leggi_da_db("doppio"),
                           news_html=leggi_da_db("news"))

@app.route('/chat', methods=['POST'])
def chat():
    """Gestione Chatbot con chiamata REST diretta (Anti-404)."""
    user_data = request.get_json()
    user_message = user_data.get("message", "")

    if not API_KEY:
        return jsonify({"response": "Configurazione Chat mancante (API KEY)."})

    # URL Ufficiale Google Gemini API
    url = f"https://generativelanguage.googleapis.com{API_KEY}"

    payload = {
        "contents": [{
            "parts": [{
                "text": f"Sei l'assistente di Jasmine Paolini. Rispondi in italiano in modo breve. Domanda: {user_message}"
            }]
        }]
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()

        # Estrazione sicura della risposta dal JSON di Google
        if "candidates" in result and len(result["candidates"]) > 0:
            # Navigo nel percorso corretto del JSON
            answer = result["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"response": answer})
        else:
            print(f"DEBUG GOOGLE: {result}")
            return jsonify({"response": "L'IA non ha risposto. Controlla i log di Render."})

    except Exception as e:
        print(f"ERRORE CHAT: {e}")
        return jsonify({"response": f"Il coach dice che c'è un errore: {str(e)}"})

if __name__ == "__main__":
    # Porta dinamica per Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)



