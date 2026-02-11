import requests
import json
import random
import string
import time
from datetime import datetime
import os
import threading
import re
import sys

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    END = '\033[0m'
    BOLD = '\033[1m'


API_URL = "https://api.grustnogram.ru/users"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

class ProxyManager:
 
    def __init__(self):
        self.proxies = []
        self.working_proxies = []
        self.current_index = 0
        self.lock = threading.Lock()
    
    def fetch_free_proxies(self):

        print(f"{Colors.CYAN}[INFO] Загрузка бесплатных прокси. . .{Colors.END}")
        
        proxy_sources = [
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/ya0gz/free-proxies/main/proxies/http.txt",
            "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt"
        ]
        
        all_proxies = []
        
        for source in proxy_sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    content = response.text
                    proxies = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', content)
                    all_proxies.extend(proxies[:100])
                    print(f"  {Colors.GREEN}+{Colors.END} {source.split('/')[-1]}: {len(proxies[:100])} прокси")
            except Exception as e:
                print(f"  {Colors.RED}-{Colors.END} {source.split('/')[-1]}: {str(e)[:30]}...")
        
        all_proxies = list(set(all_proxies))
        random.shuffle(all_proxies)
        self.proxies = all_proxies[:500]
        print(f"{Colors.GREEN}[OK]{Colors.END} Всего загружено: {len(self.proxies)} прокси")
        
        return self.proxies
    
    def test_proxy(self, proxy, timeout=5):

        try:
            proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
            response = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=timeout)
            if response.status_code == 200:
                return True
        except:
            pass
        return False
    
    def check_working_proxies(self, limit=50):

        print(f"{Colors.CYAN}[INFO] Проверка работо-способности прокси ( ищем {limit} рабочих ). . .{Colors.END}")
        print("-" * 50)
        
        working = []
        checked = 0
        
        for i, proxy in enumerate(self.proxies):
            checked += 1
            print(f"  [{checked}/{len(self.proxies)}] Проверка {proxy}...", end="\r")
            
            if self.test_proxy(proxy):
                working.append(proxy)
                print(f"  {Colors.GREEN}✓{Colors.END} {proxy} - Работает ({len(working)}/{limit})" + " " * 30)
                
                if len(working) >= limit:
                    break
            else:
                print(f"  {Colors.RED}✗{Colors.END} {proxy} - НЕ работает" + " " * 30)
            
            if i % 20 == 0:
                time.sleep(0.3)
        
        print("\n" + "-" * 50)
        self.working_proxies = working
        print(f"{Colors.GREEN}[OK]{Colors.END} Найдено рабочих прокси: {len(self.working_proxies)} из {checked} проверенных")
        
        if self.working_proxies:
            print(f"{Colors.GREEN}[OK]{Colors.END} Первые 5 прокси: {', '.join(self.working_proxies[:5])}")
        
        return self.working_proxies
    
    def get_proxy(self):
       
        with self.lock:
            if not self.working_proxies:
                return None
            
            proxy = self.working_proxies[self.current_index % len(self.working_proxies)]
            self.current_index += 1
            
            return {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
    
    def add_custom_proxy(self, proxy):
       
        if proxy not in self.working_proxies:
            self.working_proxies.append(proxy)
            print(f"{Colors.GREEN}[OK]{Colors.END} Добавлен прокси: {proxy}")
    
    def get_stats(self):

        return {
            "total": len(self.proxies),
            "working": len(self.working_proxies),
            "working_list": self.working_proxies[:10]
        }

def get_random_headers():

    return {
        "accept": "application/json",
        "accept-language": random.choice([
            "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "en-US,en;q=0.9,ru;q=0.8",
        ]),
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://grustnogram.ru",
        "referer": "https://grustnogram.ru/",
        "user-agent": random.choice(USER_AGENTS),
        "sec-ch-ua": f'"Not(A:Brand";v="8", "Chromium";v="{random.randint(120, 122)}", "Google Chrome";v="{random.randint(120, 122)}"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": random.choice(['"Windows"', '"macOS"', '"Linux"']),
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
    }

def generate_nickname():
  
    adjectives = ["cool", "super", "mega", "ultra", "pro", "best", "top", "real", "nice", "good", 
                 "happy", "sun", "moon", "star", "sky", "dark", "light", "red", "blue", "gold", 
                 "silver", "fast", "slow", "big", "small", "hot", "cold", "new", "old", "young"]
    nouns = ["user", "man", "boy", "girl", "cat", "dog", "wolf", "bear", "fox", "king", "queen", 
            "star", "light", "shadow", "storm", "wind", "fire", "water", "tree", "flower", 
            "bird", "fish", "lion", "tiger", "eagle", "hawk", "dragon", "phoenix"]
    
    adj = random.choice(adjectives)
    noun = random.choice(nouns)
    num = random.randint(1, 9999)
    
    return f"{adj}{noun}{num}"[:15]

def generate_email():

    domains = ["gmail.com", "yandex.ru", "mail.ru", "yahoo.com", "outlook.com", "bk.ru", "list.ru"]
    name = generate_nickname()
    domain = random.choice(domains)
    return f"{name}@{domain}"

def generate_password():

    length = random.randint(12, 16)
    chars = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choice(chars) for i in range(length))

