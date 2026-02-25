import os
from flask import Flask, render_template, request, redirect, render_template_string
from supabase import create_client

app = Flask(__name__)

# --- CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def leggi_da_db(id_rank):
    """Funzione per recuperare il contenuto HTML dal database."""
    try:
        # Recupera la riga dal database dove l'id è 'singolo', 'doppio' o 'news'
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        # Se trova i dati, li restituisce; altrimenti, mostra un messaggio
        if res.data:
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non trovati nel database.</p>"
    except Exception as e:
        return f"<p>Errore di connessione al Database: {e}</p>"
        
def leggi_torneo():
    """Recupera i dati del torneo in modo sicuro."""
    try:
        res = supabase.table("ranking_data").select("*").eq("id", "next_tournament").execute()
        if res.data and len(res.data) > 0:
            d = res.data[0] # Prendiamo il primo risultato
            return {
                "name": d.get('tournament_name', "In aggiornamento..."),
                "date_iso": d.get('tournament_date', "2025-01-01"), 
                "date_show": d.get('tournament_date_full', "Data da definire"), 
                "cat": d.get('tournament_cat', "WTA"),
                "logo_cat": d.get('logo_cat_file', "default_cat.png"),
                "logo_torneo": d.get('logo_torneo_file', "default_torneo.png"),
                "url": d.get('tournament_url', "#")
            }
        # Valori di emergenza se la riga non esiste
        return {"name": "In aggiornamento...", "date_iso": "2025-01-01", "date_show": "-", "cat": "WTA", "url": "#"}
    except Exception as e:
        print(f"Errore lettura torneo: {e}")
        return {"name": "Errore Connessione", "date_iso": "2025-01-01", "url": "#"}

@app.route('/admin-torneo', methods=['GET', 'POST'])
def admin_torneo():
    if request.method == 'POST':
        nome = request.form.get('nome')
        data_iso = request.form.get('data_iso')   
        data_show = request.form.get('data_show') 
        url_sito = request.form.get('url_sito')
        cat = request.form.get('categoria')
        
        logo_t = nome.lower().replace(" ", "_") + ".png"
        logo_c = cat.lower().replace(" ", "") + ".png"

        payload = {
            "id": "next_tournament",
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
            return "<h1>✅ Torneo Aggiornato!</h1><a href='/'>Vai alla Home</a>"
        except Exception as e:
            return f"<h1>❌ Errore: {e}</h1>"

    return render_template_string('''
        <div style="max-width:400px; margin:30px auto; font-family:sans-serif; border:1px solid #ddd; padding:20px; border-radius:10px;">
            <h2>🏆 Admin Calendario</h2>
            <form method="POST">
                <input type="text" name="nome" placeholder="Nome Torneo" style="width:100%; margin-bottom:10px;" required>
                <input type="text" name="data_iso" placeholder="Data Countdown (AAAA-MM-GG)" style="width:100%; margin-bottom:10px;" required>
                <input type="text" name="data_show" placeholder="Data da mostrare (es: 4-15 Marzo)" style="width:100%; margin-bottom:10px;" required>
                <input type="text" name="url_sito" placeholder="Link Sito Ufficiale" style="width:100%; margin-bottom:10px;" required>
                <select name="categoria" style="width:100%; margin-bottom:10px;">
                    <option value="WTA 1000">WTA 1000</option>
                    <option value="WTA 500">WTA 500</option>
                    <option value="WTA 250">WTA 250</option>
                </select>
                <button type="submit" style="width:100%; padding:10px; background:blue; color:white; border:none; cursor:pointer;">AGGIORNA</button>
            </form>
        </div>
    ''')

@app.route('/')
def home():
    t = leggi_torneo()
    return render_template('index.html', 
                           tabella_html=leggi_da_db("singolo"), 
                           tabella_doppio_html=leggi_da_db("doppio"), 
                           news_html=leggi_da_db("news"),
                           torneo=t)

if __name__ == "__main__":
    # Usa la porta di Render (10000) o la 5000 se sei in locale
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)







