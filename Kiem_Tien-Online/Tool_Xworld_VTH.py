import os
import sys
import time
import json
import re
import math
import base64
import random
import string
import hashlib
import socket
import subprocess
import uuid
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from datetime import datetime, timedelta
from random import randint
from sys import platform
import urllib3
import http.client
import urllib.parse
import ssl
from atexit import register
try:
    import threading
    import requests
    import httpx
    import cloudscraper
    from collections import defaultdict
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import box
    from colorama import Fore, init
    from pystyle import Add, Center, Anime, Colors, Colorate, Write, System
    from bs4 import BeautifulSoup
except ModuleNotFoundError as e:
    lib = e.name
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', lib])
        os.execl(sys.executable, sys.executable, *sys.argv)
    except subprocess.CalledProcessError:
        sys.exit(1)

API_URL = "http://webtooltvh.x10.mx/Total_Users/total_user.php"
UPGRADE_URL = "https://raw.githubusercontent.com/HoangHayHack/tvhtool/main/update.json"
STATUS_URL = "https://raw.githubusercontent.com/HoangHayHack/tvhtool/main/status.json"
API_KEY = "Api_Key_TranVanHoang-TVH"
VERSION_TOOL = "1.0"

start_time = time.time()
  
now = datetime.now()
date = now.strftime("Ngày \033[1;31m: \033[1;36m%d/%m/%Y")
thoigian = now.strftime("Giờ \033[1;31m: \033[1;36m%H:%M:%S")

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip_lan = s.getsockname()[0]
s.close()

try:
    ip_public = requests.get("https://api.ipify.org", timeout=5).text
    location_data = requests.get(f"https://ipinfo.io/{ip_public}/json", timeout=5).json()
    city = location_data.get("city", "Không Xác Định")
    country = location_data.get("country", "Không Xác Định")
except Exception:
    ip_public = "N/A"
    city = "Không Xác Định"
    country = "Không Xác Định"
    
def kiem_tra_mang():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
    except OSError:
        print("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mMạng Không Ổn Định Hoặc Bị Mất Kết Nối, Vui Lòng Kiểm Tra Lại Mạng !")

kiem_tra_mang()
scraper = cloudscraper.create_scraper()
kiem_tra_mang()

def hide_url(link: str) -> str:
    return base64.b64encode(link.encode()).decode()

def reveal_url(encoded: str) -> str:
    return base64.b64decode(encoded.encode()).decode()

def load_data():
    if not os.path.exists("device_info.txt"):
        device_id = f"TVH_{uuid.uuid4().hex[:6].upper()}"
        data = {"device_id": device_id, "count": 0, "last_run": "Chưa Từng Chạy"}
        save_data(data)
        return data

    with open("device_info.txt", "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
        if len(lines) < 3:
            device_id = f"TVH_{uuid.uuid4().hex[:6].upper()}"
            return {"device_id": device_id, "count": 0, "last_run": "Chưa Từng Chạy"}
        return {"device_id": lines[0], "count": int(lines[1]), "last_run": lines[2]}

def save_data(data):
    with open("device_info.txt", "w", encoding="utf-8") as f:
        f.write(f"{data['device_id']}\n{data['count']}\n{data['last_run']}")

def detect_vpn(ip_public):
    try:
        url = f"https://ipapi.co/{ip_public}/json/"
        r = requests.get(url, timeout=6).json()

        is_vpn = r.get("is_vpn", False)
        is_proxy = r.get("proxy", False)
        is_hosting = r.get("hosting", False)

        if is_vpn or is_proxy or is_hosting:
            return True
        return False
    except:
        return False

if detect_vpn(ip_public):
    print("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mPhát Hiện Đang Dùng VPN, Proxy Hoặc Hosting, Vui Lòng Tắt Để Tiếp Tục !")
    sys.exit()
    
def detect_system_proxy():
    proxy_vars = ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]
    for p in proxy_vars:
        if os.environ.get(p):
            return True
    return False

if detect_system_proxy():
    print("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mPhát Hiện Proxy , Vui Lòng Tắt Proxy Để Tiếp Tục !")
    sys.exit()

def kiem_tra_cap_nhat():
    try:
        res = requests.get(UPGRADE_URL, timeout=5).json()
        phien_ban_moi = res.get("version")
        link_download = res.get("download")

        if phien_ban_moi and phien_ban_moi != VERSION_TOOL:
            print(f"\n\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mCó Bản Cập Nhật Mới \033[1;32m: \033[1;36m{phien_ban_moi}")
            print(f"\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mTải Ngay Tại \033[1;31m: \033[1;36m{link_download}")
            sys.exit()
    except Exception as e:
        print(f"\n\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mKhông Thể Kiểm Tra Cập Nhật \033[1;32m: \033[1;36m{e}")

