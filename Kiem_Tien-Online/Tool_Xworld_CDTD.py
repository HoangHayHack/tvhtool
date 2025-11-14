# -*- coding: utf-8 -*-
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

SECRET = "MY_SECRET_SALT"

room_names_map = {
    "6": "Bậc Thầy Tấn Công",
    "5": "Quyền Sắt",
    "4": "Thợ Lặn Sâu",
    "3": "Cơn Lốc Sân Cỏ",
    "2": "Hiệp Sĩ Phi Nhanh",
    "1": "Vua Home Run",
}

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
\033[1;32m[\033[1;31m*\033[1;32m]\033[1;33m ➩ \033[1;32mBạn Đang Sử Dụng \033[1;31m: \033[1;36mTool Xworld Chạy Đua Tốc Độ
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
    
def fetch_data(url, headers, timeout=8):
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        else:
            return None
    except Exception:
        return None

def analyze_data(headers, asset_mode="BUILD"):
    url_recent_10 = f"https://api.sprintrun.win/sprint/recent_10_issues?asset={asset_mode}"
    url_recent_100 = f"https://api.sprintrun.win/sprint/recent_100_issues?asset={asset_mode}"
    data_10 = fetch_data(url_recent_10, headers)
    data_100 = fetch_data(url_recent_100, headers)

    if not data_10 or not data_100:
        return None, [], None, None, {}, [], {}

    issues_10 = []
    if isinstance(data_10, dict):
        if "data" in data_10 and isinstance(data_10["data"], dict):
            issues_10 = (
                data_10["data"].get("recent_10")
                or data_10["data"].get("issues")
                or data_10["data"].get("list")
                or []
            )
        else:
            issues_10 = (
                data_10.get("data")
                or data_10.get("issues")
                or []
            )
    elif isinstance(data_10, list):
        issues_10 = data_10

    if not isinstance(issues_10, list) or not issues_10:
        print(Colorate.Diagonal(Colors.red_to_white, "[♤] ➩ API Không Trả Về Dữ Liệu 10 Ván Gần Đây Hoặc Dữ Liệu Không Hợp Lệ !"))
        return None, [], None, None, {}, [], {}

    first_issue = issues_10[0]
    current_issue = first_issue.get("issue_id")
    champion_id = None
    if isinstance(first_issue.get("result"), list) and first_issue["result"]:
        champion_id = first_issue["result"][0]
    killed_room_id = str(champion_id) if champion_id is not None else None
    killed_room_name = room_names_map.get(killed_room_id, f"Phòng {killed_room_id}") if killed_room_id else "N/A"

    stats_100 = {}
    if isinstance(data_100, dict):
        if "data" in data_100 and isinstance(data_100["data"], dict):
            stats_100 = (
                data_100["data"].get("athlete_2_win_times")
                or data_100["data"].get("room_id_2_killed_times")
                or data_100["data"].get("stats")
                or {}
            )
        else:
            stats_100 = (
                data_100.get("athlete_2_win_times")
                or data_100.get("room_id_2_killed_times")
                or data_100.get("stats")
                or {}
            )
        if not isinstance(stats_100, dict):
            stats_100 = {}

    rates_100 = {}
    for rid in room_names_map.keys():
        try:
            rates_100[rid] = int(stats_100.get(str(rid), 0))
        except Exception:
            rates_100[rid] = 0

    sorted_rooms_win = sorted(rates_100.items(), key=lambda x: x[1], reverse=True)
    sorted_rooms_not_win = sorted(rates_100.items(), key=lambda x: x[1])

    return current_issue, [sorted_rooms_win, sorted_rooms_not_win], killed_room_id, killed_room_name, rates_100, issues_10, stats_100

def place_bet(headers, bet_group, coin, athlete_id, issue_id, bet_amount=1.0, bet_mode="not_champion"):
    url = "https://api.sprintrun.win/sprint/bet"
    payload = {
        "asset_type": coin,
        "issue_id": str(issue_id),
        "athlete_id": int(athlete_id),
        "bet_amount": float(bet_amount),
        "bet_mode": bet_mode,
        "bet_group": bet_group
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        try:
            data = r.json()
        except Exception:
            print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ HTTP {r.status_code} : {r.text}"))
            return False

        if data.get("code") in (0, 200):
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Đặt Cược Thành Công !"))
            return True
        else:
            print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Đặt Cược Thất Bại : {data}"))
    except Exception as e:
        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi Khi Đặt Cược : {e}"))
    return False    


def manual_place_bet(headers, issue_id, athlete_id, user_data=None, coin="BUILD", bet_amount=None):
    if user_data is None:
        user_data = {}

    if bet_amount is None:
        try:
            bet_amount = float(user_data.get("bet_amount", 1.0))
        except Exception:
            bet_amount = 1.0

    bet_mode = "champion" if user_data.get("choice_bet") == "winner" else "not_champion"
    bet_group = "winner" if bet_mode == "champion" else "not_winner"

    url = "https://api.sprintrun.win/sprint/bet"
    payload = {
        "asset_type": coin,
        "issue_id": str(issue_id),
        "athlete_id": int(athlete_id),
        "bet_amount": float(bet_amount),
        "bet_mode": bet_mode,
        "bet_group": bet_group
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        try:
            data = r.json()
        except Exception:
            print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ HTTP {r.status_code} : {r.text}"))
            return False

        if data.get("code") in (0, 200):
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Đặt Cược Tay Thành Công Kỳ {issue_id}"))
            return True
        else:
            print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Đặt Cược Tay Thất Bại : {data}"))
    except Exception as e:
        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi Khi Đặt Cược Tay : {e}"))
    return False

def show_wallet(headers, retries=3, delay=2, silent=False):
    url = "https://wallet.3games.io/api/wallet/user_asset"
    balances = {"USDT": 0.0, "WORLD": 0.0, "BUILD": 0.0}
    payload = {"user_id": headers.get("User-Id")}
    for attempt in range(retries):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=10)
            if r.status_code == 200:
                vi_data = r.json()
                if isinstance(vi_data, dict) and vi_data.get("code") == 0:
                    data = vi_data.get("data", {})
                    if isinstance(data, dict) and "user_asset" in data:
                        ua = data["user_asset"] or {}
                        for k in balances.keys():
                            v = ua.get(k)
                            try:
                                value = float(v) if v is not None else 0.0
                            except Exception:
                                value = 0.0
                            balances[k] = round(value, 2) if value >= 0.01 else 0.0
                    if not silent:
                        print("\033[1;97m════════════════════════════════════════════════")
                        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Số Dư Của Bạn :\n  - USDT : {balances['USDT']}\n  - World : {balances['WORLD']}\n  - Build : {balances['BUILD']}"))
                        print("\033[1;97m════════════════════════════════════════════════")
                    return balances["BUILD"]
        except Exception:
            pass
        if attempt < retries - 1:
            time.sleep(delay)
    return balances["BUILD"]

def load_config():
    if os.path.exists("Acc_Xworld.json"):
        with open("Acc_Xworld.json", "r") as f:
            return json.load(f)
    return None

def save_config(user_id, secret_key, login="login_v2", lang="vi-VN"):
    data = {
        "user_id": user_id,
        "user_login": login,
        "user_secret_key": secret_key,
        "lang": lang
    }
    with open("Acc_Xworld.json", "w") as f:
        json.dump(data, f, indent=4)

def print_game_data(issues_10, stats_100, bot_choice_name):
    print("\033[1;97m════════════════════════════════════════════════")
    for issue in issues_10:
        issue_id = issue.get("issue_id", "N/A")
        champion_id = None
        if isinstance(issue.get("result"), list) and issue["result"]:
            champion_id = issue["result"][0]
        champion_name = room_names_map.get(str(champion_id), f"Phòng {champion_id}")
        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Kì {issue_id} - Người Về Nhất : {champion_name}"))

    print("\033[1;97m════════════════════════════════════════════════")
    for rid, name in room_names_map.items():
        try:
            count = int(stats_100.get(str(rid), 0))
        except Exception:
            count = 0
        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ {name} Về Nhất {count} Lần"))
    
    print("\033[1;97m════════════════════════════════════════════════")
    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Chọn Đối Tượng Để Đặt Cược : {bot_choice_name or 'N/A'}"))

def calc_next_issue_id(current_issue):
    s = str(current_issue)
    tail = s.split("-")[-1]
    try:
        n = int(tail)
        return str(n + 1)
    except Exception:
        try:
            return str(int(s) + 1)
        except Exception:
            return s

def setting_xworld_cdtd():
    print("\033[1;97m════════════════════════════════════════════════")
    bet_amount = float(input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Nhập Số Build Cược Lúc Đầu : ")).strip())
    amount_to_increase_on_loss = float(input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Nhập Số Build Để Tăng Cược Sau Mỗi Lần Thua : ")).strip())
    win_limit = int(input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Thắng Bao Nhiêu Trận Thì Nghỉ : ")).strip())
    rest_games = int(input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Sau Khi Nghỉ Thì Nghỉ Được Bao Nhiêu Trận : ")).strip())
    win_stop = float(input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Thắng Tổng Cộng Bao Nhiêu Build Thì Dừng Tool (Enter Để Bỏ Qua Nếu Muốn Chạy Vô Hạn) : ")).strip() or "0")
    loss_stop = float(input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Thua Bao Nhiêu Build Thì Dừng Tool (Enter Để Bỏ Qua Nếu Muốn Chạy Vô Hạn) : ")).strip() or "0")
    proxy_input = input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Nhập Proxy, Enter Nếu Không Cần : ")).strip()
    proxies = {"http": f"http://{proxy_input}", "https": f"http://{proxy_input}"} if proxy_input else None
    
    config = {
        "bet_amount": bet_amount,
        "amount_to_increase_on_loss": amount_to_increase_on_loss,
        "win_limit": win_limit,
        "rest_games": rest_games,
        "win_stop": win_stop,
        "loss_stop": loss_stop,
        "proxy_input": proxy_input
    }
    with open('Setting_Xworld_CDTD.json', 'w') as file:
        json.dump(config, file)
    return config
    
if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    
    config = load_config()
    if config:
        user_id = config["user_id"]
        user_login = config.get("user_login", "login_v2")
        secret_key = config["user_secret_key"]
        lang = config.get("lang", "vi-VN")
        while True:
            acc_xworld_input = input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Dùng Acc Xworld Cũ Không ? (y/n) : ")).strip().lower()
            if acc_xworld_input == 'y':
                acc_xworld_enabled = True
                break
            elif acc_xworld_input == 'n':
                acc_xworld_enabled = False
                user_id = input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Nhập User Id Xworld Mới : ")).strip()
                secret_key = input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Nhập Secret Key Xworld Mới : ")).strip()
                user_login = "login_v2"
                lang = "vi-VN"
                save_config(user_id, secret_key, user_login, lang)
                break
            else:
                print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Vui Lòng Nhập (y/n) !"))
        if acc_xworld_enabled:
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Đã Dùng Lại Acc Xworld Thành Công !"))

    else:
        user_id = input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Nhập User Id Xworld : ")).strip()
        secret_key = input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Nhập Secret Key Xworld : ")).strip()
        user_login = "login_v2"
        lang = "vi-VN"
        save_config(user_id, secret_key, user_login, lang)
        
    headers = {
        "User-Id": user_id,
        "User-Login": user_login,
        "User-Secret-Key": secret_key,
        "Accept-Language": lang,
        "Content-Type": "application/json",
    }

    print("\033[1;97m════════════════════════════════════════════════")
    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Nhập Số (1) : Cược Quán Quân Chiến Thắng"))
    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Nhập Số (2) : Cược Người Thua Cuộc"))
    bet_mode_choice = input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Nhập Số : ")).strip()
    bet_mode = "champion" if bet_mode_choice == "1" else "not_champion"
    
    try:
        if os.path.exists('Setting_Xworld_CDTD.json'):
            with open('Setting_Xworld_CDTD.json', 'r') as file:
                config = json.load(file)
                bet_amount = config['bet_amount']
                amount_to_increase_on_loss = config['amount_to_increase_on_loss']
                win_limit = config['win_limit']
                rest_games = config['rest_games']
                win_stop = config['win_stop']
                loss_stop = config['loss_stop']
                proxy_input = config['proxy_input']
                print("\033[1;97m════════════════════════════════════════════════")
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Đã Thấy Cấu Hình Cũ"))
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Số Build Cược Lúc Đầu : {bet_amount} Build"))
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Số Build Tăng Cược Sau Mỗi Lần Thua : {amount_to_increase_on_loss if amount_to_increase_on_loss else 'Không Tăng'} Build"))
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Thắng {win_limit} Trận Thì Nghỉ {rest_games} Ván"))
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Thắng Tổng Cộng {win_stop if win_stop else 'Vô Hạn'} Build Thì Dừng Tool"))
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Thua Tổng Cộng {loss_stop if loss_stop else 'Vô Hạn'} Build Thì Dừng Tool"))
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Proxy : {proxy_input if proxy_input else 'Không Có'}"))
                print("\033[1;97m════════════════════════════════════════════════")      
                chon = input(Colorate.Diagonal(Colors.blue_to_white, f"[♤] ➩ Bạn Có Muốn Sử Dụng Cấu Hình Cũ Không ? (y/n) : "))
            if chon == 'y':
                bet_amount = config['bet_amount']
                amount_to_increase_on_loss = config['amount_to_increase_on_loss']
                win_limit = config['win_limit']
                rest_games = config['rest_games']
                win_stop = config['win_stop']
                loss_stop = config['loss_stop']
                proxy_input = config['proxy_input']
            else:
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Đã Xóa Cấu Hình Cũ"))
                print("\033[1;97m════════════════════════════════════════════════")
                os.remove('Setting_Xworld_CDTD.json')
                config = setting_xworld_cdtd()
                bet_amount = config['bet_amount']
                amount_to_increase_on_loss = config['amount_to_increase_on_loss']
                win_limit = config['win_limit']
                rest_games = config['rest_games']
                win_stop = config['win_stop']
                loss_stop = config['loss_stop']
                proxy_input = config['proxy_input']
        else:
            config = setting_xworld_cdtd()
            bet_amount = config['bet_amount']
            win_limit = config['win_limit']
            rest_games = config['rest_games']
            win_stop = config['win_stop']
            loss_stop = config['loss_stop']
            proxy_input = config['proxy_input']
       
    except ValueError:
        bet_amount = 30.0
        amount_to_increase_on_loss = 10.0
        win_limit = 0
        rest_games = 0
        win_stop = 0.0
        loss_stop = 0.0
        print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Nhập Sai, Dùng Setting Mặc Định !"))

    current_bet_amount = bet_amount
    total_wins, total_losses = 0, 0
    win_streak = 0
    total_profit = 0.0
    pending_issue, pending_target = None, None
    room_picked_count = {}
    locked_rooms = {}
    pick_pattern = [1, 2, 1, 3, 1]
    pick_index = 0
    skip_rounds = 0

    initial_balance = show_wallet(headers)
    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Số Dư Ban Đầu (Build) : {initial_balance}"))

    last_processed_issue = None

    try:
        while True:
            current_balance = show_wallet(headers, silent=True)
            current_issue, rankings, last_champion_id, last_champion_name, w100, issues_10, stats_100 = analyze_data(headers)

            if not current_issue:
                print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ API Thiếu Issue Hiện Tại, Thử Lại..."))
                time.sleep(3)
                continue

            champion_sorted, not_champion_sorted = rankings

            if last_processed_issue and str(last_processed_issue) != str(current_issue):
                time.sleep(3)
                new_balance = show_wallet(headers)
                try:
                    profit = (new_balance - current_balance) if (new_balance is not None and current_balance is not None) else 0.0
                except Exception:
                    profit = 0.0
                total_profit = new_balance - initial_balance if new_balance is not None else total_profit

                if bet_mode == "champion":
                    is_win = (str(pending_target) == str(last_champion_id))
                else:
                    is_win = (str(pending_target) != str(last_champion_id))

                if is_win:
                    total_wins += 1
                    win_streak += 1
                    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Kỳ {last_processed_issue} : Thắng ({total_profit:.2f} Build)"))
                    current_bet_amount = bet_amount
                    if win_limit > 0 and (total_wins % win_limit == 0):
                        print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Đã Thắng {total_wins} Ván, Tạm Nghỉ {rest_games} Ván..."))
                        skip_rounds = rest_games
                else:
                    total_losses += 1
                    win_streak = 0
                    print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Kỳ {last_processed_issue} : Thua ({total_profit:.2f} Build)"))
                    current_bet_amount = max(bet_amount, current_bet_amount + amount_to_increase_on_loss)

                if win_stop > 0 and total_profit >= win_stop:
                    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Đã Đạt {win_stop}/{total_profit:.2f} Build, Tự Động Thoát !"))
                    raise SystemExit(0)

                if loss_stop > 0 and total_profit <= -loss_stop:
                    print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Đã Lỗ {loss_stop}/{abs(total_profit):.2f} Build, Tự Động Thoát !"))
                    raise SystemExit(0)

                target_name = room_names_map.get(str(pending_target), f"Quán Quân {pending_target}")
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Bạn Chọn : {target_name} | Quán Quân : {last_champion_name}"))
                pending_issue, pending_target = None, None
                time.sleep(2)

            if not pending_issue:
                if skip_rounds > 0:
                    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Đang Nghỉ, Còn {skip_rounds} Ván..."))
                    skip_rounds -= 1
                    last_processed_issue = current_issue
                    time.sleep(4)
                    continue

            for rid in list(locked_rooms.keys()):
                locked_rooms[rid] = max(0, locked_rooms[rid] - 1)
                if locked_rooms[rid] <= 0:
                    locked_rooms.pop(rid, None)

            ranking = champion_sorted if bet_mode == "champion" else not_champion_sorted
            if not ranking:
                print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Không Có Dữ Liệu Xếp Hạng, Bỏ Qua Kỳ Này !"))
                last_processed_issue = current_issue
                time.sleep(2)
                continue

            target_rank = pick_pattern[pick_index]
            pick_index = (pick_index + 1) % len(pick_pattern)

            available = [(rid, val) for rid, val in ranking if locked_rooms.get(str(rid), 0) == 0]
            if not available:
                print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Tất Cả Lựa Chọn Đang Bị Khóa, Bỏ Qua Kỳ Này !"))
                last_processed_issue = current_issue
                time.sleep(2)
                continue

            if len(available) >= target_rank:
                best_id, _best_val = available[target_rank - 1]
            else:
                best_id, _best_val = available[0]

            best_name = room_names_map.get(str(best_id), f"Quán Quân {best_id}")
            room_picked_count[best_id] = room_picked_count.get(best_id, 0) + 1
            if room_picked_count[best_id] >= 2:
                locked_rooms[str(best_id)] = 1
                room_picked_count[best_id] = 0

            print_game_data(issues_10, stats_100, best_name)

            print("\033[1;97m════════════════════════════════════════════════")
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Thắng {total_wins} Trận/Thua {total_losses} Trận"))
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Tổng Số Trận Đã Chơi : ({total_wins + total_losses})"))
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Chuỗi Thắng : {win_streak}"))
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Lời/Lỗ : {total_profit:.2f} Build"))

            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Chờ Để Lấy Kỳ Mới..."))
            time.sleep(10)

            try:
                next_issue = calc_next_issue_id(current_issue)
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Cược Kỳ {next_issue} : {current_bet_amount} Build"))
                print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Chế Độ Cược : {'Quán Quân' if bet_mode=='champion' else 'Người Thua Cuộc'}"))

                bet_group = "winner" if bet_mode == "champion" else "not_winner"
                bet_mode_param = "champion" if bet_mode == "champion" else "not_champion"
                success = place_bet(headers, bet_group, "BUILD", int(best_id), next_issue, bet_amount=current_bet_amount, bet_mode=bet_mode_param)
                if success:
                    pending_issue, pending_target = next_issue, str(best_id)
                else:
                    print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Không Có Quán Quân Để Cược, Bỏ Qua Kỳ Này !"))
            except Exception as e:
                print(Colorate.Diagonal(Colors.red_to_white, f"[♤] ➩ Lỗi Khi Xác Định Kỳ Tiếp Theo : {e}"))
                success = False

            last_processed_issue = current_issue
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Quán Quân Kỳ {current_issue} : {last_champion_name}"))
            print(Colorate.Diagonal(Colors.green_to_white, f"[♤] ➩ Vì Tool Là Bot Tự Động Đặt Cược, Chọn Người Để Cược Nên Thua Thì Không Chịu Trách Nhiệm Nhé, Tỷ Lệ Thắng Khoảng Từ 75% - 90% !\n"))
            countdown = 1
            while True:
                time.sleep(1)
                print(f"\033[1;32m[♤] ➩ Đang Phân Tích ({countdown}s)", end="\r")
                countdown += 1
                new_issue, *_rest = analyze_data(headers)
                if new_issue and new_issue != current_issue:
                    print(Colorate.Diagonal(Colors.green_to_white, f"\n[♤] ➩ Có Kỳ Mới, Đang Xử Lý..."))
                    break
    except KeyboardInterrupt:
        print(Colorate.Diagonal(Colors.green_to_red, "[♤] ➩ Cảm Ơn Bạn Đã Sử Dụng Tool, Chúc Bạn May Mắn !"))
        sys.exit()