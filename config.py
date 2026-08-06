# config.py
import requests
import time

BOT_TOKEN = "8673180604:AAHGZzcQ9NLG_5tW1bhYjpelE3NZUaV9lPA"  # توکن ربات از BotFather
ADMIN_ID = 6662320148                  # آیدی عددی ادمین اصلی (با BotFather یا userinfobot بگیرید)

# --- آدرس ولت‌های ادمین ---
ADMIN_TON_WALLET = "UQDpnPtmh5I6nIdX4UB-7cb-fBS7lCniX3FrAqri_M83fpZu"
ADMIN_TRX_WALLET = "TL4szVoi4zpnaqwywESYJWcgZmgenayFEm"
ADMIN_USDT_WALLET = "0xEdaA7439d21e9b6E2E9f10880D464183E5D7B875"

# --- تنظیمات پیش‌فرض قابل تغییر توسط ادمین ---
REFERRAL_PERCENT = 0.10      # پورسانت ۱۰ درصدی زیرمجموعه‌گیری
DAILY_BONUS_AMOUNT = 20000    # میزان بونوس روزانه به تومان
MIN_BET_AMOUNT = 10000        # حداقل مبلغ شرط‌بندی

_last_update = 0
_cached_rates = {"USDT": 90000, "TRX": 2500, "TON": 280000}

def get_live_rates():
    global _last_update, _cached_rates
    current_time = time.time()
    if current_time - _last_update < 300 and _last_update != 0:
        return _cached_rates
    try:
        r = requests.get("https://api.nobitex.ir/v2/orderbook/USDTIRT", timeout=3).json()
        usdt_toman = float(r['bids'][0][0])
    except:
        usdt_toman = 90000

    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=TRXUSDT", timeout=3).json()
        trx_usd = float(r['price'])
    except:
        trx_usd = 0.28

    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=TONUSDT", timeout=3).json()
        ton_usd = float(r['price'])
    except:
        ton_usd = 3.1

    _cached_rates["USDT"] = int(usdt_toman)
    _cached_rates["TRX"] = int(trx_usd * usdt_toman)
    _cached_rates["TON"] = int(ton_usd * usdt_toman)
    _last_update = current_time
    return _cached_rates
