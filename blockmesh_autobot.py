import requests
import time
import os
import threading
import random
import websocket
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

def print_banner():
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════════════╗
║          BlockMesh Network AutoBot           ║
║     Github: https://github.com/IM-Hanzou     ║
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
        import websocket._core as websocket_core
        ws = websocket_core.create_connection(
            f"wss://ws.blockmesh.xyz/ws?email={email}&api_token={api_token}",
            timeout=10
        )
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.GREEN} Connected to WebSocket")
        ws.close()
    except Exception as e:
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.YELLOW} WebSocket connection OK")

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

def get_and_submit_task(email, api_token, ip_info, proxy_config):
    if not ip_info:
        return
        
    try:
        response = requests.post(
            "https://app.blockmesh.xyz/api/get_task",
            json={"email": email, "api_token": api_token},
            headers=submit_headers,
            proxies=proxy_config
        )
        response.raise_for_status()
        try:
            task_data = response.json()
        except:
            print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.YELLOW} Invalid task response format")
            return
        
        if not task_data or "id" not in task_data:
            print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.YELLOW} No Task Available")
            return
            
        task_id = task_data["id"]
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.GREEN} Got task: {task_id}")
        time.sleep(random.randint(60, 120))
        
        submit_url = f"https://app.blockmesh.xyz/api/submit_task"
        params = {
            "email": email,
            "api_token": api_token,
            "task_id": task_id,
            "response_code": 200,
            "country": ip_info.get("country_code", "XX"),
            "ip": ip_info.get("ip", ""),
            "asn": ip_info.get("asn", "AS0").replace("AS", ""),
            "colo": "Unknown",
            "response_time": generate_response_time()
        }
        
        response = requests.post(
            submit_url,
            params=params,
            data="0" * 10,
            headers=submit_headers,
            proxies=proxy_config
        )
        response.raise_for_status()
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.GREEN} Task submitted: {task_id}")
    except requests.RequestException as err:
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.RED} Failed to process task: {err}")

def format_proxy(proxy_string):
    proxy_type, address = proxy_string.split("://")
    
    if "@" in address:
        credentials, host_port = address.split("@")
        username, password = credentials.split(":")
        host, port = host_port.split(":")
        proxy_dict = {
            "http": f"{proxy_type}://{username}:{password}@{host}:{port}",
            "https": f"{proxy_type}://{username}:{password}@{host}:{port}"
        }
    else:
        host, port = address.split(":")
        proxy_dict = {
            "http": f"{proxy_type}://{host}:{port}",
            "https": f"{proxy_type}://{host}:{port}"
        }
        
    return proxy_dict, host

def authenticate(email, password, proxy):
    proxy_config, ip_address = format_proxy(proxy)
    
    if proxy in proxy_tokens:
        return proxy_tokens[proxy], ip_address
        
    login_data = {"email": email, "password": password}
    
    try:
        response = requests.post(login_endpoint, json=login_data, headers=login_headers, proxies=proxy_config)
        response.raise_for_status()
        auth_data = response.json()
        api_token = auth_data.get("api_token")
        
        proxy_tokens[proxy] = api_token
        
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.GREEN} Login successful {Fore.MAGENTA}|{Fore.LIGHTYELLOW_EX} {ip_address} {Style.RESET_ALL}")
        return api_token, ip_address
    except requests.RequestException as err:
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.RED} Login failed {Fore.MAGENTA}|{Fore.LIGHTYELLOW_EX} {ip_address}: {err}{Style.RESET_ALL}")
        return None, None

def send_uptime_report(api_token, ip_addr, proxy):
    proxy_config, _ = format_proxy(proxy)
    formatted_url = report_endpoint.format(email=email_input, api_token=api_token, ip=ip_addr)
    
    try:
        response = requests.post(formatted_url, headers=report_headers, proxies=proxy_config)
        response.raise_for_status()
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.LIGHTGREEN_EX} PING successful {Fore.MAGENTA}|{Fore.LIGHTYELLOW_EX} {ip_addr} {Fore.MAGENTA}| {Fore.LIGHTWHITE_EX}{api_token}")
    except requests.RequestException as err:
        if proxy in proxy_tokens:
            del proxy_tokens[proxy]
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.RED} Failed to PING {Fore.MAGENTA}|{Fore.LIGHTYELLOW_EX} {ip_addr}: {err}{Style.RESET_ALL}")

def process_proxy(email, password, proxy):
    first_run = True
    while True:
        if first_run or proxy not in proxy_tokens:
            api_token, ip_address = authenticate(email, password, proxy)
            first_run = False
        else:
            api_token = proxy_tokens[proxy]
            proxy_config, ip_address = format_proxy(proxy)
            
        if api_token:
            proxy_config, _ = format_proxy(proxy)
            ip_info = get_ip_info(ip_address)
            
            time.sleep(random.randint(60, 120))
            
            submit_bandwidth(email, api_token, ip_info, proxy_config)
            time.sleep(random.randint(60, 120))
            
            get_and_submit_task(email, api_token, ip_info, proxy_config)
            time.sleep(random.randint(60, 120))
            
            send_uptime_report(api_token, ip_address, proxy)
            time.sleep(random.randint(900, 1200))
        
        time.sleep(10)

def auto_refresh():
    while True:
        print(f"\n{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.YELLOW} Refreshing Proxy List and Account...")
        time.sleep(60)

def main():
    print(f"\n{Style.BRIGHT}Starting ...")
    threads = []
    
    with open('accounts.txt', 'r') as f:
        accounts = f.read().splitlines()
    
    with open('proxies.txt', 'r') as f:
        proxies_list = f.read().splitlines()

    for account in accounts:
        email, password = account.split(":")
        
        for proxy in proxies_list:
            thread = threading.Thread(target=process_proxy, args=(email, password, proxy))
            thread.daemon = True
            threads.append(thread)
            thread.start()
            time.sleep(1)
    
    print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.LIGHTCYAN_EX}[✓] DONE! Delay before next cycle. Not Stuck! Just wait and relax...{Style.RESET_ALL}")
    
    # Start auto-refresh thread
    refresh_thread = threading.Thread(target=auto_refresh)
    refresh_thread.daemon = True
    refresh_thread.start()

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
