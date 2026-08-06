import time
import requests

# --- اطلاعات پایه ربات ---
BOT_TOKEN = "8673180604:AAHGZzcQ9NLG_5tW1bhYjpelE3NZUaV9lPA"  # توکن ربات
ADMIN_ID = 6662320148                  # آیدی عددی ادمین اصلی

# --- آدرس ولت‌های ادمین ---
ADMIN_TON_WALLET = "UQDpnPtmh5I6nIdX4UB-7cb-fBS7lCniX3FrAqri_M83fpZu"
ADMIN_TRX_WALLET = "TL4szVoi4zpnaqwywESYJWcgZmgenayFEm"
ADMIN_USDT_WALLET = "0xEdaA7439d21e9b6E2E9f10880D464183E5D7B875"

# --- تنظیمات پیش‌فرض قابل تغییر توسط ادمین ---
REFERRAL_PERCENT = 0.10      # پورسانت ۱۰ درصدی زیرمجموعه‌گیری
DAILY_BONUS_AMOUNT = 20000    # میزان بونوس روزانه به تومان
MIN_BET_AMOUNT = 10000        # حداقل مبلغ شرط‌بندی به تومان

_last_update = 0
_cached_rates = {"USDT": 188000, "TRX": 25000, "TON": 250000}

def fetch_nobitex():
    """صرافی ۱: نوبیتکس"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    rates = {}
    pairs = {
        "USDT": "https://api.nobitex.ir/v2/orderbook/USDTIRT",
        "TRX": "https://api.nobitex.ir/v2/orderbook/TRXIRT",
        "TON": "https://api.nobitex.ir/v2/orderbook/TONIRT"
    }
    for coin, url in pairs.items():
        res = requests.get(url, headers=headers, timeout=3).json()
        if res.get('status') == 'ok' and 'bids' in res and len(res['bids']) > 0:
            # تبدیل ریال نوبیتکس به تومان
            rates[coin] = int(float(res['bids'][0][0]) / 10)
    
    if len(rates) == 3:
        return rates
    raise Exception("Nobitex data incomplete")

def fetch_wallex():
    """صرافی ۲: والکس"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get("https://api.wallex.ir/v1/currencies/stats", headers=headers, timeout=3).json()
    rates = {}
    if res.get('success') and 'result' in res:
        for item in res['result']:
            if item['key'] in ["USDT", "TRX", "TON"]:
                rates[item['key']] = int(float(item['price']))
    if len(rates) == 3:
        return rates
    raise Exception("Wallex data incomplete")

def fetch_tabdeal():
    """صرافی ۳: تبدیل"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get("https://api.tabdeal.org/r/plots/market_information", headers=headers, timeout=3).json()
    rates = {}
    mapping = {"USDT_IRT": "USDT", "TRX_IRT": "TRX", "TON_IRT": "TON"}
    if isinstance(res, list):
        for item in res:
            symbol = item.get("symbol")
            if symbol in mapping:
                rates[mapping[symbol]] = int(float(item['last_price']))
    if len(rates) == 3:
        return rates
    raise Exception("Tabdeal data incomplete")

def fetch_bitpin():
    """صرافی ۴: بیت‌پین"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get("https://api.bitpin.ir/v1/mkt/markets/", headers=headers, timeout=3).json()
    rates = {}
    mapping = {"USDT_IRT": "USDT", "TRX_IRT": "TRX", "TON_IRT": "TON"}
    
    items_list = res if isinstance(res, list) else res.get('results', [])
    for item in items_list:
        code = item.get("code")
        if code in mapping and item.get("price"):
            rates[mapping[code]] = int(float(item['price']))
            
    if len(rates) == 3:
        return rates
    raise Exception("Bitpin data incomplete")