def kiem_tra_bao_tri():
    try:
        enc_url = hide_url(STATUS_URL)
        url = reveal_url(enc_url)
        with httpx.Client(timeout=5) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()
        status = data.get("Status", False)

        if status:
           print(f"\r\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mTool Đang Trong Thời Gian Bảo Trì, Vui Lòng Thử Lại Sau !")
           sys.exit(1)
           
    except Exception:
        print("\r\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mKhông Thể Kiểm Tra Trạng Thái Bảo Trì !")
        sys.exit(1)
        
def anti_debug():
    if "pydevd" in sys.modules or "trace" in sys.argv:
        print("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mPhát Hiện Debugger, Thoát !")
        sys.exit(1)

def anti_crack_pycdc():
    if sys.argv[0].lower().endswith(".pyc"):
        print("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mKhông Hỗ Trợ Chạy File Pyc, Thoát !")
        sleep(1)
        os._exit(137)

def detect_debug_tools():
    suspicious_keywords = ["charles", "fiddler", "httptoolkit", "mitmproxy", "canary", "proxyman", "wireshark"]
    suspicious_ports = ["127.0.0.1:8000", "127.0.0.1:8080", "127.0.0.1:8888", "127.0.0.1:9090"]
    ssl_cert_vars = ["SSL_CERT_FILE", "NODE_EXTRA_CA_CERTS", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE", "PATH"]
    proxy_env_vars = ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]

    if os.environ.get("HTTP_TOOLKIT_ACTIVE", "").lower() == "true":
        return True

    for var in ssl_cert_vars + proxy_env_vars:
        val = os.environ.get(var, "").lower()
        if any(kw in val for kw in suspicious_keywords):
            return True
        if any(port in val for port in suspicious_ports):
            return True

    if os.environ.get("FIREFOX_PROXY", "") in suspicious_ports:
        return True

    try:
        result = subprocess.check_output(["ps", "-aux"], universal_newlines=True)
        for line in result.lower().splitlines():
            if any(kw in line for kw in suspicious_keywords):
                return True
    except Exception:
        pass

    return False

if detect_debug_tools():
    print("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mPhát Hiện Bug, Vui Lòng Tắt Sniff Hoặc In Debug Để Tiếp Tục Chạy !")
    try:
        os.remove(sys.argv[0])
    except:
        pass
    raise SystemExit("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mPhát Hiện Bug, Thoát !")

os.system("cls" if os.name == "nt" else "clear")

def check_internet_connection() -> bool:
    try:
        enc_url = hide_url('https://www.google.com')
        url = reveal_url(enc_url)
        with httpx.Client(timeout=10) as client:
            r = client.get(url)
            return r.status_code == 200
    except Exception:
        return False

if not check_internet_connection():
    print("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mKhông Có Kết Nối Mạng, Thoát Tool !")
    sys.exit()

kiem_tra_cap_nhat()
kiem_tra_bao_tri()
anti_debug()
anti_crack_pycdc()
detect_debug_tools()
     
