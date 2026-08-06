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
    
    # آپدیت هر ۶۰ ثانیه یک‌بار
    if current_time - _last_update < 60 and _last_update != 0:
        return _cached_rates

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
    }

    # 1️⃣ تلاش برای دریافت از نوبیتکس
    try:
        url = "https://api.nobitex.ir/market/stats"
        res = requests.get(url, headers=headers, timeout=4).json()
        if res.get('status') == 'ok' and 'stats' in res:
            stats = res['stats']
            if 'usdt-irt' in stats and stats['usdt-irt'].get('latest'):
                _cached_rates["USDT"] = int(float(stats['usdt-irt']['latest']) / 10)
            if 'trx-irt' in stats and stats['trx-irt'].get('latest'):
                _cached_rates["TRX"] = int(float(stats['trx-irt']['latest']) / 10)
            if 'ton-irt' in stats and stats['ton-irt'].get('latest'):
                _cached_rates["TON"] = int(float(stats['ton-irt']['latest']) / 10)
            
            _last_update = current_time
            return _cached_rates
    except Exception as e:
        print(f"Nobitex API Error: {e}")

    # 2️⃣ اگر نوبیتکس خطا داد، دریافت از والکس (جایگزین پشتیبان)
    try:
        url = "https://api.wallex.ir/v1/currencies/stats"
        res = requests.get(url, headers=headers, timeout=4).json()
        if res.get('success') and 'result' in res:
            result = res['result']
            for item in result:
                if item['key'] == 'USDT':
                    _cached_rates["USDT"] = int(float(item['price']))
                elif item['key'] == 'TRX':
                    _cached_rates["TRX"] = int(float(item['price']))
                elif item['key'] == 'TON':
                    _cached_rates["TON"] = int(float(item['price']))

            _last_update = current_time
            return _cached_rates
    except Exception as e:
        print(f"Wallex API Error: {e}")

    return _cached_rates
