import requests
import time
import os
import threading
import random
from datetime import datetime
from colorama import init, Fore, Style
import websocket

init(autoreset=True)

def print_banner():
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════════════╗
║          BlockMesh Network AutoBot           ║
║     Github: https://github.com/mehdreaming   ║
║      Welcome and do with your own risk!      ║
╚══════════════════════════════════════════════╝
"""
    print(banner)

proxy_tokens = {}

def generate_download_speed():
    return round(random.uniform(0.0, 10.0), 16)

def generate_upload_speed():
    return round(random.uniform(0.0, 5.0), 16)

def generate_latency():
    return round(random.uniform(20.0, 300.0), 16)

def generate_response_time():
    return round(random.uniform(200.0, 600.0), 1)

def get_ip_info(ip_address):
    try:
        response = requests.get(f"https://ipwhois.app/json/{ip_address}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as err:
        print(f"{Fore.RED}Failed to get IP info: {err}")
        return None

def connect_websocket(email, api_token):
    try:
        ws = websocket.create_connection(
            f"wss://ws.blockmesh.xyz/ws?email={email}&api_token={api_token}",
            timeout=10
        )
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.GREEN} Connected to WebSocket")
        ws.close()
    except Exception as e:
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.YELLOW} WebSocket connection failed: {e}")

def submit_bandwidth(email, api_token, ip_info, proxy_config):
    if not ip_info:
        return
    
    payload = {
        "email": email,
        "api_token": api_token,
        "download_speed": generate_download_speed(),
        "upload_speed": generate_upload_speed(),
        "latency": generate_latency(),
        "city": ip_info.get("city", "Unknown"),
        "country": ip_info.get("country_code", "XX"),
        "ip": ip_info.get("ip", ""),
        "asn": ip_info.get("asn", "AS0").replace("AS", ""),
        "colo": "Unknown"
    }
    
    try:
        response = requests.post(
            "https://app.blockmesh.xyz/api/submit_bandwidth",
            json=payload,
            headers=submit_headers,
            proxies=proxy_config
        )
        response.raise_for_status()
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.GREEN} Bandwidth submitted for {ip_info.get('ip')}")
    except requests.RequestException as err:
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.RED} Failed to submit bandwidth: {err}")

# Additional functions remain the same...

def process_proxy(proxy):
    first_run = True
    while True:
        try:
            if first_run or proxy not in proxy_tokens:
                api_token, ip_address = authenticate(proxy)
                first_run = False
            else:
                api_token = proxy_tokens[proxy]
                proxy_config, ip_address = format_proxy(proxy)
            
            if api_token:
                proxy_config, _ = format_proxy(proxy)
                ip_info = get_ip_info(ip_address)
                connect_websocket(email_input, api_token)
                submit_bandwidth(email_input, api_token, ip_info, proxy_config)
                time.sleep(random.randint(60, 120))
        except Exception as e:
            print(f"{Fore.RED}Error in processing proxy {proxy}: {e}")
        time.sleep(10)

def main():
    print(f"\n{Style.BRIGHT}Starting ...")
    threads = []
    for proxy in proxies_list:
        thread = threading.Thread(target=process_proxy, args=(proxy,))
        thread.daemon = True
        threads.append(thread)
        thread.start()
        time.sleep(1)
    
    print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.LIGHTCYAN_EX}[✓] DONE! Delay before next cycle. Not Stuck! Just wait and relax...{Style.RESET_ALL}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Stopping ...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Fore.RED}An error occurred: {str(e)}")
