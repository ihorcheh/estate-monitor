import requests
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def check():
    print(f"Спроба відправити повідомлення...")
    print(f"Chat ID: {CHAT_ID}") # Перевіримо, чи бачить скрипт ваш ID
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": "🚀 Ігоре, якщо ти це бачиш — зв'язок налагоджено!"}
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("✅ Успіх! Повідомлення має бути в Telegram.")
    else:
        print(f"❌ Помилка Telegram API: {response.status_code}")
        print(f"Деталі: {response.text}")

if __name__ == "__main__":
    check()
