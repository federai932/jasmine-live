import os
from flask import Flask, render_template, request, redirect, render_template_string, jsonify
from supabase import create_client
import google.generativeai as genai

app = Flask(__name__)

# --- CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CONFIGURAZIONE GOOGLE AI ---
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

def leggi_da_db(id_rank):
    """Recupera la riga dal database in base all'ID (singolo, doppio, race_singolo, race_doppio, news)."""
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        # Se i dati esistono e la lista non è vuota
        if res.data and len(res.data) > 0:
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non ancora disponibili.</p>"
    except Exception as e:
        print(f"Errore DB per {id_rank}: {e}")
        return f"<p>Errore di connessione al Database.</p>"
 
def leggi_tornei():
    """Recupera la lista di tutti i tornei salvati (1, 2, ecc.)."""
    try:
        # Cerchiamo tutti gli ID che iniziano con next_tournament
        res = supabase.table("ranking_data").select("*").ilike("id", "next_tournament%").execute()
        if res.data and len(res.data) > 0:
            lista_tornei = []
            for d in res.data:
                lista_tornei.append({
                    "name": d.get('tournament_name') or "In aggiornamento...",
                    "date_iso": d.get('tournament_date') or "2025-01-01", 
                    "date_show": d.get('tournament_date_full') or "Data da definire", 
                    "cat": d.get('tournament_cat') or "WTA",
                    "logo_cat": d.get('logo_cat_file') or "default_cat.png",
                    "logo_torneo": d.get('logo_torneo_file') or "default_torneo.png",
                    "url": d.get('tournament_url') or "#"
                })
            # Ordiniamo i tornei per data (il più vicino appare per primo)
            return sorted(lista_tornei, key=lambda x: x['date_iso'])
        return []
    except Exception as e:
        print(f"Errore lettura tornei: {e}")
        return []
        
@app.route('/admin-torneo', methods=['GET', 'POST'])
def admin_torneo():
    if request.method == 'POST':
        # RECUPERA QUALE SLOT AGGIORNARE
        torneo_id = request.form.get('torneo_id')
        
        nome = request.form.get('nome')
        data_iso = request.form.get('data_iso')   
        data_show = request.form.get('data_show') 
        url_sito = request.form.get('url_sito')
        cat = request.form.get('categoria')
        
        logo_t = nome.lower().replace(" ", "_") + ".png"
        logo_c = cat.lower().replace(" ", "") + ".png"

        payload = {
            "id": torneo_id, # <--- Slot scelto (1 o 2)
            "tournament_name": nome,
            "tournament_date": data_iso,
            "tournament_date_full": data_show,
            "tournament_url": url_sito,
            "tournament_cat": cat,
            "logo_torneo_file": logo_t,
            "logo_cat_file": logo_c
        }

        try:
            supabase.table("ranking_data").upsert(payload).execute()
            return "<h1>✅ Slot Aggiornato con Successo!</h1><a href='/'>Vai alla Home</a>"
        except Exception as e:
            return f"<h1>❌ Errore: {e}</h1>"

    return render_template_string('''
        <div style="max-width:400px; margin:30px auto; font-family:sans-serif; border:1px solid #ddd; padding:20px; border-radius:10px;">
            <h2>🏆 Admin Calendario Multiplo</h2>
            <form method="POST">
                <label>Seleziona quale torneo vuoi inserire/cambiare:</label>
                <select name="torneo_id" style="width:100%; margin-bottom:15px; padding:8px; border-radius:5px;">
                    <option value="next_tournament_1">Torneo 1 (Slot Principale)</option>
                    <option value="next_tournament_2">Torneo 2 (Slot Secondario)</option>
                </select>
                <hr style="margin-bottom:15px; opacity:0.3;">
                
                <input type="text" name="nome" placeholder="Nome Torneo" style="width:100%; margin-bottom:10px;" required>
                <input type="text" name="data_iso" placeholder="Data Countdown (AAAA-MM-GG)" style="width:100%; margin-bottom:10px;" required>
                <input type="text" name="data_show" placeholder="Data da mostrare (es: 4-15 Marzo)" style="width:100%; margin-bottom:10px;" required>
                <input type="text" name="url_sito" placeholder="Link Sito Ufficiale" style="width:100%; margin-bottom:10px;" required>
                <select name="categoria" style="width:100%; margin-bottom:15px; padding:8px;">
                    <option value="WTA 1000">WTA 1000</option>
                    <option value="WTA 500">WTA 500</option>
                    <option value="WTA 250">WTA 250</option>
                </select>
                <button type="submit" style="width:100%; padding:12px; background:blue; color:white; border:none; cursor:pointer; font-weight:bold; border-radius:5px;">SALVA DATI</button>
            </form>
        </div>
    ''')
    
@app.route('/')
def home():
    t_lista = leggi_tornei()  # Assicurati che questa funzione esista sopra
    
    return render_template('index.html', 
                           tabella_html=leggi_da_db("singolo"), 
                           tabella_doppio_html=leggi_da_db("doppio"), 
                           race_singolare_html=leggi_da_db("race_singolo"), 
                           race_doppio_html=leggi_da_db("race_doppio"),
                           news_html=leggi_da_db("news"),
                           tornei=t_lista)

@app.route("/ask-ai", methods=["POST"])
def ask_ai():

    data = request.json
    user_message = data.get("message")

    prompt = f"""
You are an assistant specialized in tennis player Jasmine Paolini.

Answer questions about:
- Jasmine Paolini
- her career
- rankings
- tournaments
- results
- tennis information

Be concise and friendly.

User question:
{user_message}
"""

    try:

        response = model.generate_content(prompt)

        return jsonify({
            "reply": response.text
        })

    except Exception as e:

        return jsonify({
            "reply": "AI assistant temporarily unavailable."
        })

if __name__ == "__main__":
    # Prende la porta dall'ambiente (Koyeb/Render) o usa 8000 come fallback
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)













