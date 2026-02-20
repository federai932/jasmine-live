import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from supabase import create_client

app = Flask(__name__)

# --- SUPABASE CONFIGURATION ---
# Ensure SUPABASE_URL and SUPABASE_KEY are in Render's Env Vars
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- GOOGLE GEMINI CONFIGURATION (STABLE VERSION V1) ---
api_key = os.environ.get("GOOGLE_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # Use gemini-1.5-flash: faster, stable, and free
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
    except Exception as e:
        print(f"GEMINI INITIALIZATION ERROR: {e}")
else:
    print("WARNING: GOOGLE_API_KEY not found in environment variables!")

def leggi_da_db(id_rank):
    """Retrieves the HTML content saved in the Supabase database."""
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        # Verify if data exists before accessing the index
        if res.data and len(res.data) > 0:
            return res.data[0]['html_content']
        return f"<p>Data {id_rank} not found in the database.</p>"
    except Exception as e:
        print(f"DATABASE ERROR: {e}")
        return f"<p>Database connection error.</p>"

@app.route('/')
def home():
    """Main route that loads the app interface with data from the DB."""
    return render_template('index.html',
                           tabella_html=leggi_da_db("singolo"),
                           tabella_doppio_html=leggi_da_db("doppio"),
                           news_html=leggi_da_db("news"))

@app.route('/chat', methods=['POST'])
def chat():
    """Handles the IA Chatbot logic on Jasmine Paolini."""
    if not api_key:
        return jsonify({"response": "Chat configuration not found (missing API Key)."})

    user_message = request.json.get("message")

    # Context instructions (Prompt Engineering) in Italian
    context = (
        "You are the official virtual assistant of the 'Game Set Jasmine' app. "
        "Answer questions about Jasmine Paolini, Italian tennis player ranked 8th in the world. "
        "Be technical, friendly, and passionate. If you don't know a specific detail, "
        "recommend checking the Match section or the WTA Calendar."
    )

    try:
        # Response generation with the stable model
        response = model.generate_content(f"{context}\n\nUser: {user_message}")
        return jsonify({"response": response.text})
    except Exception as e:
        print(f"GEMINI ERROR: {e}")
        # Return the technical error for debugging in Render logs
        return jsonify({"response": f"The coach says there is a technical problem: {str(e)}"})

# Startup for Render
if __name__ == "__main__":
    # Render assigns a dynamic port through the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)




