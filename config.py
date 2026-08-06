# config.py
import requests
import time

BOT_TOKEN = "8673180604:AAHGZzcQ9NLG_5tW1bhYjpelE3NZUaV9lPA"  # توکن ربات از BotFather
ADMIN_ID = 6662320148                  # آیدی عددی ادمین اصلی (با BotFather یا userinfobot بگیرید)

# --- آدرس ولت‌های ادمین ---
ADMIN_TON_WALLET = "UQDpnPtmh5I6nIdX4UB-7cb-fBS7lCniX3FrAqri_M83fpZu"
ADMIN_TRX_WALLET = "TL4szVoi4zpnaqwywESYJWcgZmgenayFEm"
ADMIN_USDT_WALLET = "0xEdaA7439d21e9b6E2E9f10880D464183E5D7B875"

import time
import requests

# --- تنظیمات پیش‌فرض قابل تغییر توسط ادمین ---
REFERRAL_PERCENT = 0.10      # پورسانت ۱۰ درصدی زیرمجموعه‌گیری
DAILY_BONUS_AMOUNT = 20000    # میزان بونوس روزانه به تومان
MIN_BET_AMOUNT = 10000        # حداقل مبلغ شرط‌بندی

_last_update = 0
_cached_rates = {"USDT": 90000, "TRX": 25000, "TON": 250000}

def get_live_rates():
    global _last_update, _cached_rates
    current_time = time.time()
    
    # به‌روزرسانی هر ۳۰ ثانیه یک‌بار
    if current_time - _last_update < 30 and _last_update != 0:
        return _cached_rates

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    pairs = {
        "USDT": "https://api.nobitex.ir/v2/orderbook/USDTIRT",
        "TRX": "https://api.nobitex.ir/v2/orderbook/TRXIRT",
        "TON": "https://api.nobitex.ir/v2/orderbook/TONIRT"
    }

    for coin, url in pairs.items():
        try:
            res = requests.get(url, headers=headers, timeout=3).json()
            if res.get('status') == 'ok' and 'bids' in res and len(res['bids']) > 0:
                # قیمت خرید زنده از فروشندگان به ریال (تقسیم بر ۱۰ برای تبدیل به تومان)
                price_toman = int(float(res['bids'][0][0]) / 10)
                _cached_rates[coin] = price_toman
        except Exception as e:
            print(f"Error fetching {coin}: {e}")

    _last_update = current_time
    return _cached_rates
