import requests
from bs4 import BeautifulSoup
import time
import os

# Твої дані з секретів GitHub
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Список твоїх посилань
URLS = [
    "https://www.x-estate.com/offers?city=5c87a27fe758c42fbc38bca3&category=5cf3da6afe460b4aa52ab4b9&sort=date&order=desc&min_price=1000&max_price=15000",
    "https://dom.ria.com/uk/search?category=1&realty_type=2&operation=1&state_id=7&city_ids=7&price_cur=1&sort=created_at",
    "https://rem.ua/ua/search?type=apartments&city=kharkov&priceMin=1000&priceMax=15000&currency=1",
    "https://lun.ua/sale/kharkiv/flats?price_min=100000&price_max=700000&currency=UAH&sort=insert_time",
    "https://kn.ua/ua/flats/sale/?city=1&price2%5Bfrom%5D=1000&price2%5Bto%5D=15000&sort=date",
    "https://rieltor.ua/harkov/flats-sale/?price_min=100000&price_max=650000&sort=bycreated",
    "https://valion.estate/uk/flats/search"
]

# Файл для збереження знайдених ID оголошень, щоб не спамити дублями
DB_FILE = "seen_ids.txt"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.get(url, params=params)

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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    for url in URLS:
        try:
            print(f"Перевіряю: {url.split('/')[2]}") # Друкує назву сайту в лог
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Шукаємо посилання на оголошення (спрощений пошук для всіх сайтів)
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                # Фільтруємо тільки посилання, схожі на оголошення
                if any(x in href for x in ['offer', 'realty', 'flat', 'apartments', 'uk/flats']):
                    if href.startswith('/'):
                        # Додаємо домен, якщо посилання відносне
                        domain = url.split('/')[0] + "//" + url.split('/')[2]
                        href = domain + href
                    if href not in seen_ids and url.split('/')[2] in href:
                        links.append(href)
            
            # Беремо тільки перші 2 нові посилання з кожного сайту, щоб не забанили
            for link in links[:2]:
                send_msg(f"🏠 <b>Новий об'єкт!</b>\n\nДжерело: {url.split('/')[2]}\nПокликання: {link}")
                save_id(link)
                seen_ids.add(link)
                time.sleep(2) # Пауза між повідомленнями

        except Exception as e:
            print(f"Помилка при перевірці {url}: {e}")

if __name__ == "__main__":
    check_sites()
