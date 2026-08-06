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
    
    # کش به مدت ۳ دقیقه (۱۸۰ ثانیه) - جهت جلوگیری از بن شدن IP
    if current_time - _last_update < 180 and _last_update != 0:
        return _cached_rates

    try:
        # دریافت یکجای آخرین قیمت تمام ارزها از API نوبیتکس
        response = requests.get("https://api.nobitex.ir/v2/orderbook/all", timeout=5).json()
        
        if response.get('status') == 'ok':
            # دریافت قیمت خرید تتر، ترون و تون به تومان (تبدیل ریال به تومان)
            usdt_toman = float(response['USDTIRT']['bids'][0][0]) / 10
            trx_toman = float(response['TRXIRT']['bids'][0][0]) / 10
            ton_toman = float(response['TONIRT']['bids'][0][0]) / 10

            _cached_rates["USDT"] = int(usdt_toman)
            _cached_rates["TRX"] = int(trx_toman)
            _cached_rates["TON"] = int(ton_toman)
            _last_update = current_time

    except Exception as e:
        print(f"خطا در دریافت نرخ ارز: {e}")
        # در صورت خطا یا قطع بودن اینترنت، از آخرین قیمت ثبت‌شده در حافظه استفاده می‌شود

    return _cached_rates
