import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

def cerca_notizie_jasmine():
    notizie = []
    link_visti = set()
    fonti = [
        {"url": "https://www.oasport.it", "fonte": "OA Sport"},
        {"url": "https://www.sportmediaset.mediaset.it", "fonte": "SportMediaset"},
        {"url": "https://www.ubitennis.com", "fonte": "Ubitennis"},
        {"url": "https://www.eurosport.it", "fonte": "Eurosport"}
    ]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    for f in fonti:
        try:
            r = requests.get(f['url'], headers=headers, timeout=12)
            r.encoding = 'utf-8'
            soup = BeautifulSoup(r.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                titolo = a.get_text().strip()
                link = a['href']
                if link.startswith('/'): link = requests.compat.urljoin(f['url'], link)
                
                if "paolini" in titolo.lower() or "paolini" in link.lower():
                    if "/2024/" in link or "/2025/11/" in link: continue
                    if link not in link_visti and len(titolo) > 25:
                        img_url = "https://via.placeholder.com"
                        img_tag = a.find('img') or a.find_next('img')
                        if img_tag:
                            src = img_tag.get('data-src') or img_tag.get('src')
                            if src and not src.startswith('data:image'): img_url = requests.compat.urljoin(f['url'], src)
                        
                        notizie.append({
                            'titolo': titolo[:95], 'link': link, 'fonte': f['fonte'], 
                            'data': datetime.now().strftime('%d %b %H:%M'), 'immagine': img_url
                        })
                        link_visti.add(link)
        except: continue

    html = '<div class="news-grid">'
    if not notizie:
        html += '<p style="color:white; padding:20px;">Nessuna notizia trovata.</p>'
    else:
        for n in notizie[:10]:
            html += f'''
            <a href="{n['link']}" target="_blank" class="news-item">
                <div class="news-content">
                    <span class="news-source">{n['fonte']}</span>
                    <span class="news-title">{n['titolo']}</span>
                    <span class="news-time">{n['data']}</span>
                </div>
                <div class="news-image-container"><img src="{n['immagine']}" alt="News" loading="lazy"></div>
            </a>'''
    html += '</div>'

    output_path = os.path.join(os.path.dirname(__file__), "static", "news_section.html")
    with open(output_path, "w", encoding="utf-8") as f_out:
        f_out.write(html)
    
    # IMPORTANTE: Restituisce un messaggio per app.py
    return f"News Aggiornate ({len(notizie)} articoli)"


