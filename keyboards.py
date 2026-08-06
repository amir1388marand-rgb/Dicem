from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import config

def main_keyboard(user_id=None):
    buttons = [
        [KeyboardButton(text="🎲 شروع بازی"), KeyboardButton(text="👤 حساب کاربری")],
        [KeyboardButton(text="💳 شارژ حساب"), KeyboardButton(text="📤 برداشت وجه")],
        [KeyboardButton(text="👥 زیرمجموعه‌گیری"), KeyboardButton(text="🎁 بونوس روزانه")],
        [KeyboardButton(text="📜 تاریخچه بازی‌ها"), KeyboardButton(text="📊 آمار من")]
    ]
    if user_id == config.ADMIN_ID:
        buttons.append([KeyboardButton(text="👑 پنل مدیریت حرفه‌ای")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def admin_panel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 آمار کامل سیستم"), KeyboardButton(text="🔍 مدیریت کاربر")],
            [KeyboardButton(text="💳 شارژ/کسر موجودی"), KeyboardButton(text="🚫 مسدودسازی / رفع بن")],
            [KeyboardButton(text="⚙️ تنظیمات متغیر ربات"), KeyboardButton(text="📢 ارسال پیام همگانی")],
            [KeyboardButton(text="🔙 بازگشت به منوی اصلی")]
        ],
        resize_keyboard=True
    )

def admin_settings_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ تغییر درصد زیرمجموعه‌گیری", callback_data="set_ref_percent")],
        [InlineKeyboardButton(text="✏️ تغییر مبلغ بونوس روزانه", callback_data="set_daily_bonus")],
        [InlineKeyboardButton(text="✏️ تغییر حداقل مبلغ شرط", callback_data="set_min_bet")],
        [InlineKeyboardButton(text="❌ بستن پنل", callback_data="cancel_action")]
    ])

def game_modes_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="۱. عدد زوج (ضریب 1.95)", callback_data="mode_even"), InlineKeyboardButton(text="۲. عدد فرد (ضریب 1.95)", callback_data="mode_odd")],
        [InlineKeyboardButton(text="۳. کوچک‌تر از ۴ (1 تا 3) - ضریب 1.95", callback_data="mode_low")],
        [InlineKeyboardButton(text="۴. بزرگ‌تر از ۳ (4 تا 6) - ضریب 1.95", callback_data="mode_high")],
        [InlineKeyboardButton(text="۵. فقط عدد ۱ یا ۶ (ضریب 2.90)", callback_data="mode_1or6")],
        [InlineKeyboardButton(text="۶. فقط عدد ۳ یا ۴ (ضریب 2.90)", callback_data="mode_3or4")],
        [InlineKeyboardButton(text="۷. عدد ۱ یا ۲ (ضریب 2.90)", callback_data="mode_1or2")],
        [InlineKeyboardButton(text="۸. پیش‌بینی دقیق یک عدد (ضریب 5.50)", callback_data="mode_exact")],
        [InlineKeyboardButton(text="❌ انصراف", callback_data="cancel_action")]
    ])

def exact_number_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1️⃣", callback_data="num_1"), InlineKeyboardButton(text="2️⃣", callback_data="num_2"), InlineKeyboardButton(text="3️⃣", callback_data="num_3")],
        [InlineKeyboardButton(text="4️⃣", callback_data="num_4"), InlineKeyboardButton(text="5️⃣", callback_data="num_5"), InlineKeyboardButton(text="6️⃣", callback_data="num_6")],
        [InlineKeyboardButton(text="🔙 بازگشت به انتخاب حالت", callback_data="back_to_modes")]
    ])

def deposit_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 شارژ با تون کوین (TON)", callback_data="dep_TON")],
        [InlineKeyboardButton(text="🔴 شارژ با ترون (TRX)", callback_data="dep_TRX")],
        [InlineKeyboardButton(text="💵 شارژ با تتر (USDT)", callback_data="dep_USDT")],
        [InlineKeyboardButton(text="❌ انصراف", callback_data="cancel_action")]
    ])

def withdraw_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 برداشت کارت به کارت", callback_data="wth_CARD")],
        [InlineKeyboardButton(text="💎 برداشت تون کوین (TON)", callback_data="wth_TON")],
        [InlineKeyboardButton(text="🔴 برداشت ترون (TRX)", callback_data="wth_TRX")],
        [InlineKeyboardButton(text="💵 برداشت تتر (USDT)", callback_data="wth_USDT")],
        [InlineKeyboardButton(text="❌ انصراف", callback_data="cancel_action")]
    ])