def save_to_txt(account_data, filename="grustnogram_accounts.txt"):

    try:
        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as f:
                f.write("НИКНЕЙМ | EMAIL | ПАРОЛЬ | ID | TOKEN | ДАТА | ПРОКСИ\n")
                f.write("-" * 120 + "\n")
        
        with open(filename, "a", encoding="utf-8") as f:
            line = (f"{account_data['nickname']} | "
                   f"{account_data['email']} | "
                   f"{account_data['password']} | "
                   f"{account_data.get('user_id', 'N/A')} | "
                   f"{account_data.get('access_token', 'N/A')} | "
                   f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
                   f"{account_data.get('proxy', 'N/A')}\n")
            f.write(line)
        return True
    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.END} Ошибка сохранения: {e}")
        return False

def register_account_with_proxy(proxy_manager, max_retries=2):

    
    nickname = generate_nickname()
    email = generate_email()
    password = generate_password()
    
    payload = {
        "nickname": nickname,
        "email": email,
        "password": password,
        "password_confirm": password
    }
    
    headers = get_random_headers()
    
    for attempt in range(max_retries):
        proxy = proxy_manager.get_proxy()
        if not proxy:
            print(f"{Colors.RED}[ERROR]{Colors.END} Нет рабочих прокси!")
            return None
        
        proxy_str = proxy['http'].replace('http://', '')
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Попытка {attempt+1}/{max_retries}")
        print(f"  {Colors.BLUE}Никнейм:{Colors.END} {nickname}")
        print(f"  {Colors.BLUE}Email:{Colors.END} {email}")
        print(f"  {Colors.BLUE}Прокси:{Colors.END} {proxy_str}")
        
        try:
            response = requests.post(
                API_URL,
                headers=headers,
                data=payload,
                proxies=proxy,
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("err") == [0]:
                    user_data = {
                        "success": True,
                        "nickname": nickname,
                        "email": email,
                        "password": password,
                        "user_id": result["data"]["id_user"],
                        "access_token": result["data"]["access_token"],
                        "p_token": result["data"]["p_token"],
                        "proxy": proxy_str,
                    }
                    
                    print(f"  {Colors.GREEN}[УСПЕХ]{Colors.END} ID: {user_data['user_id']}")
                    save_to_txt(user_data)
                    return user_data
                    
                elif result.get("err") == [998]:
                    print(f"  {Colors.RED}[БАН]{Colors.END} Прокси забанен: {proxy_str}")
                    if proxy_str in proxy_manager.working_proxies:
                        proxy_manager.working_proxies.remove(proxy_str)
                
                else:
                    print(f"  {Colors.RED}[ОШИБКА]{Colors.END} {result.get('err_msg')}")
                    time.sleep(1)
                    
            else:
                print(f"  {Colors.RED}[HTTP]{Colors.END} {response.status_code}")
                
        except Exception as e:
            print(f"  {Colors.RED}[СОЕДИНЕНИЕ]{Colors.END} {str(e)[:30]}...")
            if proxy_str in proxy_manager.working_proxies:
                proxy_manager.working_proxies.remove(proxy_str)
    
    return None

def show_account_stats():

    filename = "grustnogram_accounts.txt"
    
    if not os.path.exists(filename):
        print(f"\n{Colors.YELLOW}[WARN]{Colors.END} Файл с аккаунтами не найден")
        return
    
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    account_lines = [line for line in lines if "|" in line and not line.startswith("НИКНЕЙМ") and not line.startswith("-")]
    
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}СТАТИСТИКА АККАУНТОВ{Colors.END}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.BLUE}Файл:{Colors.END} {filename}")
    print(f"{Colors.BLUE}Всего аккаунтов:{Colors.END} {len(account_lines)}")
    
    if account_lines:
        # Аккаунты по дням
        dates = {}
        for line in account_lines[-50:]:
            parts = line.split("|")
            if len(parts) >= 6:
                date = parts[5].strip().split()[0] if len(parts[5].strip().split()) > 0 else "unknown"
                dates[date] = dates.get(date, 0) + 1
        
        if dates:
            print(f"\n{Colors.BLUE}Аккаунты по дням:{Colors.END}")
            for date, count in sorted(dates.items(), reverse=True)[:5]:
                print(f"  • {date}: {count} аккаунтов")
        
        print(f"\n{Colors.BLUE}Последние 5 аккаунтов:{Colors.END}")
        for line in account_lines[-5:]:
            parts = line.split("|")
            nickname = parts[0].strip()
            email = parts[1].strip()
            date = parts[5].strip() if len(parts) > 5 else "N/A"
            print(f"  • {nickname} | {email} | {date}")
    
    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}")