def banner():
    data = load_data()
    try:
        res = requests.get(API_URL, params={"api_key": API_KEY}, timeout=5)
        api_data = res.json()
        total_users = api_data.get("total_users", 0)
    except:
        total_users = 0
        
    data["count"] += 1
    data["last_run"] = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
    save_data(data)
    banner = f"""\033[1;32m████████╗██╗   ██╗██╗  ██╗████████╗ ██████╗  ██████╗ ██╗     
\033[1;97m╚══██╔══╝██║   ██║██║  ██║╚══██╔══╝██╔═══██╗██╔═══██╗██║     
\033[1;32m   ██║   ██║   ██║███████║   ██║   ██║   ██║██║   ██║██║     
\033[1;97m   ██║   ╚██╗ ██╔╝██╔══██║   ██║   ██║   ██║██║   ██║██║     
\033[1;32m   ██║    ╚████╔╝ ██║  ██║   ██║   ╚██████╔╝╚██████╔╝███████╗
\033[1;97m   ╚═╝     ╚═══╝  ╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝

\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mAdmin Tool \033[1;31m: \033[1;36mTrần Văn Hoàng
\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mVersion \033[1;31m: \033[1;36m1.0
\033[1;32m[\033[1;31m×\033[1;32m]\033[1;33m ➩ \033[1;32mYoutuber \033[1;31m: \033[1;36mTrần Văn Hoàng
\033[1;32m[\033[1;31m÷\033[1;32m]\033[1;33m ➩ \033[1;32mZalo \033[1;31m: \033[1;36m0347896645
\033[1;32m[\033[1;31m♧\033[1;32m]\033[1;33m ➩ \033[1;32mTikTok \033[1;31m: \033[1;36m@tranvanhoang324
\033[1;32m[\033[1;31m♡\033[1;32m]\033[1;33m ➩ \033[1;32mFacebook \033[1;31m: \033[1;36mTrần Văn Hoàng
\033[1;32m[\033[1;31m*\033[1;32m]\033[1;33m ➩ \033[1;32mBạn Đang Sử Dụng \033[1;31m: \033[1;36mTool Xworld Vua Thoát Hiểm
\033[1;32m[\033[1;31m◇\033[1;32m]\033[1;33m ➩ \033[1;32mThông Báo \033[1;31m: \033[1;36mMua Full Source Tool Inbox Zalo Trên !
\033[1;97m════════════════════════════════════════════════
\033[1;32m[\033[1;31m~\033[1;32m]\033[1;33m ➩ \033[1;32mBox Share Tool \033[1;31m: \033[1;36mhttps://zalo.me/g/loyedh038
\033[1;32m[\033[1;31m~\033[1;32m]\033[1;33m ➩ \033[1;32mBox Giao Lưu \033[1;31m: \033[1;36mhttps://zalo.me/g/lzousq414
\033[1;97m════════════════════════════════════════════════
\033[1;32m[\033[1;31m•\033[1;32m]\033[1;33m ➩ \033[1;32mIp Address \033[1;31m: \033[1;36m{ip_lan}
\033[1;32m[\033[1;31m•\033[1;32m]\033[1;33m ➩ \033[1;32mDevice Id \033[1;31m: \033[1;36m{data['device_id']}
\033[1;32m[\033[1;31m•\033[1;32m]\033[1;33m ➩ \033[1;32mSố Lần Đã Chạy \033[1;31m: \033[1;36m{data['count']} Lần
\033[1;32m[\033[1;31m•\033[1;32m]\033[1;33m ➩ \033[1;32mSố Người Đã Dùng \033[1;31m: \033[1;36m{total_users} Người
\033[1;32m[\033[1;31m•\033[1;32m]\033[1;33m ➩ \033[1;32mLần Chạy Gần Nhất \033[1;31m: \033[1;36m{data['last_run']}
\033[1;32m[\033[1;31m•\033[1;32m]\033[1;33m ➩ \033[1;32mVị Trí \033[1;31m: \033[1;36m{city}, {country}
\033[1;32m[\033[1;31m•\033[1;32m]\033[1;33m ➩ \033[1;32m{thoigian}
\033[1;32m[\033[1;31m•\033[1;32m]\033[1;33m ➩ \033[1;32m{date}
\033[1;97m════════════════════════════════════════════════
\033[1;32m[\033[1;31m☆\033[1;32m]\033[1;33m ➩ \033[1;32mAgribank \033[1;31m: \033[1;36m3611205248044
\033[1;32m[\033[1;33m> \033[1;34mXin Chân Thành Cảm Ơn Nếu Bạn Đã Donate \033[1;33m<\033[1;32m]
\033[1;97m════════════════════════════════════════════════"""
    for X in banner:
        sys.stdout.write(X)
        sys.stdout.flush()
        sleep(0.0001)
    print("")
    
os.system("cls" if os.name == "nt" else "clear")
banner()

def parse_escapemaster_url(url):
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        user_id = query_params.get('userId', [None])[0]
        secret_key = query_params.get('secretKey', [None])[0]
        
        if user_id and secret_key:
            return user_id, secret_key
        else:
            return None, None
    except Exception as e:
        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi Khi Parse Link : {e}"))
        return None, None

current_time = int(time.time() * 1000)

