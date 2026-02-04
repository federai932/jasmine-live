import flet as ft
import threading
import time
import subprocess
from app_flask import app 

# Funzione per far girare Flask
def run_flask():
    app.run(port=5000, debug=False, use_reloader=False)

# Funzione per lanciare gli scraper (così i dati appaiono subito)
def avvia_scraper():
    print("Aggiornamento dati in corso...")
    subprocess.run(["python", "news_scraper.py"])
    subprocess.run(["python", "ranking.py"])
    subprocess.run(["python", "prendi_ranking_doppio.py"])
    print("Dati pronti!")

def main(page: ft.Page):
    page.title = "Jasmine Live"
    page.window_width = 400
    page.window_height = 700
    page.padding = 0
    
    # 1. Avviamo gli scraper prima di tutto
    avvia_scraper()

    # 2. Avviamo Flask in sottofondo
    threading.Thread(target=run_flask, daemon=True).start()
    
    # 3. Messaggio di caricamento con allineamento corretto
    loading_container = ft.Container(
        content=ft.Text("Caricamento Ranking...", size=20),
        alignment=ft.alignment.center, # In alcune versioni usa ft.Alignment(0,0)
        expand=True
    )
    page.add(loading_container)
    page.update()

    # Aspettiamo che Flask sia pronto
    time.sleep(3)
    
    # 4. Carichiamo il sito (launch_url lo apre nel browser interno/esterno)
    page.launch_url("http://127.0.0.1:5000")
    
    # Opzionale: aggiungi un bottone per ricaricare se non lo vedi
    page.add(ft.ElevatedButton("Ricarica Sito", on_click=lambda _: page.launch_url("http://127.0.0.1:5000")))
    page.update()

ft.app(target=main)
