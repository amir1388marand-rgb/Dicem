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
    
    # به‌روزرسانی هر ۶۰ ثانیه یک‌بار
    if current_time - _last_update < 60 and _last_update != 0:
        return _cached_rates

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    # ۱. دریافت نرخ لحظه‌ای تتر (USDT) به تومان از نوبیتکس
    usdt_toman = _cached_rates["USDT"]
    try:
        res = requests.get("https://api.nobitex.ir/v2/orderbook/USDTIRT", headers=headers, timeout=5).json()
        if res.get('status') == 'ok' and 'bids' in res:
            usdt_toman = float(res['bids'][0][0]) / 10  # تبدیل ریال به تومان
    except Exception as e:
        print(f"Nobitex USDT Error: {e}")

    # ۲. دریافت نرخ دلار جهانی TRX و TON از CoinGecko
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=tron,the-open-network&vs_currencies=usd"
        res = requests.get(url, headers=headers, timeout=5).json()
        
        trx_usd = float(res['tron']['usd'])
        ton_usd = float(res['the-open-network']['usd'])

        # محاسبه قیمت تومانی بر اساس نرخ زنده تتر
        _cached_rates["USDT"] = int(usdt_toman)
        _cached_rates["TRX"] = int(trx_usd * usdt_toman)
        _cached_rates["TON"] = int(ton_usd * usdt_toman)
        _last_update = current_time

    except Exception as e:
        print(f"CoinGecko API Error: {e}")
        # در صورت خطا در CoinGecko، تلاش مجدد از طریق Binance API بدون تحریم
        try:
            trx_res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=TRXUSDT", headers=headers, timeout=3).json()
            ton_res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=TONUSDT", headers=headers, timeout=3).json()
            
            trx_usd = float(trx_res['price'])
            ton_usd = float(ton_res['price'])

            _cached_rates["USDT"] = int(usdt_toman)
            _cached_rates["TRX"] = int(trx_usd * usdt_toman)
            _cached_rates["TON"] = int(ton_usd * usdt_toman)
            _last_update = current_time
        except Exception as ex:
            print(f"Fallback Binance Error: {ex}")

    return _cached_rates
