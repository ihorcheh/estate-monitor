import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Твої чотири джерела моніторингу в Харкові
URLS = {
    "LUN_Kharkiv": "https://lun.ua/sale/kharkiv/flats?price_min=150000&price_max=800000&currency=UAH&sort=price-asc",
    "REM_Kharkiv": "https://rem.ua/ua/search?type=apartments&region=kharkovskaya&city=kharkov&withoutSearchMarker=true&typeSort=rils_enot&district=z-10021,z-395&priceMin=3000&priceMax=17000&hasPhotos=1&currency=1",
    "AN_Gorod": "https://an-gorod.com.ua/real/flat/sale?sub_locality_id[]=192&sub_locality_id[]=1553&price_from=3000&price_to=17000",
    "X_Estate": "https://www.x-estate.com/offers?city=5c87a27fe758c42fbc38bca3&category=5cf3da6afe460b4aa52ab4b9&sort=price&order=asc&page=1&currency=USD&geo_ids=28%2C57%2C29&min_price=3000&max_price=17000"
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
                offer = soup.find('a', class_='object-link', href=True)
                if offer:
                    link = offer['href'] if offer['href'].startswith('http') else "https://rem.ua" + offer['href']

            elif name == "AN_Gorod":
                offer = soup.find('a', class_='realty-item__title', href=True)
                if offer:
                    link = "https://an-gorod.com.ua" + offer['href'] if offer['href'].startswith('/') else offer['href']
            
            elif name == "X_Estate":
                # Спеціальний пошук для карток X-Estate
                offer = soup.find('a', href=True, class_=lambda x: x and 'offer-card' in x)
                if offer:
                    link = "https://www.x-estate.com" + offer['href'] if offer['href'].startswith('/') else offer['href']

            if link and link != last_ids.get(name):
                labels = {
                    "LUN_Kharkiv": "🏙 ЛУН", 
                    "REM_Kharkiv": "🏠 REM.ua", 
                    "AN_Gorod": "🏢 АН Город",
                    "X_Estate": "💎 X-Estate"
                }
                msg = f"{labels.get(name, name)}: Нова знахідка!\n\n🔗 {link}"
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                              json={"chat_id": CHAT_ID, "text": msg})
                last_ids[name] = link
                print(f"Знайдено нове на {name}")
            else:
                print(f"На {name} без змін")
                
        except Exception as e:
            print(f"Помилка на {name}: {e}")

    with open("last_id.txt", "w") as f:
        for name, l in last_ids.items():
            f.write(f"{name}:{l}\n")

if __name__ == "__main__":
    check()