def start_registration():

    

    print(f"{Colors.CYAN}{Colors.BOLD}(-) Grustnogram Auto-Registrator (-){Colors.END}")

    
    print(f"\n{Colors.BLUE}Выберите режим работы:{Colors.END}")
    print(f"  [1] - Поиск бесплатных прокси")
    print(f"  [2] - Использовать свои прокси из файла proxies.txt")
    print(f"  [3] - Статистика работы")
    print(f"  [0] - Выход")
    
    choice = input(f"\n{Colors.YELLOW}Ваш выбор (0-3):{Colors.END} ").strip()
    
    if choice == "0":
        print(f"{Colors.BLUE}[INFO]{Colors.END} Выход...")
        return
    
    elif choice == "1":

        print(f"\n{Colors.BLUE}[INFO]{Colors.END} Режим: поиск бесплатных прокси")
        print("-" * 40)
        
        while True:
            try:
                proxy_count = input(f"{Colors.YELLOW}Сколько рабочих прокси найти? (по умолч. 30):{Colors.END} ").strip()
                proxy_count = int(proxy_count) if proxy_count else 30
                if proxy_count > 0:
                    break
                else:
                    print(f"{Colors.RED}[ERROR]{Colors.END} Введите положительное число")
            except ValueError:
                print(f"{Colors.RED}[ERROR]{Colors.END} Введите число")
        
        while True:
            try:
                account_count = input(f"{Colors.YELLOW}Сколько аккаунтов зарегистрировать? (по умолч. 5):{Colors.END} ").strip()
                account_count = int(account_count) if account_count else 5
                if account_count > 0:
                    break
                else:
                    print(f"{Colors.RED}[ERROR]{Colors.END} Введите положительное число")
            except ValueError:
                print(f"{Colors.RED}[ERROR]{Colors.END} Введите число")
        
        start_proxy_registration(proxy_count, account_count)
    
    elif choice == "2":

        print(f"\n{Colors.BLUE}[INFO]{Colors.END} Режим: свои прокси из файла")
        print("-" * 40)
        
        while True:
            try:
                account_count = input(f"{Colors.YELLOW}Сколько аккаунтов зарегистрировать? (по умолч. 5):{Colors.END} ").strip()
                account_count = int(account_count) if account_count else 5
                if account_count > 0:
                    break
                else:
                    print(f"{Colors.RED}[ERROR]{Colors.END} Введите положительное число")
            except ValueError:
                print(f"{Colors.RED}[ERROR]{Colors.END} Введите число")
        
        start_custom_proxy_registration(account_count)
    
    elif choice == "3":

        show_account_stats()
    
    else:
        print(f"{Colors.RED}[ERROR]{Colors.END} Неверный выбор")