def nhap_du_lieu():
    file_name = "Acc_Xworld.json"

    if os.path.exists(file_name):
        try:
            with open(file_name, "r") as f:
                data = json.load(f)
            user_id = data.get("user_id", "")
            user_login = data.get("user_login", "login_v2")
            user_secret_key = data.get("user_secret_key", "")
        except (json.JSONDecodeError, ValueError):
            print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ File Bị Lỗi Hoặc Trống, Vui Lòng Nhập Lại !"))
            os.remove(file_name)
            return nhap_du_lieu()
    else:
        user_id = input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Nhập Id Xworld : "))
        user_secret_key = input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Nhập Secret Key Xworld : "))
        print("\033[1;97m════════════════════════════════════════════════")

        with open(file_name, "w") as f:
            json.dump({
                "user_id": user_id,
                "user_login": "login_v2",
                "user_secret_key": user_secret_key
            }, f)

    while True:
        try:
            amount = int(input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Nhập Số Build Cược Ban Đầu (Ít Nhất Là 1 Build) : ")))
            if amount < 1:
                raise ValueError
            break
        except ValueError:
            print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Vui Lòng Nhập Số Nguyên Từ 1 Trở Lên Cho Số Build Cược !"))
            time.sleep(1)

    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Nhập Thông Tin Cần Thiết Thành Công !"))
    return user_id, user_secret_key, amount

user_id, user_secret_key, amount = nhap_du_lieu()
user_login = "login_v2"

print("\033[1;97m════════════════════════════════════════════════")
while True:
    stop_loss_input = input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Bật Stop Loss ? (y/n) : ")).strip().lower()
    if stop_loss_input == 'y':
        stop_loss_enabled = True
        break
    elif stop_loss_input == 'n':
        stop_loss_enabled = False
        break
    else:
        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Vui Lòng Nhập (y/n)"))

stop_loss_amount = 0
take_profit_amount = 0

if stop_loss_enabled:
    stop_loss_amount = int(input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Nhập Số Build Để Dừng Khi Lỗ Ví Dụ - (150) : ")))
    take_profit_amount = int(input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Nhập Số Build Để Dừng Khi Lời Ví Dụ - (500) : ")))

print("\033[1;97m════════════════════════════════════════════════")
while True:
    martingale_input = input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Bật Gấp Đôi Tiền Cược Sau Khi Thua ? (y/n) : ")).strip().lower()
    if martingale_input == 'y':
        martingale_enabled = True
        break
    elif martingale_input == 'n':
        martingale_enabled = False
        break
    else:
        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Vui Lòng Nhập (y/n)"))

if martingale_enabled:
    print("\033[1;97m════════════════════════════════════════════════")
    print(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Hệ Số Gấp Cược Mặc Định : (Lần Đầu : x15 | Lần 2 : x20 | Lần 3 : x15)"))
    while True:
        custom_input = input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Tùy Chỉnh Hệ Số Gấp Cược ? (y/n) : ")).strip().lower()
        if custom_input == 'y':
            custom_multiplier = True
            break
        elif custom_input == 'n':
            custom_multiplier = False
            break
        else:
            print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Vui Lòng Nhập (y/n)"))

    multiplier_1 = 15
    multiplier_2 = 20
    multiplier_3 = 15

    if custom_multiplier:
        multiplier_1 = float(input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Nhập Hệ Số Gấp Lần 1 (Mặc Định - 15) : ")) or "15")
        multiplier_2 = float(input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Nhập Hệ Số Gấp Lần 2 (Mặc Định - 20) : ")) or "20")
        multiplier_3 = float(input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Nhập Hệ Số Gấp Lần 3 (Mặc Định - 15) : ")) or "15")
else:
    custom_multiplier = False
    multiplier_1 = 1
    multiplier_2 = 1
    multiplier_3 = 1

print("\033[1;97m════════════════════════════════════════════════")
while True:
    prediction_input = input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Bật Tự Động Phân Tích Và Dự Đoán Kết Quả ? (y/n) : ")).strip().lower()
    if prediction_input == 'y':
        prediction_enabled = True
        break
    elif prediction_input == 'n':
        prediction_enabled = False
        break
    else:
        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Vui Lòng Nhập (y/n)"))

cuoc_ban_dau = amount
so_du_ban_dau = 0
tool_running = True
history_results = []
last_checked_issue = None
so_du_truoc_cuoc = 0

url = f"https://user.3games.io/user/regist?is_cwallet=1&is_mission_setting=true&version=&time={current_time}"
api_10_van = f"https://api.escapemaster.net/escape_game/recent_10_issues?asset=BUILD"
api_100_van = f"https://api.escapemaster.net/escape_game/recent_100_issues?asset=BUILD"
api_cuoc = "https://api.escapemaster.net/escape_game/bet"
api_my_joined = "https://api.escapemaster.net/escape_game/my_joined?asset=BUILD&page=1&page_size=10"

headers = {
    "user-id": user_id,
    "user-login": user_login,
    "user-secret-key": user_secret_key,
    "accept": "*/*",
    "accept-language": "vi,en;q=0.9",
    "country-code": "vn",
    "origin": "https://xworld.info",
    "priority": "u=1, i",
    "referer": "https://xworld.info/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "xb-language": "vi-VN",
    "Content-Type": "application/json"
}

def login():
    global so_du_ban_dau
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                username = data["data"]["username"]
                ctoken_contribute = data["data"]["cwallet"]["ctoken_contribute"]
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Tên : {username}"))
                so_du_ban_dau = ctoken_contribute
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Số Dư : {ctoken_contribute:.2f} Build"))
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Đã Lưu Số Dư {so_du_ban_dau:.2f} Build"))
            else:
                print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Đăng Nhập Không Thành Công !"))
                sys.exit(1)
        else:
            print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi Mạng !"))
    except requests.RequestException as e:
        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi Không Xác Định !"))

def tong_loi_lo():
    global tool_running
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                ctoken_contribute = data["data"]["cwallet"]["ctoken_contribute"]
                loi_lo = ctoken_contribute - so_du_ban_dau
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Số Dư Hiện Tại : {ctoken_contribute:.2f} | Số Dư Ban Đầu : {so_du_ban_dau:.2f} | Chênh Lệch : {loi_lo:.2f}"))
                
                if stop_loss_enabled:
                    if loi_lo <= -stop_loss_amount:
                        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Đã Đạt Stop Loss : {loi_lo:.2f} Build"))
                        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Dừng Tool Tự Động !"))
                        tool_running = False
                        return
                    elif loi_lo >= take_profit_amount:
                        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Đã Đạt Take Profit : {loi_lo:.2f} Build"))
                        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Dừng Tool Tự Động !"))
                        tool_running = False
                        return

                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Số Dư Hiện Tại : {ctoken_contribute:.2f} Build"))
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Số Dư Ban Đầu : {so_du_ban_dau:.2f} Build"))
                
                if loi_lo >= 0:
                    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Tổng Thể : +{loi_lo:.2f} Build (Lời)"))
                else:
                    if abs(loi_lo) <= amount:
                        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Tổng Thể : {loi_lo:.2f} Build (Đã Cân Bằng)"))
                    else:
                        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Tổng Thể : {loi_lo:.2f} Build (Lỗ)"))
        else:
            print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi Mạng !"))
    except requests.RequestException as e:
        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi Không Xác Định : {e}"))

def phan_tich_lich_su():
    global history_results
    try:
        response = requests.get(api_100_van, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                issues = data.get("data", [])
                history_results = []
                
                room_mapping = {
                    8: "Nhà Kho",
                    7: "Phòng Họp", 
                    6: "Phòng Giám Đốc",
                    5: "Phòng Trò Chuyện",
                    4: "Phòng Giám Sát",
                    3: "Văn Phòng",
                    2: "Phòng Tài Vụ",
                    1: "Phòng Nhân Sự"
                }
                
                for issue in issues:
                    try:
                        if isinstance(issue, dict) and "killed_room_id" in issue:
                            room_id = issue["killed_room_id"]
                            room_name = room_mapping.get(room_id, "Không Xác Định")
                            history_results.append(room_name)
                        else:
                            continue
                    except Exception as e:
                        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi Khi Xử Lý Issue : {e}"))
                        continue
                
                if not history_results:
                    return None
                
                room_counts = Counter(history_results)
                total_games = len(history_results)
                
                print("\033[1;97m════════════════════════════════════════════════")
                for room, count in room_counts.most_common():
                    percentage = (count / total_games) * 100
                    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ {room} : {count} Lần ({percentage:.1f}%)"))
                
                least_frequent_room = min(room_counts.items(), key=lambda x: x[1])
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Dự Đoán : {least_frequent_room[0]} Có Thể Xuất Hiện Tiếp Theo (Ít Xuất Hiện Nhất)"))
                
                return least_frequent_room[0]
            else:
                print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi API : {data.get('message', 'Không Xác Định')}"))
        else:
            print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi HTTP : {response.status_code}"))
    except requests.RequestException as e:
        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi Khi Phân Tích Lịch Sử : {e}"))
    except Exception as e:
        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi Không Xác Định : {e}"))
    return None

def kiem_tra_ket_qua_cuoc():
    global last_checked_issue, chuoi_thang, so_du_truoc_cuoc

    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            response = requests.get(api_my_joined, headers=headers, timeout=10)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("code") == 0:
                        items = data.get("data", {}).get("items", [])
                        if items:
                            latest_bet = items[0]
                            issue_id = latest_bet.get("issue_id")
                            bet_amount = latest_bet.get("bet_amount", 0)
                            enter_room_id = latest_bet.get("enter_room_id")
                            enter_room = latest_bet.get("enter_room", "Không Xác Định")
                            killed_room_id = latest_bet.get("killed_room_id")
                            killed_room = latest_bet.get("killed_room", "Không Xác Định")
                            
                            if enter_room_id == killed_room_id:
                                result = "lose"
                            else:
                                result = "win"
                            
                            if issue_id != last_checked_issue:
                                last_checked_issue = issue_id
                                
                                time.sleep(2)
                                
                                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Sát Thủ Vào : {killed_room}"))
                                
                                room_mapping_reverse = {
                                    1: "Nhà Kho",
                                    2: "Phòng Họp", 
                                    3: "Phòng Giám Đốc",
                                    4: "Phòng Trò Chuyện",
                                    5: "Phòng Giám Sát",
                                    6: "Văn Phòng",
                                    7: "Phòng Tài Vụ",
                                    8: "Phòng Nhân Sự"
                                }                               
                                try:
                                    response_bet = requests.get(api_my_joined, headers=headers, timeout=5)
                                    if response_bet.status_code == 200:
                                        bet_data = response_bet.json()
                                        if bet_data.get("code") == 0:
                                            bet_items = bet_data.get("data", {}).get("items", [])
                                            if bet_items:
                                                bet_room_id = bet_items[0].get("enter_room_id")
                                                bet_room_name = room_mapping_reverse.get(bet_room_id, "Không xác định")
                                                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Bạn Đặt Cược Vào : {bet_room_name}"))
                                            else:
                                                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Bạn Vào : {enter_room}"))
                                        else:
                                            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Bạn Vào : {enter_room}"))
                                    else:
                                        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Bạn Vào : {enter_room}"))
                                except:
                                    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Bạn Vào : {enter_room}"))
                                
                                try:
                                    time.sleep(1)
                                    
                                    response_balance = requests.get(url, headers=headers, timeout=5)
                                    if response_balance.status_code == 200:
                                        balance_data = response_balance.json()
                                        if balance_data.get("code") == 200:
                                            so_du_sau_cuoc = balance_data["data"]["cwallet"]["ctoken_contribute"]
                                            ket_qua_van = so_du_sau_cuoc - so_du_truoc_cuoc
                                            
                                            actual_result = result
                                            
                                            if actual_result == "win":
                                                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Ván Này Thắng : +{bet_amount:.2f} Build"))
                                            elif actual_result == "lose":
                                                print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Ván Này Thua : -{bet_amount:.2f} Build"))
                                                
                                except Exception as e:
                                    print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi Khi Tính Toán Số Dư : {e}"))
                                    actual_result = result
                                
                                if actual_result == "win":
                                    chuoi_thang += 1
                                    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Chuỗi Thắng Liên Tiếp Hiện Tại : {chuoi_thang} Ván"))
                                elif actual_result == "lose":
                                    chuoi_thang = 0
                                    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Chuỗi Thắng Liên Tiếp Hiện Tại : {chuoi_thang} Ván"))
                                
                                tong_loi_lo()
                                return True
                            else:
                                if attempt < max_attempts - 1:
                                    time.sleep(1)
                                    continue
                                else:
                                    print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Chưa Có Kết Quả Mới, Đợi Vòng Tiếp Theo..."))
                                    return False
                        else:
                            if attempt == 0:
                                print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Chưa Có Dữ Liệu Cược, Đang Chờ..."))
                            time.sleep(0.5)
                            continue
                    else:
                        error_msg = data.get('msg', 'Không Xác Định')
                        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Lỗi API : {error_msg}"))
                        
                        if data.get("code") == 1004 and "Must login" in error_msg:
                            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Đang Thử Refresh Session..."))
                            if refresh_session():
                                continue
                        break
                except Exception as json_error:
                    print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi Parse Json : {json_error}"))
            else:
                print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi HTTP : {response.status_code}"))
                
        except requests.RequestException as e:
            print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi Khi Kiểm Tra Kết Quả : {e}"))
            break
        except Exception as e:
            print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi Không Xác Định : {e}"))
            break
    
    print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Không Thể Lấy Kết Quả Sau Nhiều Lần Thử"))
    return False

vong_choi = None
chuoi_thang = 0
count_thang = 0

def lich_su():
    global vong_choi
    try:
        response = requests.get(api_10_van, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                room_mapping = {
                    1: "Nhà Kho",
                    2: "Phòng Họp",
                    3: "Phòng Giám Đốc",
                    4: "Phòng Trò Chuyện",
                    5: "Phòng Giám Sát",
                    6: "Văn Phòng",
                    7: "Phòng Tài Vụ",
                    8: "Phòng Nhân Sự"
                }
                issues = data.get("data", [])[:3]
                vong_choi_truoc = issues[0]["issue_id"]
                id_ket_qua_vong_truoc = issues[0]["killed_room_id"]
                ten_phong_vong_truoc = room_mapping.get(id_ket_qua_vong_truoc, "Không Xác Định")
                vong_choi_hien_tai = issues[0]["issue_id"] + 1
                issue_details = []
                for issue in issues:
                    issue_id = issue["issue_id"]
                    killed_room_id = issue["killed_room_id"]
                    room_name = room_mapping.get(killed_room_id, "Không Xác Định")
                    issue_details.append(f"Issue ID : {issue_id}, Room : {room_name}")

                if vong_choi_truoc != vong_choi:
                    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Vòng Chơi Hiện Tại : {vong_choi_hien_tai}"))
                    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Kết Quả Vòng Chơi Trước : {vong_choi_truoc} | {ten_phong_vong_truoc}"))
                    vong_choi = vong_choi_truoc
                    
                    if prediction_enabled:
                        try:
                            predicted_room = phan_tich_lich_su()
                        except Exception as e:
                            print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi Khi Phân Tích Và Dự Đoán : {e}"))
                            predicted_room = None
                    
                    kiem_tra_dieu_kien(issue_details)
                    print("\033[1;97m════════════════════════════════════════════════")
    except requests.RequestException as e:
        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi : {e}"))

number_cuoc = 0

def kiem_tra_dieu_kien(issue_details):
    global number_cuoc,amount,cuoc_ban_dau,chuoi_thang,count_thang,tool_running
    room_mapping = {
        "Nhà Kho": 1,
        "Phòng Họp": 2,
        "Phòng Giám Đốc": 3,
        "Phòng Trò Chuyện": 4,
        "Phòng Giám Sát": 5,
        "Văn Phòng": 6,
        "Phòng Tài Vụ": 7,
        "Phòng Nhân Sự": 8
    }
    room_0 = issue_details[0].split(",")[1].split(":")[1].strip()
    room_1 = issue_details[1].split(",")[1].split(":")[1].strip()
    room_2 = issue_details[2].split(",")[1].split(":")[1].strip()
    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Phòng 0 : {room_0} | Phòng 1 : {room_1} | Phòng 2 : {room_2} | Số Tiền Cược : {number_cuoc}"))
    
    if prediction_enabled and len(history_results) > 0:
        try:
            predicted_room = min(Counter(history_results).items(), key=lambda x: x[1])[0]
            predicted_room_id = room_mapping.get(predicted_room)
            if predicted_room_id:
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Sử Dụng Dự Đoán : {predicted_room}"))
                dat_cuoc(predicted_room_id)
                number_cuoc = 1
                return
        except Exception as e:
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Lỗi Khi Sử Dụng Dự Đoán : {e}"))
            print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Chuyển Sang Setting Cũ !"))
    
    if room_0 != room_1 and number_cuoc == 0 :
        room_name = issue_details[1].split(",")[1].split(":")[1].strip()
        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Đặt Cược Theo : {room_name}"))
        room_id = room_mapping.get(room_name, None)
        dat_cuoc(room_id)
        number_cuoc = 1
        return
    elif room_0 != room_1 and room_0 != room_2 and number_cuoc == 1 :
        room_name = issue_details[1].split(",")[1].split(":")[1].strip()
        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Thắng - Đặt Cược Tiếp : {room_name}"))
        room_id = room_mapping.get(room_name, None)
        dat_cuoc(room_id)
        number_cuoc = 1
        return
    elif room_0 != room_1 and room_0 == room_2 and number_cuoc == 1 :
        room_name = issue_details[1].split(",")[1].split(":")[1].strip()
        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Thua - Gấp Đôi Cược : {room_name}"))
        if not tool_running:
            return
        
        if martingale_enabled:
            amount = int(amount * multiplier_1)
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Gấp Cược x{multiplier_1} : {amount:.2f} Build"))
            number_cuoc = 2
        else:
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Giữ Nguyên Số Tiền Cược : {amount:.2f} Build"))
            number_cuoc = 1
            
        room_id = room_mapping.get(room_name, None)
        dat_cuoc(room_id)
        return
    elif room_0 != room_1 and room_0 != room_2 and number_cuoc == 2 :
        room_name = issue_details[1].split(",")[1].split(":")[1].strip()
        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Thắng - Reset Về Cơ Bản : {room_name}"))
        if not tool_running:
            return
        amount = cuoc_ban_dau
        room_id = room_mapping.get(room_name, None)
        dat_cuoc(room_id)
        number_cuoc = 1
        return
    elif room_0 != room_1 and room_0 == room_2 and number_cuoc == 2 :
        room_name = issue_details[1].split(",")[1].split(":")[1].strip()
        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Thua - Gấp Đôi Cược Lần 2 : {room_name}"))
        if not tool_running:
            return
        
        if martingale_enabled:
            amount = int(amount * multiplier_2)
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Gấp Cược x{multiplier_2} : {amount:.2f} Build"))
            number_cuoc = 3
        else:
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Giữ Nguyên Số Tiền Cược : {amount:.2f} Build"))
            number_cuoc = 1
            
        room_id = room_mapping.get(room_name, None)
        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Đặt Cược {room_name}, Id : {room_id}"))
        dat_cuoc(room_id)
        return
    elif room_0 != room_1 and room_0 != room_2 and number_cuoc == 3 :
        room_name = issue_details[1].split(",")[1].split(":")[1].strip()
        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Thắng - Reset Về Cơ Bản : {room_name}"))
        if not tool_running:
            return
        amount = cuoc_ban_dau
        room_id = room_mapping.get(room_name, None)
        dat_cuoc(room_id)
        number_cuoc = 1
        return
    elif room_0 != room_1 and room_0 == room_2 and number_cuoc == 3 :
        room_name = issue_details[1].split(",")[1].split(":")[1].strip()
        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Thua - Gấp Đôi Cược Lần 3 : {room_name}"))
        if not tool_running:
            return
        
        if martingale_enabled:
            amount = int(amount * multiplier_3)
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Gấp Cược x{multiplier_3} : {amount:.2f} Build"))
            number_cuoc = 4
        else:
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Giữ Nguyên Số Tiền Cược : {amount:.2f} Build"))
            number_cuoc = 1
            
        room_id = room_mapping.get(room_name, None)
        dat_cuoc(room_id)
        return
    elif room_0 != room_1 and room_0 != room_2 and number_cuoc == 4 :
        room_name = issue_details[1].split(",")[1].split(":")[1].strip()
        print(Colorate.Diagonal(Colors.green_to_red, f"Thắng - Reset Về Cơ Bản : {room_name}"))
        if not tool_running:
            return
        
        if martingale_enabled:
            amount = cuoc_ban_dau
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Reset Về Số Tiền Ban Đầu : {amount:.2f} Build"))
        else:
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Giữ Nguyên Số Tiền Cược : {amount:.2f} Build"))
            
        room_id = room_mapping.get(room_name, None)
        dat_cuoc(room_id)
        number_cuoc = 1
        return
    elif room_0 != room_1 and room_0 == room_2 and number_cuoc == 4 :
        room_name = issue_details[1].split(",")[1].split(":")[1].strip()
        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Đã Đạt Gấp Cược Tối Đa - Reset : {room_name}"))
        if not tool_running:
            return
        
        if martingale_enabled:
            amount = cuoc_ban_dau
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Reset Về Số Tiền Ban Đầu : {amount:.2f} Build"))
        else:
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Giữ Nguyên Số Tiền Cược : {amount:.2f} Build"))
            
        room_id = room_mapping.get(room_name, None)
        dat_cuoc(room_id)
        number_cuoc = 1
        return
    elif room_0 == room_1 :
        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Phát Hiện Sát Thủ Vào 1 Phòng Liên Tục !"))
        if not tool_running:
            return
        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Chuỗi Thắng Liên Tiếp Hiện Tại : {chuoi_thang} Ván"))

def dat_cuoc(room_id):
    global so_du_truoc_cuoc
    
    room_mapping_debug = {
        1: "Nhà Kho",
        2: "Phòng Họp", 
        3: "Phòng Giám Đốc",
        4: "Phòng Trò Chuyện",
        5: "Phòng Giám Sát",
        6: "Văn Phòng",
        7: "Phòng Tài Vụ",
        8: "Phòng Nhân Sự"
    }
    room_name_debug = room_mapping_debug.get(room_id, "Không Xác Định")
    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Đặt Cược Phòng : {room_name_debug}, Id : {room_id}"))
    
    body = {
        "asset_type": "BUILD",
        "bet_amount": amount,
        "room_id": room_id,
        "user_id": headers["user-id"]
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                so_du_truoc_cuoc = data["data"]["cwallet"]["ctoken_contribute"]
    except:
        pass
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(api_cuoc, headers=headers, json=body, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("code") == 0:
                        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Cược Thành Công {amount:.2f} Build (Lần {attempt + 1})"))
                        kiem_tra_ket_qua_cuoc()
                        return True
                    else:
                        error_msg = data.get("message", "Không Xác Định")
                        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lần {attempt + 1} : {error_msg}"))
                except Exception as json_error:
                    print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lần {attempt + 1} : Lỗi Parse Json - {json_error}"))
            else:
                print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lần {attempt + 1} : HTTP {response.status_code}"))

        except requests.RequestException as e:
            print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lần {attempt + 1} : Lỗi Mạng - {e}"))
        except Exception as e:
            print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lần {attempt + 1} : Lỗi Không Xác Định - {e}"))
        
        if attempt < max_retries - 1:
            time.sleep(1)
    
    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Không Thể Đặt Cược Sau {max_retries} Lần Thử !"))
    return False

def refresh_session():
    global headers
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Session Đã Được Refresh Thành Công !"))
                return True
            else:
                print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Không Thể Refresh Session : {data.get('message', 'Lỗi')}"))
                return False
        else:
            print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi HTTP Khi Refresh : {response.status_code}"))
            return False
    except Exception as e:
        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi Refresh Session : {e}"))
        return False

def test_api_connection():
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
            	return True
            else:
                return False
        else:
            return False
    except Exception as e:
        return False
    
    try:
        response = requests.get(api_10_van, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        return False
    
    try:
        response = requests.get(api_my_joined, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        return False
    return True
    
if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    banner()

    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Số Tiền Cược Ban Đầu : {cuoc_ban_dau:.2f} Build"))
    if stop_loss_enabled:
        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Stop Loss : -{stop_loss_amount} Build"))
        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Take Profit : +{take_profit_amount} Build"))
    else:
        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Stop Loss/Take Profit : Tắt"))

    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Gấp Đôi Cược : {'Bật' if martingale_enabled else 'Tắt'}"))
    if martingale_enabled:
        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Hệ Số Gấp : Lần Đầu : x{multiplier_1} | Lần 2 : x{multiplier_2} | Lần 3 : x{multiplier_3}"))
    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Tự Động Phân Tích Và Dự Đoán : {'Bật' if prediction_enabled else 'Tắt'}"))
    print("\033[1;97m════════════════════════════════════════════════")

    login()

    if not test_api_connection():
        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Có Lỗi Với API, Vui Lòng Kiểm Tra Lại Thông Tin Đăng Nhập !"))
        sys.exit(1)

    if prediction_enabled:
        try:
            phan_tich_lich_su()
        except Exception as e:
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Lỗi Khi Phân Tích Lịch Sử Ban Đầu : {e}"))
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Tool Sẽ Tiếp Tục Chạy Với Setting Cũ"))

    try:
        while tool_running:
            lich_su()
            if not tool_running:
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Tool Đã Dừng Do Đã Đạt Điều Kiện Stop Loss/Take Profit !"))
                break
            time.sleep(15)
    except KeyboardInterrupt:
        print(Colorate.Diagonal(Colors.green_to_red, "[♤] ➩ Cảm Ơn Bạn Đã Sử Dụng Tool, Chúc Bạn May Mắn !"))
        sys.exit()