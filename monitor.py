import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Твоє налаштоване посилання на Харків
URLS = {
    "LUN/Flatfy": "https://lun.ua/sale/kharkiv/flats?price_min=150000&price_max=800000&currency=UAH&sort=price-asc"
}

def check():
    if not TOKEN or not CHAT_ID:
        print("Помилка: Secrets не налаштовані")
        return

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    }
    
    last_ids = {}
    if os.path.exists("last_id.txt"):
        try:
            with open("last_id.txt", "r") as f:
                for line in f:
                    if ":" in line:
                        k, v = line.strip().split(":", 1)
                        last_ids[k] = v
        except: pass

    for name, url in URLS.items():
        try:
            res = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Шукаємо перше оголошення на LUN
            offer = soup.find('a', class_=lambda x: x and 'realty-preview__title-link' in x, href=True)
            
            if offer:
                link = "https://flatfy.ua" + offer['href'] if offer['href'].startswith('/') else offer['href']
                
                if link != last_ids.get(name):
                    msg = f"🏙 {name}: Нова пропозиція в Харкові!\nЦіна за твоїм фільтром: {link}"
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                  json={"chat_id": CHAT_ID, "text": msg})
                    last_ids[name] = link
                    print(f"Знайдено нове оголошення на {name}")
                else:
                    print(f"На {name} нових оголошень немає")
        except Exception as e:
            print(f"Помилка на {name}: {e}")

    with open("last_id.txt", "w") as f:
        for name, link in last_ids.items():
            f.write(f"{name}:{link}\n")

if __name__ == "__main__":
    check()
