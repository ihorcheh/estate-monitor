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

# ПОВНИЙ СПИСОК САЙТІВ З ТВОГО ФАЙЛУ
URLS = [
    "https://www.x-estate.com/offers?city=5c87a27fe758c42fbc38bca3&category=5cf3da6afe460b4aa52ab4b9&sort=date&order=desc&page=1&currency=USD&min_price=1000&max_price=15000",
    "https://dom.ria.com/uk/search?excludeSold=1&category=1&realty_type=2&operation=1&state_id=7&price_cur=1&wo_dupl=1&sort=created_at&city_ids=7&client=searchV2&limit=20&type=list",
    "https://rem.ua/ua/search?type=apartments&region=kharkovskaya&city=kharkov&withoutSearchMarker=true&typeSort=rils_enot&priceMin=1000&priceMax=15000&hasPhotos=1&currency=1",
    "https://lun.ua/sale/kharkiv/flats?price_min=100000&price_max=700000&currency=UAH&sort=insert_time",
    "https://kn.ua/ua/flats/sale/?keyword=&city=1&price2%5Bfrom%5D=1000&price2%5Bto%5D=15000",
    "https://rieltor.ua/harkov/flats-sale/?price_min=100000&price_max=650000&radius=20&sort=bycreated",
    "https://valion.estate/uk/flats/search?mfsid=28f9c2efeb9b7384a1b80810045626bc"
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
            # Визначаємо домен для фільтрації посилань
            domain = url.split('/')[2].replace('www.', '')
            res = scraper.get(url, timeout=20)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                
                # Обробка відносних посилань (якщо сайт дає /offer/1 замість повного url)
                if href.startswith('/'):
                    href = f"https://{domain}{href}"
                
                # Перевірка: чи належить посилання сайту і чи ми його вже бачили
                if domain in href and href not in new_ids:
                    # Надсилаємо в Телеграм
                    msg = f"✨ Нова квартира на {domain}!\n{href}"
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                  json={"chat_id": CHAT_ID, "text": msg})
                    new_ids.add(href)
                    count += 1
        except Exception as e:
            print(f"Помилка при перевірці {url}: {e}")
            continue

    save_ids(new_ids)
    print(f"Готово. Знайдено нових: {count}")

if __name__ == "__main__":
    check_sites()
