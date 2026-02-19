import os
from flask import Flask, render_template, request, jsonify
from supabase import create_client
import google.generativeai as genai

app = Flask(__name__)

# --- SUPABASE CONFIGURATION ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- GOOGLE GEMINI CONFIGURATION ---
# Use your API key: AIzaSyBB5TUGLgtqipDjhKvS4437_9MOQujJM-U
# NOTE: For security on Render, it's better to put it in Env Vars as GOOGLE_API_KEY
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", "AIzaSyBB5TUGLgtqipDjhKvS4437_9MOQujJM-U"))
model = genai.GenerativeModel('gemini-pro')

def leggi_da_db(id_rank):
    """Retrieves HTML content from Supabase."""
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        if res.data:
            return res.data[0]['html_content']
        return f"<p>Data {id_rank} not found.</p>"
    except Exception as e:
        return f"<p>DB Error: {e}</p>"

@app.route('/')
def home():
    """Main page."""
    return render_template('index.html',
                           tabella_html=leggi_da_db("singolo"),
                           tabella_doppio_html=leggi_da_db("doppio"),
                           news_html=leggi_da_db("news"))

@app.route('/chat', methods=['POST'])
def chat():
    """Gemini Chatbot route."""
    user_message = request.json.get("message")
    context = (
        "You are the virtual assistant for the 'Game Set Jasmine' app. "
        "Answer questions about Jasmine Paolini (Italian tennis player, world no. 8). "
        "Be friendly, sporty and precise. If you don't know something, invite to follow the live matches."
    )
    try:
        response = model.generate_content(f"{context}\nUser: {user_message}")
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": "Sorry, my coach says I need to rest. Try again later!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)





