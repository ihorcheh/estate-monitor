import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Твої персоналізовані посилання
URLS = {
    "LUN_Kharkiv": "https://lun.ua/sale/kharkiv/flats?price_min=150000&price_max=800000&currency=UAH&sort=price-asc",
    "REM_Kharkiv": "https://rem.ua/ua/search?type=apartments&region=kharkovskaya&city=kharkov&withoutSearchMarker=true&typeSort=rils_enot&district=z-10021,z-395&priceMin=3000&priceMax=17000&hasPhotos=1&currency=1"
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
                        last_ids[k] = v.strip()
        except: pass

    for name, url in URLS.items():
        try:
            res = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            link = ""

            if name == "LUN_Kharkiv":
                offer = soup.find('a', class_=lambda x: x and 'realty-preview__title-link' in x, href=True)
                if offer:
                    link = "https://lun.ua" + offer['href'] if offer['href'].startswith('/') else offer['href']
            
            elif name == "REM_Kharkiv":
                # Шукаємо перше посилання на квартиру в списку REM
                offer = soup.find('a', class_='object-link', href=True)
                if offer:
                    link = offer['href'] if offer['href'].startswith('http') else "https://rem.ua" + offer['href']

            if link and link != last_ids.get(name):
                site_label = "🏙 ЛУН" if "LUN" in name else "🏠 REM.ua"
                msg = f"{site_label}: Знайдено новий варіант!\n\n🔗 {link}"
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                              json={"chat_id": CHAT_ID, "text": msg})
                last_ids[name] = link
                print(f"Знайдено нове на {name}")
            else:
                print(f"На {name} без змін")
                
        except Exception as e:
            print(f"Помилка на {name}: {e}")

    # Зберігаємо стан для обох сайтів
    with open("last_id.txt", "w") as f:
        for name, l in last_ids.items():
            f.write(f"{name}:{l}\n")

if __name__ == "__main__":
    check()
