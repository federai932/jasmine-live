import os
from flask import Flask, render_template
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

def leggi_torneo():
    """Recupera i dati per la card del calendario dalle nuove colonne."""
    try:
        res = supabase.table("ranking_data").select("*").eq("id", "next_tournament").execute()
        if res.data and len(res.data) > 0:
            d = res.data[0]
            return {
                "name": d.get('tournament_name') or "In aggiornamento...",
                "date": d.get('tournament_date') or "Entry List WTA",
                "cat": d.get('tournament_cat') or "WTA",
                "surf": d.get('tournament_surf') or "Hard",
                "logo_cat": d.get('logo_cat_file') or "default_cat.png",
                "logo_torneo": d.get('logo_torneo_file') or "default_torneo.png"
            }
        return {"name": "Dati non trovati", "date": "-", "cat": "WTA"}
    except Exception as e:
        print(f"Errore lettura torneo: {e}")
        return {"name": "Errore Connessione", "date": "-"}

@app.route('/admin-torneo', methods=['GET', 'POST'])
def admin_torneo():
    if request.method == 'POST':
        nome = request.form.get('nome')
        data = request.form.get('data')
        cat = request.form.get('categoria')
        surf = request.form.get('superficie')
        
        # Generazione nomi file: "Indian Wells" -> "indian_wells.png"
        logo_t = nome.lower().replace(" ", "_") + ".png"
        logo_c = cat.lower().replace(" ", "") + ".png"

        payload = {
            "id": "next_tournament",
            "tournament_name": nome,
            "tournament_date": data,
            "tournament_cat": cat,
            "tournament_surf": surf,
            "logo_torneo_file": logo_t,
            "logo_cat_file": logo_c
        }

        try:
            supabase.table("ranking_data").upsert(payload).execute()
            return "<h1>✅ Torneo Aggiornato!</h1><a href='/'>Vai alla Home</a>"
        except Exception as e:
            return f"<h1>❌ Errore: {e}</h1>"

    return render_template_string('''
        <div style="max-width:400px; margin:50px auto; font-family:sans-serif; border:1px solid #ddd; padding:20px; border-radius:10px;">
            <h2>🏆 Admin Calendario</h2>
            <form method="POST">
                <input type="text" name="nome" placeholder="Nome Torneo" style="width:100%; margin-bottom:10px;" required><br>
                <input type="text" name="data" placeholder="Data (es: 10-20 Marzo)" style="width:100%; margin-bottom:10px;" required><br>
                <select name="categoria" style="width:100%; margin-bottom:10px;">
                    <option value="WTA 1000">WTA 1000</option>
                    <option value="WTA 500">WTA 500</option>
                    <option value="WTA 250">WTA 250</option>
                </select><br>
                <input type="text" name="superficie" placeholder="Superficie (es: Hard)" style="width:100%; margin-bottom:10px;" required><br>
                <button type="submit" style="width:100%; padding:10px; background:blue; color:white;">AGGIORNA</button>
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)