def fetch_global_fallback():
    """صرافی ۵ (پشتیبان نهایی): ترکیب نرخ دلار تتر و CoinGecko جهانی"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    usdt_price = _cached_rates.get("USDT", 90000)
    try:
        r = requests.get("https://api.nobitex.ir/v2/orderbook/USDTIRT", headers=headers, timeout=2).json()
        usdt_price = int(float(r['bids'][0][0]) / 10)
    except Exception:
        pass

    cg_res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=tron,the-open-network&vs_currencies=usd", headers=headers, timeout=3).json()
    trx_usd = float(cg_res['tron']['usd'])
    ton_usd = float(cg_res['the-open-network']['usd'])

    return {
        "USDT": usdt_price,
        "TRX": int(trx_usd * usdt_price),
        "TON": int(ton_usd * usdt_price)
    }

def get_live_rates():
    global _last_update, _cached_rates
    current_time = time.time()
    
    # به‌روزرسانی cache هر ۴۵ ثانیه یک‌بار
    if current_time - _last_update < 45 and _last_update != 0:
        return _cached_rates

    providers = [
        ("Nobitex", fetch_nobitex),
        ("Wallex", fetch_wallex),
        ("Tabdeal", fetch_tabdeal),
        ("Bitpin", fetch_bitpin),
        ("Global Fallback", fetch_global_fallback)
    ]

    for name, provider_func in providers:
        try:
            new_rates = provider_func()
            if new_rates and all(v > 0 for v in new_rates.values()):
                _cached_rates = new_rates
                _last_update = current_time
                print(f"✅ نرخ‌ها با موفقیت از {name} دریافت شدند: {_cached_rates}")
                return _cached_rates
        except Exception as e:
            print(f"⚠️ تامین‌کننده {name} ناموفق بود: {e}")
            continue

    return _cached_rates
    
    if len(rates) == 3:
        return rates
    raise Exception("Nobitex data incomplete")

def fetch_wallex():
    """صرافی ۲: والکس"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get("https://api.wallex.ir/v1/currencies/stats", headers=headers, timeout=3).json()
    rates = {}
    if res.get('success') and 'result' in res:
        for item in res['result']:
            if item['key'] in ["USDT", "TRX", "TON"]:
                rates[item['key']] = int(float(item['price']))
    if len(rates) == 3:
        return rates
    raise Exception("Wallex data incomplete")

def fetch_tabdeal():
    """صرافی ۳: تبدیل"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get("https://api.tabdeal.org/r/plots/market_information", headers=headers, timeout=3).json()
    rates = {}
    # تبدیل جفت‌ارزها
    mapping = {"USDT_IRT": "USDT", "TRX_IRT": "TRX", "TON_IRT": "TON"}
    if isinstance(res, list):
        for item in res:
            symbol = item.get("symbol")
            if symbol in mapping:
                rates[mapping[symbol]] = int(float(item['last_price']))
    if len(rates) == 3:
        return rates
    raise Exception("Tabdeal data incomplete")

def fetch_bitpin():
    """صرافی ۴: بیت‌پین"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get("https://api.bitpin.ir/v1/mkt/markets/", headers=headers, timeout=3).json()
    rates = {}
    mapping = {"USDT_IRT": "USDT", "TRX_IRT": "TRX", "TON_IRT": "TON"}
    if isinstance(res, list):
        for item in res:
            code = item.get("code")
            if code in mapping and item.get("price"):
                rates[mapping[code]] = int(float(item['price']))
    elif isinstance(res, dict) and 'results' in res:
        for item in res['results']:
            code = item.get("code")
            if code in mapping and item.get("price"):
                rates[mapping[code]] = int(float(item['price']))
    if len(rates) == 3:
        return rates
    raise Exception("Bitpin data incomplete")

def fetch_global_fallback():
    """صرافی ۵ (پشتیبان نهایی): ترکیب نرخ دلار تتر و CoinGecko جهانی"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    # گرفتن نرخ تتر
    usdt_price = _cached_rates.get("USDT", 90000)
    try:
        r = requests.get("https://api.nobitex.ir/v2/orderbook/USDTIRT", headers=headers, timeout=2).json()
        usdt_price = int(float(r['bids'][0][0]) / 10)
    except:
        pass

    # گرفتن نرخ ارزها به دلار
    cg_res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=tron,the-open-network&vs_currencies=usd", headers=headers, timeout=3).json()
    trx_usd = float(cg_res['tron']['usd'])
    ton_usd = float(cg_res['the-open-network']['usd'])

    return {
        "USDT": usdt_price,
        "TRX": int(trx_usd * usdt_price),
        "TON": int(ton_usd * usdt_price)
    }

def get_live_rates():
    global _last_update, _cached_rates
    current_time = time.time()
    
    # به‌روزرسانی هر ۴۵ ثانیه یک‌بار
    if current_time - _last_update < 45 and _last_update != 0:
        return _cached_rates

    providers = [
        ("Nobitex", fetch_nobitex),
        ("Wallex", fetch_wallex),
        ("Tabdeal", fetch_tabdeal),
        ("Bitpin", fetch_bitpin),
        ("Global Fallback", fetch_global_fallback)
    ]

    for name, provider_func in providers:
        try:
            new_rates = provider_func()
            if new_rates and all(v > 0 for v in new_rates.values()):
                _cached_rates = new_rates
                _last_update = current_time
                print(f"✅ نرخ‌ها با موفقیت از {name} دریافت شدند: {_cached_rates}")
                return _cached_rates
        except Exception as e:
            print(f"⚠️ تامین‌کننده {name} ناموفق بود: {e}")
            continue

    # اگر همه صرافی‌ها قطع بودند، از آخرین قیمت ذخیره‌شده در حافظه استفاده کن
    return _cached_rates
