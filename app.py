import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from supabase import create_client

app = Flask(__name__)

# --- SUPABASE CONFIGURATION ---
# Ensure these variables are set correctly on Render
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- GOOGLE GEMINI CONFIGURATION (Version 1.5 Flash - STABLE) ---
api_key = os.environ.get("GOOGLE_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # Use the 1.5 flash model, which is the most current and free
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"GEMINI INITIALIZATION ERROR: {e}")
else:
    print("WARNING: GOOGLE_API_KEY not found in environment variables!")

def leggi_da_db(id_rank):
    """Retrieves the HTML content saved in the Supabase database."""
    try:
        res = supabase.table("ranking_data").select("html_content").eq("id", id_rank).execute()
        # Note: res.data is a list, take the first element
        if res.data and len(res.data) > 0:
            return res.data[0]['html_content']
        return f"<p>Data {id_rank} not found in the database.</p>"
    except Exception as e:
        print(f"DATABASE ERROR: {e}")
        return f"<p>Database connection error.</p>"

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
        return jsonify({"response": "Chat configuration not found on the server."})

    user_message = request.json.get("message")
    
    # Context instructions (Prompt Engineering)
    context = (
        "You are the official virtual assistant for the app 'Game Set Jasmine'. "
        "Answer questions about Jasmine Paolini, a top 10 world-ranked Italian tennis player. "
        "Be technical, friendly, and speak as if you were part of her team. "
        "Use information from her bio: born Jan 4, 1996, 1.63m tall, coach Danilo Pizzorno and Sara Errani."
    )

    try:
        # Response generation
        response = model.generate_content(f"{context}\n\nUser question: {user_message}")
        return jsonify({"response": response.text})
    except Exception as e:
        print(f"GEMINI ERROR: {e}")
        return jsonify({"response": f"The coach says there's a technical problem: {str(e)}"})

# Startup for Render
if __name__ == "__main__":
    # Render assigns the port automatically
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)




