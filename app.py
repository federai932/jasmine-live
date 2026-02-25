import os
from flask import Flask, render_template, request, redirect, render_template_string
from supabase import create_client

app = Flask(__name__)
# --- CONFIGURAZIONE SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def leggi_da_db(id_rank):
    """Recupera il contenuto HTML (Ranking e News)."""
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        if res.data:
            return res.data[0]['html_content']
        return f"<p>Dati {id_rank} non trovati.</p>"
    except Exception:
        return f"<p>Errore Database {id_rank}</p>"

# --- FUNZIONE LETTURA TORNEO AGGIORNATA ---
def leggi_torneo():
    try:
        res = supabase.table("ranking_data").select("*").eq("id", "next_tournament").execute()
        if res.data and len(res.data) > 0:
            d = res.data[0]
            return {
                "name": d.get('tournament_name') or "In aggiornamento...",
                "date_iso": d.get('tournament_date') or "2025-01-01", 
                "date_show": d.get('tournament_date_full') or "Data da definire",
                "cat": d.get('tournament_cat') or "WTA",
                "logo_cat": d.get('logo_cat_file') or "default_cat.png",
                "logo_torneo": d.get('logo_torneo_file') or "default_torneo.png",
                "url": d.get('tournament_url') or "#"
            }
        return {"name": "Dati non trovati", "date_iso": "2025-01-01"}
    except Exception:
        return {"name": "Errore Connessione", "date_iso": "2025-01-01"}

# --- ROTTA ADMIN ---
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
                <input type="text" name="url_sito" placeholder="Link Sito Ufficiale (http://...)" style="width:100%; margin-bottom:10px;" required>
                <select name="categoria" style="width:100%; margin-bottom:10px;">
                    <option value="WTA 1000">WTA 1000</option>
                    <option value="WTA 500">WTA 500</option>
                    <option value="WTA 250">WTA 250</option>
                </select>
                <button type="submit" style="width:100%; padding:10px; background:blue; color:white; border:none; cursor:pointer;">AGGIORNA</button>
            </form>
        </div>
    ''')

# --- ROTTA HOME (MANCANTE NEL TUO PEZZO) ---
@app.route('/')
def home():
    t = leggi_torneo()
    return render_template('index.html', 
                           tabella_html=leggi_da_db("singolo"), 
                           tabella_doppio_html=leggi_da_db("doppio"), 
                           news_html=leggi_da_db("news"),
                           torneo=t)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)






