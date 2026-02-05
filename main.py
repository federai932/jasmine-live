import flet as ft
import requests

def main(page: ft.Page):
    page.title = "Jasmine Live App"
    page.theme_mode = ft.ThemeMode.DARK
    
    # URL del tuo sito su Render dopo il deploy
    URL_SITO = "https://tua-app-jasmine.onrender.com"

    def refresh_data(e):
        page.add(ft.Text("Aggiornamento in corso..."))
        # In una versione reale qui useresti requests.get(f"{URL_SITO}/dati-json")
        page.update()

    page.add(
        ft.Image(src="jasmine_paolini.jpeg", width=100, height=100),
        ft.Text("Jasmine Paolini Live Stats", size=25, weight="bold"),
        ft.ElevatedButton("Aggiorna Classifiche", on_click=refresh_data),
        ft.Container(
            content=ft.Text("Visualizza i dati aggiornati dal server Render"),
            padding=20,
            bgcolor=ft.colors.SURFACE_VARIANT
        )
    )

ft.app(target=main)
