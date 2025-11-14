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
\033[1;32m[\033[1;31m*\033[1;32m]\033[1;33m ➩ \033[1;32mBạn Đang Sử Dụng \033[1;31m: \033[1;36mTool Bumx Facebook
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
    
def Delay(value):
    print(" " * 60, end="\r")
    while not(value <= 1):
        value -= 0.123
        print(f'''\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;36mTVHTool \033[1;32m| \033[1;33mDelay \033[1;31m: \033[1;34m{str(value)[0:5]} \033[1;32m| \033[1;35m[\033[1;30m░    \033[1;35m]''', '               ', end = '\r')
        sleep(0.02)
        print(f'''\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;36mTVHTool \033[1;32m| \033[1;33mDelay \033[1;31m: \033[1;34m{str(value)[0:5]} \033[1;32m| \033[1;35m[\033[1;30m ░   \033[1;35m]''', '               ', end = '\r')
        sleep(0.02)
        print(f'''\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;36mTVHTool \033[1;32m| \033[1;33mDelay \033[1;31m: \033[1;34m{str(value)[0:5]} \033[1;32m| \033[1;35m[\033[1;30m  ░  \033[1;35m]''', '               ', end = '\r')
        sleep(0.02)
        print(f'''\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;36mTVHTool \033[1;32m| \033[1;33mDelay \033[1;31m: \033[1;34m{str(value)[0:5]} \033[1;32m| \033[1;35m[\033[1;30m   ░ \033[1;35m]''', '               ', end = '\r')
        sleep(0.02)
        print(f'''\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;36mTVHTool \033[1;32m| \033[1;33mDelay \033[1;31m: \033[1;34m{str(value)[0:5]} \033[1;32m| \033[1;35m[\033[1;30m    ░\033[1;35m]''', '               ', end = '\r')
        sleep(0.02)
        print(f'''\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;36mTVHTool \033[1;32m| \033[1;33mDelay \033[1;31m: \033[1;34m{str(value)[0:5]} \033[1;32m| \033[1;35m[\033[1;30m    █\033[1;35m]''', '               ', end = '\r')
        sleep(0.02)
        print(f'''\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;36mTVHTool \033[1;32m| \033[1;33mDelay \033[1;31m: \033[1;34m{str(value)[0:5]} \033[1;32m| \033[1;35m[\033[1;30m   █ \033[1;35m]''', '               ', end = '\r')
        sleep(0.02)
        print(f'''\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;36mTVHTool \033[1;32m| \033[1;33mDelay \033[1;31m: \033[1;34m{str(value)[0:5]} \033[1;32m| \033[1;35m[\033[1;30m  █  \033[1;35m]''', '               ', end = '\r')
        sleep(0.02)
        print(f'''\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;36mTVHTool \033[1;32m| \033[1;33mDelay \033[1;31m: \033[1;34m{str(value)[0:5]} \033[1;32m| \033[1;35m[\033[1;30m █   \033[1;35m]''', '               ', end = '\r')
        sleep(0.02)
        print(f'''\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;36mTVHTool \033[1;32m| \033[1;33mDelay \033[1;31m: \033[1;34m{str(value)[0:5]} \033[1;32m| \033[1;35m[\033[1;30m█    \033[1;35m]''', '               ', end = '\r')
        sleep(0.02)
    print(" " * 60, end="\r")
    
def decode_base64(encoded_str):
    decoded_bytes = base64.b64decode(encoded_str)
    decoded_str = decoded_bytes.decode('utf-8')
    return decoded_str

def encode_to_base64(_data):
    byte_representation = _data.encode('utf-8')
    base64_bytes = base64.b64encode(byte_representation)
    base64_string = base64_bytes.decode('utf-8')
    return base64_string

def facebook_info(cookie: str, timeout: int = 15):
    try:
        session = requests.Session()
        session_id = str(uuid.uuid4())
        fb_dtsg = ""
        jazoest = ""
        lsd = ""
        name = ""
        user_id = cookie.split("c_user=")[1].split(";")[0]

        headers = {
            "authority": "web.facebook.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "vi",
            "sec-ch-prefers-color-scheme": "light",
            "sec-ch-ua": '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/106.0.0.0 Safari/537.36",
            "viewport-width": "1366",
            "Cookie": cookie
        }

        url = session.get(f"https://web.facebook.com/{user_id}", headers=headers, timeout=timeout).url
        response = session.get(url, headers=headers, timeout=timeout).text

        fb_token = re.findall(r'\["DTSGInitialData",\[\],\{"token":"(.*?)"\}', response)
        if fb_token:
            fb_dtsg = fb_token[0]

        jazo = re.findall(r'jazoest=(.*?)\"', response)
        if jazo:
            jazoest = jazo[0]

        lsd_match = re.findall(r'"LSD",\[\],\{"token":"(.*?)"\}', response)
        if lsd_match:
            lsd = lsd_match[0]

        get = session.get("https://web.facebook.com/me", headers=headers, timeout=timeout).url
        url = "https://web.facebook.com/" + get.split("%2F")[-2] + "/" if "next=" in get else get
        response = session.get(url, headers=headers, params={"locale": "vi_VN"}, timeout=timeout)

        data_split = response.text.split('"CurrentUserInitialData",[],{')
        json_data_raw = "{" + data_split[1].split("},")[0] + "}"
        parsed_data = json.loads(json_data_raw)

        user_id = parsed_data.get("USER_ID", "0")
        name = parsed_data.get("NAME", "")

        if user_id == "0" and name == "":
            print("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mCookie Đã Bị Die Hoặc Hết Hạn !")
            return {'success': False}
        elif "828281030927956" in response.text:
            print("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mTài Khoản Bị 956 Checkpoint !")
            return {'success': False}
        elif "1501092823525282" in response.text:
            print("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mTài Khoản Bị 282 Checkpoint !")
            return {'success': False}
        elif "601051028565049" in response.text:
            print("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mTài Khoản Bị Block Do Spam !")
            return {'success': False}

        json_data = {
            'success': True,
            'user_id': user_id,
            'fb_dtsg': fb_dtsg,
            'jazoest': jazoest,
            'lsd': lsd,
            'name': name,
            'session': session,
            'session_id': session_id,
            'cookie': cookie,
            'headers': headers
        }
        return json_data

    except Exception as e:
        print(f"\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mLỗi : {e}")
        return {'success': False}

def get_post_id(session,cookie,link):
    print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mĐang Lấy Post Id...', end='\r')
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'dpr': '1',
        'priority': 'u=0, i',
        'sec-ch-prefers-color-scheme': 'light',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'cookie': cookie,
    }
    try:
        response = session.get(link, headers=headers, timeout=15).text
        response= re.sub(r"\\", "", response)
        
        page_id=''
        post_id=''
        stories_id=''
        permalink_id=''
        try:
            if '"post_id":"' in str(response):
                permalink_id=re.findall('"post_id":".*?"',response)[0].split(':"')[1].split('"')[0]
                print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mPermalink Id Là \033[1;31m: \033[1;36m{permalink_id[:20]}      ', end='\r')
        except:
            pass
        try:
            if 'posts' in str(response):
                post_id=response.split('posts')[1].split('"')[0]
                post_id=post_id.replace("/", "")
                post_id = re.sub(r"\\", "", post_id)
                print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mPost Id Là \033[1;31m: \033[1;36m{post_id[:20]}       ', end='\r')
        except:
            pass
        try:
            if 'storiesTrayType' in response and not '"profile_type_name_for_content":"PAGE"' in response:
                stories_id=re.findall('"card_id":".*?"',response)[0].split('":"')[1].split('"')[0]
                print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mStories Id Là \033[1;31m: \033[1;36m{stories_id[:20]}      ', end='\r')
        except:
            pass
        try:
            if '"page_id"' in response:
                page_id=re.findall('"page_id":".*?"',response)[0].split('id":"')[1].split('"')[0]
                print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mPage Id Là \033[1;31m: \033[1;36m{page_id[:20]}        ', end='\r')
        except:
            pass
        return {'success':True,'post_id':post_id,'permalink_id':permalink_id,'stories_id':stories_id,'page_id':page_id}
    except Exception as e:
        print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mLỗi Khi Lấy Id Post \033[1;32m: \033[1;36m{e}')
        return {'success':False}

def react_post_perm(data,object_id,type_react):
    print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mĐang Thả {type_react} Vào {object_id[:20]}       ',end='\r')

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://web.facebook.com',
        'priority': 'u=1, i',
        'referer': 'https://web.facebook.com/'+str(object_id),
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'x-fb-friendly-name': 'CometUFIFeedbackReactMutation',
        'x-fb-lsd': data['lsd'],
        'cookie': data['cookie'],
    }
    react_list = {"LIKE": "1635855486666999","LOVE": "1678524932434102","CARE": "613557422527858","HAHA": "115940658764963","WOW": "478547315650144","SAD": "908563459236466","ANGRY": "444813342392137"}
    
    json_data = {
        'av': str(data['user_id']),
        '__user': str(data['user_id']),
        'fb_dtsg': data['fb_dtsg'],
        'jazoest': str(data['jazoest']),
        'lsd': str(data['lsd']),
        'fb_api_caller_class': 'RelayModern',
        'fb_api_req_friendly_name': 'CometUFIFeedbackReactMutation',
        'variables': '{"input":{"attribution_id_v2":"CometSinglePostDialogRoot.react,comet.post.single_dialog,via_cold_start,'+str(int(time.time()*1000))+',893597,,,","feedback_id":"'+encode_to_base64(str('feedback:'+object_id))+'","feedback_reaction_id":"'+str(react_list.get(type_react.upper()))+'","feedback_source":"OBJECT","is_tracking_encrypted":true,"tracking":["AZWEqXNx7ELYfHNA7b4CrfdPexzmIf2rUloFtOZ9zOxrcEuXq9Nr8cAdc1kP5DWdKx-DdpkffT5hoGfKYfh0Jm8VlJztxP7elRZBQe5FqkP58YxifFUwdqGzQnJPfhGupHYBjoq5I5zRHXPrEeuJk6lZPblpsrYQTO1aDBDb8UcDpW8F82ROTRSaXpL-T0gnE3GyKCzqqN0x99CSBp1lCZQj8291oXhMoeESvV__sBVqPWiELtFIWvZFioWhqpoAe_Em15uPs4EZgWgQmQ-LfgOMAOUG0TOb6wDVO75_PyQ4b8uTdDWVSEbMPTCglXWn5PJzqqN4iQzyEKVe8sk708ldiDug7SlNS7Bx0LknC7p_ihIfVQqWLQpLYK6h4JWZle-ugySqzonCzb6ay09yrsvupxPUGp-EDKhjyEURONdtNuP-Fl3Oi1emIy61-rqISLQc-jp3vzvnIIk7r_oA1MKT065zyX-syapAs-4xnA_12Un5wQAgwu5sP9UmJ8ycf4h1xBPGDmC4ZkaMWR_moqpx1k2Wy4IbdcHNMvGbkkqu12sgHWWznxVfZzrzonXKLPBVW9Y3tlQImU9KBheHGL_ADG_8D-zj2S9JG2y7OnxiZNVAUb1yGrVVrJFnsWNPISRJJMZEKiYXgTaHVbZBX6CdCrA7gO25-fFBvVfxp2Do3M_YKDc5Ttq1BeiZgPCKogeTkSQt1B67Kq7FTpBYJ05uEWLpHpk1jYLH8ppQQpSEasmmKKYj9dg7PqbHPMUkeyBtL69_HkdxtVhDgkNzh1JerLPokIkdGkUv0RALcahWQK4nR8RRU2IAFMQEp-FsNk_VKs_mTnZQmlmSnzPDymkbGLc0S1hIlm9FdBTQ59--zU4cJdOGnECzfZq4B5YKxqxs0ijrcY6T-AOn4_UuwioY"],"session_id":"'+data['session_id']+'","actor_id":"'+str(data['user_id'])+'","client_mutation_id":"1"},"useDefaultActor":false,"__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider":false}',
        'server_timestamps': 'true',
        'doc_id': '24034997962776771',
    }
    try:
        response = data['session'].post('https://web.facebook.com/api/graphql/', headers=headers, data=json_data, timeout=15).text
        return True
    except Exception:
        return False

def react_post_defaul(data,object_id,type_react):
    print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mĐang Thả {type_react} Vào {object_id[:20]}       ', end='\r')

    react_list = {"LIKE": "1635855486666999","LOVE": "1678524932434102","CARE": "613557422527858","HAHA": "115940658764963","WOW": "478547315650144","SAD": "908563459236466","ANGRY": "444813342392137"}
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://web.facebook.com',
        'priority': 'u=1, i',
        'referer': 'https://web.facebook.com/'+str(object_id),
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'x-fb-friendly-name': 'CometUFIFeedbackReactMutation',
        'x-fb-lsd': data['lsd'],
        'cookie': data['cookie'],
    }
    
    json_data = {
        'av': str(data['user_id']),
        '__user': str(data['user_id']),
        'fb_dtsg': data['fb_dtsg'],
        'jazoest': data['jazoest'],
        'lsd': data['lsd'],
        'fb_api_caller_class': 'RelayModern',
        'fb_api_req_friendly_name': 'CometUFIFeedbackReactMutation',
        'variables': '{"input":{"attribution_id_v2":"CometSinglePostDialogRoot.react,comet.post.single_dialog,via_cold_start,'+str(int(time.time()*1000))+',912367,,,","feedback_id":"'+encode_to_base64(str('feedback:'+object_id))+'","feedback_reaction_id":"'+str(react_list.get(type_react.upper()))+'","feedback_source":"OBJECT","is_tracking_encrypted":true,"tracking":["AZWEqXNx7ELYfHNA7b4CrfdPexzmIf2rUloFtOZ9zOxrcEuXq9Nr8cAdc1kP5DWdKx-DdpkffT5hoGfKYfh0Jm8VlJztxP7elRZBQe5FqkP58YxifFUwdqGzQnJPfhGupHYBjoq5I5zRHXPrEeuJk6lZPblpsrYQTO1aDBDb8UcDpW8F82ROTRSaXpL-T0gnE3GyKCzqqN0x99CSBp1lCZQj8291oXhMoeESvV__sBVqPWiELtFIWvZFioWhqpoAe_Em15uPs4EZgWgQmQ-LfgOMAOUG0TOb6wDVO75_PyQ4b8uTdDWVSEbMPTCglXWn5PJzqqN4iQzyEKVe8sk708ldiDug7SlNS7Bx0LknC7p_ihIfVQqWLQpLYK6h4JWZle-ugySqzonCzb6ay09yrsvupxPUGp-EDKhjyEURONdtNuP-Fl3Oi1emIy61-rqISLQc-jp3vzvnIIk7r_oA1MKT065zyX-syapAs-4xnA_12Un5wQAgwu5sP9UmJ8ycf4h1xBPGDmC4ZkaMWR_moqpx1k2Wy4IbdcHNMvGbkkqu12sgHWWznxVfZzrzonXKLPBVW9Y3tlQImU9KBheHGL_ADG_8D-zj2S9JG2y7OnxiZNVAUb1yGrVVrJFnsWNPISRJJMZEKiYXgTaHVbZBX6CdCrA7gO25-fFBvVfxp2Do3M_YKDc5Ttq1BeiZgPCKogeTkSQt1B67Kq7FTpBYJ05uEWLpHpk1jYLH8ppQQpSEasmmKKYj9dg7PqbHPMUkeyBtL69_HkdxtVhDgkNzh1JerLPokIkdGkUv0RALcahWQK4nR8RRU2IAFMQEp-FsNk_VKs_mTnZQmlmSnzPDymkbGLc0S1hIlm9FdBTQ59--zU4cJdOGnECzfZq4B5YKxqxs0ijrcY6T-AOn4_UuwioY"],"session_id":"'+str(data['session_id'])+'","actor_id":"'+data['user_id']+'","client_mutation_id":"1"},"useDefaultActor":false,"__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider":false}',
        'server_timestamps': 'true',
        'doc_id': '24034997962776771',
    }
    try:
        response = data['session'].post('https://web.facebook.com/api/graphql/', headers=headers, data=json_data, timeout=15)
        response.raise_for_status()
        return True
    except:
        return False

def react_stories(data,object_id):
    print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mĐang Tim Story {object_id[:20]}      ', end='\r')

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://web.facebook.com',
        'priority': 'u=1, i',
        'referer': 'https://web.facebook.com/',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'x-fb-friendly-name': 'useStoriesSendReplyMutation',
        'x-fb-lsd': data['lsd'],
        'cookie': data['cookie']
    }

    json_data = {
        'av': str(data['user_id']),
        '__user': str(data['user_id']),
        'fb_dtsg': data['fb_dtsg'],
        'jazoest': str(data['jazoest']),
        'lsd': data['lsd'],
        'fb_api_caller_class': 'RelayModern',
        'fb_api_req_friendly_name': 'useStoriesSendReplyMutation',
        'variables': '{"input":{"attribution_id_v2":"StoriesCometSuspenseRoot.react,comet.stories.viewer,via_cold_start,'+str(int(time.time()*1000))+',33592,,,","lightweight_reaction_actions":{"offsets":[0],"reaction":"❤️"},"message":"❤️","story_id":"'+str(object_id)+'","story_reply_type":"LIGHT_WEIGHT","actor_id":"'+str(data['user_id'])+'","client_mutation_id":"2"}}',
        'server_timestamps': 'true',
        'doc_id': '9697491553691692',
    }
    try:
        response = data['session'].post('https://web.facebook.com/api/graphql/',  headers=headers, data=json_data, timeout=15).json()
        if response.get('extensions', {}).get('is_final') == True:
            return True
        else:
            return False
    except Exception:
        return False

def react_post(data,link,type_react):
    res_object_id=get_post_id(data['session'],data['cookie'],link)
    if not res_object_id.get('success'):
        return False
        
    if res_object_id.get('stories_id'):
        return react_stories(data,res_object_id['stories_id'])
    elif res_object_id.get('permalink_id'):
        return react_post_perm(data,res_object_id['permalink_id'],type_react)
    elif res_object_id.get('post_id'):
        return react_post_defaul(data,res_object_id['post_id'],type_react)
    return False

def wallet(authorization):
    headers = {
        'User-Agent': 'Dart/3.3 (dart:io)',
        'Content-Type': 'application/json',
        'lang': 'en',
        'version': '37',
        'origin': 'app',
        'authorization': authorization,
    }
    try:
        response = requests.get('https://api-v2.bumx.vn/api/business/wallet', headers=headers, timeout=10).json()
        return response.get('data', {}).get('balance', 'N/A')
    except requests.exceptions.RequestException as e:
        return f"\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mLỗi \033[1;32m: \033[1;36m{e}"
    except json.JSONDecodeError:
        return "\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mLỗi Khi Phản Hồi Giải Mã Server !"

def load(session,authorization,job):
    print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mĐang Mở Nhiệm Vụ...', end='\r')

    headers = {
        'User-Agent': 'Dart/3.3 (dart:io)',
        'Content-Type': 'application/json',
        'lang': 'en',
        'version': '37',
        'origin': 'app',
        'authorization': authorization,
    }

    json_data = {'buff_id': job['buff_id']}
    try:
        response = session.post('https://api-v2.bumx.vn/api/buff/load-mission', headers=headers, json=json_data, timeout=10).json()
        return response
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mLỗi Khi Tải Thông Tin Nhiệm Vụ !')
        return None

def get_job(session,authorization):
    print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mĐang Lấy Nhiệm Vụ...', end='\r')
    headers = {
        'User-Agent': 'Dart/3.3 (dart:io)',
        'lang': 'en',
        'version': '37',
        'origin': 'app',
        'authorization': authorization,
    }
    params = {'is_from_mobile': 'true'}
    
    try:
        response = session.get('https://api-v2.bumx.vn/api/buff/mission', params=params, headers=headers, timeout=10)
        response.raise_for_status()
        response_json = response.json()
    except requests.exceptions.RequestException:
        print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mLỗi Khi Lấy Nhiệm Vụ !')
        return []
    except json.JSONDecodeError:
        print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mLỗi Khi Giải Mã Json Để Lấy Nhiệm Vụ !')
        return []

    print(f"\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mĐã Tìm Thấy {response_json.get('count', 0)} Nhiệm Vụ !", end='\r')
    
    JOB=[]
    for i in response_json.get('data', []):
        json_job={
            "_id":i['_id'],
            "buff_id":i['buff_id'],
            "type":i['type'],
            "name":i['name'],
            "status":i['status'],
            "object_id":i['object_id'],
            "business_id":i['business_id'],
            "mission_id":i['mission_id'],
            "create_date":i['create_date'],
            "note":i['note'],
            "require":i['require'],
        }
        JOB.insert(0,json_job)
    return JOB

def reload(session, authorization, type_job, retries=3):
    print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mĐang Nhấn Tải Danh Sách Nhiệm Vụ...', end='\r')
    if retries == 0:
        print('\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mTải Danh Sách Nhiệm Vụ Thất Bại, Bỏ Qua Chu Kỳ Này !')
        return

    headers = {
        'User-Agent': 'Dart/3.3 (dart:io)',
        'Content-Type': 'application/json',
        'lang': 'en',
        'version': '37',
        'origin': 'app',
        'authorization': authorization,
    }
    json_data = {'type': type_job}
    try:
        response = session.post('https://api-v2.bumx.vn/api/buff/get-new-mission', headers=headers, json=json_data, timeout=10).json()
    except Exception:
        print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mLỗi Khi Tải Lại Nhiệm Vụ, Thử Lại Trong 2 Giây...')
        time.sleep(2)
        return reload(session, authorization, type_job, retries - 1)

def submit(session,authorization,job,reslamjob,res_load):
    print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mĐang Nhấn Hoàn Thành Nhiệm Vụ...', end='\r')
    headers = {
        'User-Agent': 'Dart/3.3 (dart:io)',
        'Content-Type': 'application/json',
        'lang': 'en',
        'version': '37',
        'origin': 'app',
        'authorization': authorization,
    }
    json_data = {
        'buff_id': job['buff_id'],
        'comment': None, 'comment_id': None, 'code_submit': None,
        'attachments': [], 'link_share': '', 'code': '',
        'is_from_mobile': True, 'type': job['type'], 'sub_id': None, 'data': None,
    }

    if job['type']=='like_facebook':
        json_data['comment'] = 'tt nha'

    try:
        response = session.post('https://api-v2.bumx.vn/api/buff/submit-mission', headers=headers, json=json_data, timeout=10).json()
        if response.get('success') == True:
            message = response.get('message', '')
            _xu = '0'
            sonvdalam = '0'
            try:
                _xu = message.split('cộng ')[1].split(',')[0]
                sonvdalam = message.split('làm: ')[1]
            except IndexError:
                pass
            return [True,_xu,sonvdalam]
        return [False,'0','0']
    except Exception:
        print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mLỗi Khi Submit !')
        return [False,'0','0']
    
def report(session, authorization, job, retries=3):
    print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mĐang Báo Lỗi...', end='\r')
    if retries == 0:
        print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mBáo Lỗi Thất Bại Sau Nhiều Lần Thử, Bỏ Qua...')
        return

    headers = {
        'User-Agent': 'Dart/3.3 (dart:io)',
        'Content-Type': 'application/json',
        'lang': 'en',
        'version': '37',
        'origin': 'app',
        'authorization': authorization,
    }
    json_data = {'buff_id': job['buff_id']}
    try:
        response = session.post('https://api-v2.bumx.vn/api/buff/report-buff', headers=headers, json=json_data, timeout=10).json()
        print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mĐã Báo Lỗi Thành Công Và Bỏ Qua Nhiệm Vụ !')
        print("\033[1;97m════════════════════════════════════════════════")
    except Exception:
        print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mBáo Lỗi Không Thành Công, Thử Lại ({retries-1} Lần Còn Lại)...')
        print("\033[1;97m════════════════════════════════════════════════")
        time.sleep(2)
        return report(session, authorization, job, retries - 1)

def lam_job(data,jobs,type_job_doing):
    print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mĐang Làm Nhiệm Vụ...', end='\r')

    link='https://web.facebook.com/'+jobs['object_id']
    if type_job_doing=='like_facebook':
        react_type = 'LIKE'
        icon = jobs.get('icon', '').lower()
        if 'love' in icon or 'thuongthuong' in icon: react_type='LOVE'
        elif 'care' in icon: react_type='CARE'
        elif 'wow' in icon: react_type='WOW'
        elif 'sad' in icon: react_type='SAD'
        elif 'angry' in icon: react_type='ANGRY'
        elif 'haha' in icon: react_type='HAHA'
        return react_post(data,link,react_type.upper())
    return False
        
def add_account_fb(session,authorization,user_id):
    headers = {
        'Content-Type': 'application/json',
        'lang': 'en',
        'version': '37',
        'origin': 'app',
        'authorization': authorization,
    }
    json_data = {'link': f'https://web.facebook.com/profile.php?id={str(user_id)}'}
    try:
        response = session.post('https://api-v2.bumx.vn/api/account-facebook/connect-link', headers=headers, json=json_data, timeout=10).json()
        print(f"\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mKhai Báo Tài Khoản Fb \033[1;31m: \033[1;36m{response.get('message', 'No Message')}")
        sleep(1)
    except Exception as e:
        print(f"\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mLỗi Khi Khai Báo Tài Khoản Fb \033[1;32m: \033[1;36m{e}")
        sleep(1)

def print_state(status_job,_xu,jobdalam,dahoanthanh,tongcanhoanthanh,type_job, name_acc):
    hanoi_tz = timezone(timedelta(hours=7))
    now = datetime.now(hanoi_tz).strftime("%H:%M:%S")
    type_NV = {'like_facebook':'CAMXUC'}
    
    print(f"\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;36m({jobdalam.strip()}) \033[1;33m|"
          f"\033[1;31m{now} \033[1;33m|"
          f"\033[1;34m{type_NV.get(type_job, 'Không Xác Định')} \033[1;33m|"
          f"\033[1;35m+{_xu.strip()} Xu \033[1;33m|"
    )

def switch_facebook_account(cookie, authorization):
    print("\033[1;97m════════════════════════════════════════════════")
    data = facebook_info(cookie)
    if not data or not data.get('success'):
        print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mCookie Không Hợp Lệ, Bỏ Qua Tài Khoản Này !')
        return None

    print(f"\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mTên Acc Facebook \033[1;31m: \033[1;36m{data['name']}")
    print(f"\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mId Acc Facebook \033[1;31m: \033[1;36m{data['user_id']}")
    print("\033[1;97m════════════════════════════════════════════════")
    add_account_fb(data['session'], authorization, data['user_id'])
    print("\033[1;97m════════════════════════════════════════════════")
    sleep(1.5)
    return data

def main_bumx_free():
    os.system('cls' if os.name== 'nt' else 'clear')
    banner()
    
    if os.path.exists('Authorization_Bumx.txt'):
        x=input('\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mBạn Có Muốn Dùng Lại Authorization Bumx Cũ Không ? \033[1;97m(\033[1;32my\033[1;97m/\033[1;31mn\033[1;97m) \033[1;31m: \033[1;36m').lower()
        print("\033[1;97m════════════════════════════════════════════════")
        if x=='y':
            with open('Authorization_Bumx.txt','r',encoding='utf-8') as f:
                authorization=f.read().strip()
        else:
            authorization=input('\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mNhập Authorization Bumx \033[1;31m: \033[1;36m').strip()
            print("\033[1;97m════════════════════════════════════════════════")
            with open('Authorization_Bumx.txt','w',encoding='utf-8') as f: f.write(authorization)
    else:
        authorization=input('\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mNhập Authorization Bumx \033[1;31m: \033[1;36m').strip()
        print("\033[1;97m════════════════════════════════════════════════")
        with open('Authorization_Bumx.txt','w',encoding='utf-8') as f: f.write(authorization)
        
    print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mSố Dư \033[1;31m: \033[1;36m{wallet(authorization)} Đ')
    print("\033[1;97m════════════════════════════════════════════════")

    num_cookies = int(input('\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mNhập Số Lượng Cookie Facebook Mà Bạn Muốn Chạy \033[1;31m: \033[1;36m'))
    cookies_list = []
    for i in range(num_cookies):
        cookie_file = f'Cookie_Fb_{i+1}.txt'
        cookie = ''
        if os.path.exists(cookie_file):
            x = input(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mBạn Có Muốn Dùng Lại Cookie Facebook Đã Lưu Không ? \033[1;97m(\033[1;32my\033[1;97m/\033[1;31mn\033[1;97m) \033[1;31m: \033[1;36m').lower()
            print("\033[1;97m════════════════════════════════════════════════")

            if x == 'y':
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    cookie = f.read().strip()
            else:
                cookie = input(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mNhập Cookie Facebook Thứ {i+1} \033[1;31m: \033[1;36m').strip()
                print("\033[1;97m════════════════════════════════════════════════")
                with open(cookie_file, 'w', encoding='utf-8') as f:
                    f.write(cookie)
        else:
            cookie = input(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mNhập Cookie Facebook Thứ {i+1} \033[1;31m: \033[1;36m').strip()
            print("\033[1;97m════════════════════════════════════════════════")
            with open(cookie_file, 'w', encoding='utf-8') as f:
                f.write(cookie)
        if cookie:
            cookies_list.append(cookie)

    if not cookies_list:
        print("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mKhông Có Cookie Nào Được Nhập, Thoát !")
        sys.exit(1)

    switch_threshold = int(input('\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mSau Bao Nhiêu Nhiệm Vụ Thì Đổi Cookie Facebook \033[1;31m: \033[1;36m'))

    list_type_job=[]
    x = "1"
    print("\033[1;97m════════════════════════════════════════════════")
    
    job_map = {'1': 'like_facebook'}
    for i in x:
        job_type = job_map.get(i)
        if job_type:
            list_type_job.append(job_type)
        else:
            print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mLựa Chọn "{i}" Không Hợp Lệ, Thoát !')
            sys.exit(1)
            
    SO_NV=int(input('\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mLàm Bao Nhiêu Nhiệm Vụ Thì Dừng Tool \033[1;31m: \033[1;36m'))
    SO_NV1=SO_NV
    demht=0
    demsk=0
    
    delay1=int(input('\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mNhập Delay Tối Thiểu (Giây) \033[1;31m: \033[1;36m'))
    delay2=int(input('\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;32mNhập Delay Tối Đa (Giây) \033[1;31m: \033[1;36m'))

    current_cookie_index = 0
    tasks_on_current_cookie = 0
    valid_cookies = []
    
    for ck in cookies_list:
        info = facebook_info(ck)
        if info and info.get('success'):
            valid_cookies.append(ck)
        else:
            print(f"\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mCookie Không Hợp Lệ, Bỏ Qua !")
    
    if not valid_cookies:
        print("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mKhông Có Cookie Nào Hợp Lệ, Vui Lòng Kiểm Tra Lại !")
        sys.exit(1)
        
    data = switch_facebook_account(valid_cookies[current_cookie_index], authorization)
    if not data:
        print("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mCookie Đầu Tiên Không Hợp Lệ, Thoát !")
        sys.exit(1)

    os.system('cls' if os.name== 'nt' else 'clear')
    banner()

    while demht < SO_NV1:
        try:
            if tasks_on_current_cookie >= switch_threshold and len(valid_cookies) > 1:
                current_cookie_index = (current_cookie_index + 1) % len(valid_cookies)
                new_data = switch_facebook_account(valid_cookies[current_cookie_index], authorization)
                if new_data:
                    data = new_data
                    tasks_on_current_cookie = 0
                else:
                    print(f"\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mLỗi Với Cookie Thứ {current_cookie_index+1}, Loại Bỏ Khỏi Danh Sách Chạy !")
                    valid_cookies.pop(current_cookie_index)
                    if not valid_cookies:
                        print("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mTất Cả Cookie Đều Lỗi, Thoát !")
                        break
                    current_cookie_index = current_cookie_index % len(valid_cookies)
                    data = switch_facebook_account(valid_cookies[current_cookie_index], authorization)
                    tasks_on_current_cookie = 0

            if not list_type_job:
                print('\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mĐã Hết Loại Nhiệm Vụ Để Làm !')
                break
            
            for type_job in list_type_job:
                reload(data['session'],authorization,type_job)
            
            time.sleep(4)
            JOB = get_job(data['session'], authorization)
            
            if not JOB:
                print('\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mKhông Tìm Thấy Nhiệm Vụ, Chờ 10 Giây...', end='\r')
                time.sleep(10)
                continue

            for job in JOB:
                if demht >= SO_NV1: break
                try:
                    res_load = load(data['session'], authorization, job)
                    time.sleep(random.randint(2,4))
                    
                    if res_load and res_load.get('success') and job['type'] in list_type_job:
                        delay = random.randint(delay1, delay2)
                        start_job = time.time()
                        
                        status_job = lam_job(data, res_load, job['type'])
                        
                        if status_job:
                            res_submit = submit(data['session'], authorization, job, status_job, res_load)
                            if res_submit[0]:
                                demht+=1
                                tasks_on_current_cookie += 1
                                print_state('complete', res_submit[1], res_submit[2], demht, SO_NV1, job['type'], data['name'])
                                Delay(delay - (time.time() - start_job))
                            else:
                                raise Exception("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mSubmit Thất Bại !")
                        else:
                            raise Exception("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mHành Động (Cảm Xúc) Thất Bại !")
                    else:
                        raise Exception("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mLoad Nhiệm Vụ Thất Bại Hoặc Sai Loại Job !")

                except Exception:
                    print("\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mNhiệm Vụ Đang Bị Lỗi, Bỏ Qua Job Này !")
                    report(data['session'], authorization, job)
                    demsk += 1
                    time.sleep(4)
        
        except Exception as e:
            print(f'\033[1;32m[\033[1;31m♤\033[1;32m]\033[1;33m ➩ \033[1;31mLỗi \033[1;32m: \033[1;36m{e}')
            time.sleep(10)

if __name__ == "__main__":
    main_bumx_free()