def start_proxy_registration(proxy_search_count, account_count):

    
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.CYAN}[РЕГИСТРАЦИЯ С ПРОКСИ]{Colors.END}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}")
    
    proxy_manager = ProxyManager()
    
    print(f"\n{Colors.BLUE}[1/3]{Colors.END} Поиск бесплатных прокси. . .")
    proxy_manager.fetch_free_proxies()
    
    if len(proxy_manager.proxies) > 0:
        print(f"\n{Colors.BLUE}[2/3]{Colors.END} Проверка работоспособности. . .")
        proxy_manager.check_working_proxies(limit=proxy_search_count)
    
    if len(proxy_manager.working_proxies) == 0:
        print(f"\n{Colors.RED}[ERROR]{Colors.END} Нет рабочих прокси!")
        print(f"\n{Colors.YELLOW}Возможные решения:{Colors.END}")
        print(f"  1. Купить качественные прокси")
        print(f"  2. Добавить свои прокси в файл proxies.txt")
        print(f"  3. Увеличить кол-во проверяемых прокси (так-же вы можете пополнить источники бесплатных прокси)")
        
        if not os.path.exists("proxies.txt"):
            with open("proxies.txt", "w") as f:
                f.write("# Список прокси для Grustnogram\n")
                f.write("# Формат: ip:port\n")
                f.write("# Формат с авторизацией: user:pass@ip:port\n\n")
                f.write("# Примеры:\n")
                f.write("1.2.3.4:8080\n")
                f.write("user:pass@5.6.7.8:3128\n")
        
        return
    
    print(f"\n{Colors.BLUE}[3/3]{Colors.END} Начало регистрации...")
    print(f"{Colors.GREEN}[OK]{Colors.END} Доступно прокси: {len(proxy_manager.working_proxies)}")
    print(f"{Colors.GREEN}[OK]{Colors.END} План: {account_count} аккаунтов")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}")
    
    successful = 0
    failed = 0
    accounts = []
    
    for i in range(account_count):
        print(f"\n{Colors.BOLD}Аккаунт {i+1}/{account_count}{Colors.END}")
        print("-" * 50)
        
        result = register_account_with_proxy(proxy_manager)
        
        if result:
            successful += 1
            accounts.append(result)
            
            if successful % 3 == 0:
                print(f"\n{Colors.BLUE}[СОХРАНЕНИЕ]{Colors.END} Успешно: {successful}, Неудачно: {failed}")
            
            if i < account_count - 1:
                delay = random.uniform(2, 4)
                print(f"\n{Colors.BLUE}[ПАУЗА]{Colors.END} {delay:.1f} сек...")
                time.sleep(delay)
        else:
            failed += 1
            
            if len(proxy_manager.working_proxies) == 0:
                print(f"\n{Colors.RED}[ERROR]{Colors.END} Закончились рабочие прокси!")
                
                if len(proxy_manager.proxies) > 0:
                    print(f"{Colors.YELLOW}[ПОИСК]{Colors.END} Пытаемся найти еще прокси...")
                    proxy_manager.check_working_proxies(limit=proxy_search_count)
                    
                    if len(proxy_manager.working_proxies) == 0:
                        break
                else:
                    break
        
        if (i + 1) % 5 == 0:
            print(f"\n{Colors.BLUE}[ПРОГРЕСС]{Colors.END} {successful}/{i+1} успешных")
    
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}ИТОГОВАЯ СТАТИСТИКА{Colors.END}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.GREEN}Успешно зарегистрировано:{Colors.END} {successful}")
    print(f"{Colors.RED}Неудачных попыток:{Colors.END} {failed}")
    print(f"{Colors.BLUE}Аккаунты сохранены в:{Colors.END} grustnogram_accounts.txt")
    
    if accounts:
        print(f"\n{Colors.GREEN}Последний успешный аккаунт:{Colors.END}")
        last = accounts[-1]
        print(f"  Никнейм: {last['nickname']}")
        print(f"  Email: {last['email']}")
        print(f"  ID: {last['user_id']}")
        print(f"  Прокси: {last['proxy']}")
    
    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}")

