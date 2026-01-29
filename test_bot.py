import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Посилання на OLX (Оренда Київ) - тут оновлення кожні 1-2 хвилини
URL = "https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/kiev/?sort=created_at%3Adesc"

def test_check():
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"}
    try:
        print("Запуск тест-перевірки OLX...")
        res = requests.get(URL, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Шукаємо перше оголошення на OLX
        offer = soup.find('a', href=True)
        # Знаходимо перше посилання, яке веде на оголошення (зазвичай містить /d/uk/obyavlenie/)
        all_links = soup.find_all('a', href=True)
        link = ""
        for a in all_links:
            if "/d/uk/obyavlenie/" in a['href']:
                link = "https://www.olx.ua" + a['href'].split('#')[0]
                break

        if link:
            msg = f"⚡️ ТЕСТ ПРАЦЮЄ!\nОсь найсвіжіше оголошення з OLX:\n{link}"
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                          json={"chat_id": CHAT_ID, "text": msg})
            print(f"Повідомлення надіслано: {link}")
        else:
            print("Не вдалося знайти посилання на OLX")
            
    except Exception as e:
        print(f"Помилка тесту: {e}")

if __name__ == "__main__":
    test_check()
