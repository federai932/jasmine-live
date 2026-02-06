import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

def cerca_notizie_jasmine():
    notizie = []
    link_visti = set()
    
    # Fonti mirate: usiamo i tag specifici per Jasmine Paolini dove possibile
    fonti = [
        {"url": "https://www.oasport.it", "fonte": "OA Sport"},
        {"url": "https://www.sportmediaset.mediaset.it", "fonte": "SportMediaset"},
        {"url": "https://www.corrieredellosport.it", "fonte": "Corriere dello Sport"},
        {"url": "https://www.supertennis.tv", "fonte": "SuperTennis"},
        {"url": "https://www.ubitennis.com", "fonte": "Ubitennis"},
        {"url": "https://www.eurosport.it", "fonte": "Eurosport"}
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for f in fonti:
        try:
            r = requests.get(f['url'], headers=headers, timeout=12)
            r.encoding = 'utf-8'
            soup = BeautifulSoup(r.text, 'html.parser')
            
            for a in soup.find_all('a', href=True):
                titolo = a.get_text().strip()
                link = a['href']
                
                # Gestione link relativi
                if link.startswith('/'):
                    link = requests.compat.urljoin(f['url'], link)
                
                # REGOLE DI FILTRO:
                # 1. Deve esserci "paolini"
                # 2. Escludiamo il 2024 e specificamente Novembre 2025 (/11/)
                # 3. Accettiamo tutto il 2026 (Gennaio e Febbraio)
                if "paolini" in titolo.lower() or "paolini" in link.lower():
                    if "/2024/" in link or "/2025/11/" in link or "-202511" in link:
                        continue
                    
                    if link not in link_visti and len(titolo) > 25:
                        
                        # --- RECUPERO IMMAGINE (FIX UBITENNIS & OA SPORT) ---
                        img_url = "https://via.placeholder.com"
                        img_tag = a.find('img') or a.find_next('img')
                        
                        if img_tag:
                            # Controlliamo tutti i tag possibili dove i siti nascondono le foto
                            img_src = (img_tag.get('data-src') or 
                                       img_tag.get('data-lazy-src') or 
                                       img_tag.get('src') or
                                       img_tag.get('data-original'))
                            
                            if img_src and not img_src.startswith('data:image'):
                                img_url = requests.compat.urljoin(f['url'], img_src)
                        
                        # Pulizia titolo
                        titolo_pulito = (titolo[:95] + '...') if len(titolo) > 95 else titolo

                        notizie.append({
                            'titolo': titolo_pulito, 
                            'link': link, 
                            'fonte': f['fonte'],
                            'data': datetime.now().strftime('%d %b %H:%M'),
                            'immagine': img_url
                        })
                        link_visti.add(link)
        except Exception as e:
            print(f"Errore su {f['fonte']}: {e}")
            continue

    # Generazione Griglia HTML
    html = '<div class="news-grid">'
    if not notizie:
        html += '<p style="color:white; padding:20px;">Nessun articolo recente trovato (Febbraio 2026).</p>'
    else:
        # Prende i primi 10 articoli
        for n in notizie[:10]:
            html += f'''
            <a href="{n['link']}" target="_blank" class="news-item">
                <div class="news-content">
                    <span class="news-source">{n['fonte']}</span>
                    <span class="news-title">{n['titolo']}</span>
                    <span class="news-time">{n['data']}</span>
                </div>
                <div class="news-image-container">
                    <img src="{n['immagine']}" alt="News Paolini" loading="lazy">
                </div>
            </a>'''
    html += '</div>'

    # Percorso salvataggio
    path_news = r"C:\Users\fedec\OneDrive\Desktop\Sito Web\news_section.html"
    
    try:
        os.makedirs(os.path.dirname(path_news), exist_ok=True)
        with open(path_news, "w", encoding="utf-8") as f_out:
            f_out.write(html)
        print(f"Aggiornato alle {datetime.now().strftime('%H:%M')}! Articoli validi: {len(notizie)}")
    except Exception as e:
        print(f"Errore nel salvataggio: {e}")

if __name__ == "__main__":
    cerca_notizie_jasmine()