def start_custom_proxy_registration(account_count):

    
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.CYAN}[РЕГИСТРАЦИЯ С ПРОКСИ ИЗ ФАЙЛА]{Colors.END}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}")
    
    proxy_manager = ProxyManager()
    
    if not os.path.exists("proxies.txt"):
        print(f"{Colors.RED}[ERROR]{Colors.END} Файл proxies.txt не найден!")
        
        with open("proxies.txt", "w") as f:
            f.write("# Список прокси для Grustnogram\n")
            f.write("# Формат: ip:port\n")
            f.write("# Формат с авторизацией: user:pass@ip:port\n\n")
            f.write("# Примеры:\n")
            f.write("1.2.3.4:8080\n")
            f.write("user123:pass456@5.6.7.8:3128\n")
        
        print(f"{Colors.GREEN}[OK]{Colors.END} Создан файл proxies.txt с примером")
        print(f"{Colors.YELLOW}[INFO]{Colors.END} Добавьте свои прокси в файл и запустите снова")
        return
    
    print(f"{Colors.BLUE}[INFO]{Colors.END} Загрузка прокси из proxies.txt...")
    
    with open("proxies.txt", "r") as f:
        custom_proxies = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        if not custom_proxies:
            print(f"{Colors.RED}[ERROR]{Colors.END} Файл proxies.txt пуст!")
            return
        
        for proxy in custom_proxies:
            proxy_manager.add_custom_proxy(proxy)
    
    print(f"{Colors.GREEN}[OK]{Colors.END} Загружено {len(custom_proxies)} прокси")
    
    if len(proxy_manager.working_proxies) == 0:
        print(f"{Colors.RED}[ERROR]{Colors.END} Нет рабочих прокси!")
        return
    
    print(f"\n{Colors.BLUE}[СТАРТ]{Colors.END} Начало регистрации...")
    print(f"{Colors.GREEN}[OK]{Colors.END} Доступно прокси: {len(proxy_manager.working_proxies)}")
    print(f"{Colors.GREEN}[OK]{Colors.END} План: {account_count} аккаунтов")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}")
    
    successful = 0
    failed = 0
    accounts = []
    
    for i in range(account_count):
        print(f"\n{Colors.BOLD}Аккаунт {i+1}/{account_count}{Colors.END}")
        print("-" * 50)
        
        result = register_account_with_proxy(proxy_manager)
        
        if result:
            successful += 1
            accounts.append(result)
            
            if i < account_count - 1:
                delay = random.uniform(2, 4)
                print(f"\n{Colors.BLUE}[ПАУЗА]{Colors.END} {delay:.1f} сек...")
                time.sleep(delay)
        else:
            failed += 1
            
            if len(proxy_manager.working_proxies) == 0:
                print(f"\n{Colors.RED}[ERROR]{Colors.END} Закончились рабочие прокси!")
                break
        
        if (i + 1) % 5 == 0:
            print(f"\n{Colors.BLUE}[ПРОГРЕСС]{Colors.END} {successful}/{i+1} успешных")
    
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}ИТОГОВАЯ СТАТИСТИКА{Colors.END}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.GREEN}Успешно зарегистрировано:{Colors.END} {successful}")
    print(f"{Colors.RED}Неудачных попыток:{Colors.END} {failed}")
    print(f"{Colors.BLUE}Аккаунты сохранены в:{Colors.END} grustnogram_accounts.txt")
    
    if accounts:
        print(f"\n{Colors.GREEN}Последний успешный аккаунт:{Colors.END}")
        last = accounts[-1]
        print(f"  Никнейм: {last['nickname']}")
        print(f"  Email: {last['email']}")
        print(f"  ID: {last['user_id']}")
        print(f"  Прокси: {last['proxy']}")
    
    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}")

if __name__ == "__main__":
    try:
        start_registration()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[INFO]{Colors.END} Прервано пользователем")
    except Exception as e:
        print(f"\n{Colors.RED}[ERROR]{Colors.END} {e}")
    
    input(f"\n{Colors.BLUE}[INFO]{Colors.END} Нажмите Enter для выхода...")