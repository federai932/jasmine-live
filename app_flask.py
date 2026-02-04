import os
from flask import Flask, render_template

app = Flask(__name__)

# --- INSERISCI QUI LE TUE ROTTE ORIGINALI ---
# Esempio di rotta principale (modificala se hai già una index)
@app.route('/')
def home():
    return "<h1>Benvenuto su Jasmine Live</h1><p>I dati dei ranking sono in fase di aggiornamento...</p>"

# Se hai altre rotte come @app.route('/ranking'), incollale qui sotto
# --------------------------------------------

# LOGICA DI AVVIO PER RENDER
if __name__ == "__main__":
    # Importante: Render usa una porta dinamica, non forzare la 5000
    port = int(os.environ.get("PORT", 5000))
    # Host 0.0.0.0 è obbligatorio per rendere il sito accessibile dall'APK
    app.run(host='0.0.0.0', port=port, debug=False)


