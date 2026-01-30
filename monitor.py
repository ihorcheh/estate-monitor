import cloudscraper
from bs4 import BeautifulSoup
import time
import os
import random

# Дані з GitHub Secrets
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

URLS = [
    "https://www.x-estate.com/offers?city=5c87a27fe758c42fbc38bca3&category=5cf3da6afe460b4aa52ab4b9&sort=date&order=desc&min_price=1000&max_price=15000",
    "https://dom.ria.com/uk/search?category=1&realty_type=2&operation=1&state_id=7&city_ids=7&price_cur=1&sort=created_at",
    "https://rem.ua/ua/search?type=apartments&city=kharkov&priceMin=1000&priceMax=15000&currency=1",
    "https://lun.ua/sale/kharkiv/flats?price_min=100000&price_max=700000&currency=UAH&sort=insert_time",
    "https://kn.ua/ua/flats/sale/?city=1&price2%5Bfrom%5D=1000&price2%5Bto%5D=15000&sort=date",
    "https://rieltor.ua/harkov/flats-sale/?price_min=100000&price_max=650000&sort=bycreated",
    "https://valion.estate/uk/flats/search"
]

DB_FILE = "seen_ids.txt"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, params=params)
    except:
        pass

def get_seen_ids():
    if not os.path.exists(DB_FILE):
        return set()
    with open(DB_FILE, 'r') as f:
        return set(line.strip() for line in f)

def save_id(realty_id):
    with open(DB_FILE, 'a') as f:
        f.write(f"{realty_id}\n")

def check_sites():
    seen_ids = get_seen_ids()
    # Створюємо "розумний" сканер, який обходить захист
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    for url in URLS:
        try:
            site_name = url.split('/')[2]
            print(f"Сканування: {site_name}")
            
            # Випадкова затримка перед кожним сайтом, щоб не спалитись
            time.sleep(random.uniform(3, 7))
            
            response = scraper.get(url, timeout=20)
            if response.status_code != 200:
                print(f"Сайт {site_name} повернув помилку {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            links = []

            # Покращений пошук посилань
            for a in soup.find_all('a', href=True):
                href = a['href']
                # Специфічні фільтри для нерухомості
                is_realty = any(x in href.lower() for x in ['offer', 'realty', 'flat', 'apartments', 'uk/flats', 'sale/'])
                
                if is_realty:
                    if href.startswith('/'):
                        domain = url.split('/')[0] + "//" + url.split('/')[2]
                        href = domain + href
                    
                    if href not in seen_ids and site_name in href:
                        links.append(href)

            # Відправляємо тільки найсвіжіші (перші 3)
            for link in list(dict.fromkeys(links))[:3]:
                send_msg(f"✨ <b>Знайдено об'єкт!</b>\n\n📍 Джерело: {site_name}\n🔗 <a href='{link}'>Відкрити оголошення</a>")
                save_id(link)
                seen_ids.add(link)
                time.sleep(1)

        except Exception as e:
            print(f"Помилка {url}: {e}")

if __name__ == "__main__":
    check_sites()
