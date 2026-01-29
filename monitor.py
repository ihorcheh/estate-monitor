import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Тестове посилання (Оренда Київ, нові оголошення кожну хвилину)
URL = "https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/kiev/?sort=created_at%3Adesc"

def check():
    if not TOKEN or not CHAT_ID: return
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"}
    
    try:
        res = requests.get(URL, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Шукаємо перше-ліпше посилання на оголошення
        offer = soup.find('a', href=True)
        all_links = soup.find_all('a', href=True)
        link = ""
        for a in all_links:
            if "/d/uk/obyavlenie/" in a['href']:
                link = "https://www.olx.ua" + a['href'].split('#')[0]
                break

        if link:
            # Бот надішле це повідомлення в будь-якому випадку для перевірки
            msg = f"🔔 ТЕСТ: Бот бачить OLX!\nОсь свіже оголошення:\n{link}"
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          json={"chat_id": CHAT_ID, "text": msg})
            print("Тестове повідомлення відправлено!")
    except Exception as e:
        print(f"Помилка: {e}")

if __name__ == "__main__":
    check()
