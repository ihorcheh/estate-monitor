import requests
from bs4 import BeautifulSoup
import os

# Беремо ключі з налаштувань
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = "https://www.x-estate.com/offers?city=5c87a27fe758c42fbc38bca3&category=5cf3da6afe460b4aa52ab4b9&page=1&currency=USD&sort=price&order=asc&geo_ids=28%2C57%2C29&min_price=3000&max_price=17000"

def check():
    if not TOKEN or not CHAT_ID:
        print("Помилка: Ключі (Secrets) не налаштовані!")
        return

    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"}
    
    try:
        res = requests.get(URL, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        offer = soup.find('a', href=True, class_=lambda x: x and 'offer-card' in x)
        
        if offer:
            link = "https://www.x-estate.com" + offer['href']
            
            # Перевірка на новизну
            last_id = ""
            if os.path.exists("last_id.txt"):
                with open("last_id.txt", "r") as f:
                    last_id = f.read().strip()

            if link != last_id:
                requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                              json={"chat_id": CHAT_ID, "text": f"Ігоре, нова квартира! 🏠\n{link}"})
                with open("last_id.txt", "w") as f:
                    f.write(link)
                print("Повідомлення надіслано!")
            else:
                print("Нових хат поки немає.")
    except Exception as e:
        print(f"Помилка: {e}")

if __name__ == "__main__":
    check()
