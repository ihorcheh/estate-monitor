import cloudscraper
from bs4 import BeautifulSoup
import os
import requests
import json

# ТВОЇ НАЛАШТУВАННЯ
TOKEN = "8597947732:AAF4d-Gn6vZklzxI7CtG8nwjuijA46ebtAo"
CHAT_ID = "710609623"
GIST_ID = "9bfd0cb3e109e85aed617eaaa5fdb25a"
GIST_TOKEN = os.getenv("MY_GIST_TOKEN")

URLS = [
    "https://www.x-estate.com/offers?city=5c87a27fe758c42fbc38bca3&category=5cf3da6afe460b4aa52ab4b9&sort=date&order=desc&min_price=1000&max_price=15000",
    "https://dom.ria.com/uk/search?category=1&realty_type=2&operation=1&state_id=7&city_ids=7&price_cur=1&sort=created_at",
    "https://rem.ua/ua/search?type=apartments&city=kharkov&priceMin=1000&priceMax=15000&currency=1"
]

def get_seen_ids():
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {"Authorization": f"token {GIST_TOKEN}"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        content = r.json()['files']['seen_ids.txt']['content']
        return set(content.splitlines())
    except:
        return set()

def save_ids(all_ids):
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {"Authorization": f"token {GIST_TOKEN}"}
    data = {"files": {"seen_ids.txt": {"content": "\n".join(all_ids)}}}
    requests.patch(url, headers=headers, data=json.dumps(data), timeout=10)

def check_sites():
    seen_ids = get_seen_ids()
    new_ids = seen_ids.copy()
    count = 0
    scraper = cloudscraper.create_scraper()

    for url in URLS:
        try:
            domain = url.split('/')[2]
            res = scraper.get(url, timeout=20)
            soup = BeautifulSoup(res.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if "http" in href and href not in new_ids:
                    # Надсилаємо в Телеграм
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                  json={"chat_id": CHAT_ID, "text": f"✨ Нова квартира!\n{href}"})
                    new_ids.add(href)
                    count += 1
        except: continue

    save_ids(new_ids)
    print(f"Готово. Знайдено нових: {count}")

if __name__ == "__main__":
    check_sites()
