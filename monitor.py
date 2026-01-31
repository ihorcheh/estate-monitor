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

# ОНОВЛЕНИЙ СПИСОК САЙТІВ
URLS = [
    "https://www.x-estate.com/offers?city=5c87a27fe758c42fbc38bca3&category=5cf3da6afe460b4aa52ab4b9&sort=date&order=desc&min_price=1000&max_price=15000",
    "https://dom.ria.com/uk/search?category=1&realty_type=2&operation=1&state_id=7&city_ids=7&price_cur=1&sort=created_at",
    "https://an-gorod.com.ua/real/flat/sale?sub_locality_id[]=192&sub_locality_id[]=234&sub_locality_id[]=258&sub_locality_id[]=521&sub_locality_id[]=581&sub_locality_id[]=746&sub_locality_id[]=777&sub_locality_id[]=900&sub_locality_id[]=460&sub_locality_id[]=1047&sub_locality_id[]=1189&sub_locality_id[]=1296&sub_locality_id[]=523&sub_locality_id[]=257&sub_locality_id[]=1553&sub_locality_id[]=1624&sub_locality_id[]=1509&sub_locality_id[]=1641&sub_locality_id[]=442&sub_locality_id[]=1114&sub_locality_id[]=1772&sub_locality_id[]=1583&sub_locality_id[]=1731&sub_locality_id[]=17949&sub_locality_id[]=307&sub_locality_id[]=1674&sub_locality_id[]=505&sub_locality_id[]=2079&sub_locality_id[]=2476&price_from=1000&price_to=16000",
    "https://lun.ua/sale/kharkiv/flats?price_min=100000&price_max=700000&currency=UAH&sort=insert_time",
    "https://rieltor.ua/harkov/flats-sale/?price_min=100000&price_max=650000&sort=bycreated"
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

def is_valid_link(href, domain):
    """Фільтрація посилань, щоб уникнути сміття та інших міст"""
    trash_words = ['uk/help', 'support', 'about', 'contacts', 'news', 'blog', 'user', 'login', 'register', 'favorite']
    if any(word in href.lower() for word in trash_words):
        return False
        
    if 'dom.ria.com' in domain and '/uk/realty-' not in href: return False
    if 'x-estate.com' in domain and '/offers/' not in href: return False
    if 'rieltor.ua' in domain and '/harkov/' not in href: return False
    if 'lun.ua' in domain and '/uk/' not in href: return False
    # Фільтр для нового сайту Город
    if 'an-gorod.com.ua' in domain and '/real/flat/sale/' not in href: return False
    
    return True

def check_sites():
    seen_ids = get_seen_ids()
    new_ids = seen_ids.copy()
    count = 0
    scraper = cloudscraper.create_scraper()

    for url in URLS:
        try:
            domain = url.split('/')[2].replace('www.', '')
            res = scraper.get(url, timeout=20)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                
                if href.startswith('/'):
                    href = f"https://{domain}{href}"
                
                if domain in href and href not in new_ids:
                    if is_valid_link(href, domain):
                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                      json={"chat_id": CHAT_ID, "text": f"✨ Нова квартира у Харкові!\n{href}"})
                        new_ids.add(href)
                        count += 1
        except Exception as e:
            print(f"Error on {url}: {e}")
            continue

    save_ids(new_ids)
    print(f"Готово. Нових оголошень: {count}")

if __name__ == "__main__":
    check_sites()
