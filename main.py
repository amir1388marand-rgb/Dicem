import asyncio
from datetime import date
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import config
import database as db
import keyboards as kb

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# --- حالت‌های کاربری ---
class Form(StatesGroup):
    waiting_for_deposit_proof = State()
    waiting_for_deposit_amount = State()
    waiting_for_withdraw_amount = State()      # مرحله ۱: دریافت مبلغ برداشت
    waiting_for_withdraw_details = State()     # مرحله ۲: دریافت آدرس/شماره کارت

class GameState(StatesGroup):
    waiting_for_exact_num = State()
    waiting_for_bet = State()

# --- حالت‌های ادمین ---
class AdminState(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_user_search = State()
    waiting_for_balance_user = State()
    waiting_for_balance_amount = State()
    waiting_for_ban_id = State()
    waiting_for_unban_id = State()
    waiting_for_setting_value = State()

# --- شروع ---
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    args = message.text.split()
    referrer_id = 0
    if len(args) > 1 and args[1].isdigit():
        ref_candidate = int(args[1])
        if ref_candidate != message.from_user.id:
            referrer_id = ref_candidate

    user = db.get_user(message.from_user.id, message.from_user.username, referrer_id)
    if user and len(user) > 7 and user[7] == 1:
        await message.answer("❌ حساب کاربری شما مسدود است.")
        return

    await message.answer("به ربات حرفه‌ای بازی و شرط‌بندی خوش آمدید!", reply_markup=kb.main_keyboard(message.from_user.id))

# --- ورود به پنل مدیریت ---
@dp.message(F.text == "👑 پنل مدیریت حرفه‌ای")
@dp.message(Command("admin"))
async def open_admin_panel(message: types.Message):
    if message.from_user.id != config.ADMIN_ID: return
    await message.answer("👑 **پنل مدیریت حرفه‌ای ربات**", reply_markup=kb.admin_panel_keyboard(), parse_mode="Markdown")

@dp.message(F.text == "🔙 بازگشت به منوی اصلی")
async def back_to_main(message: types.Message):
    await message.answer("منوی اصلی:", reply_markup=kb.main_keyboard(message.from_user.id))

# --- بخش‌های ادمین ---
@dp.message(F.text == "📊 آمار کامل سیستم")
async def global_stats_cmd(message: types.Message):
    if message.from_user.id != config.ADMIN_ID: return
    t_users, t_bal, t_games, t_bets, t_wins = db.get_global_stats()
    profit = t_bets - t_wins
    await message.answer(
        f"📊 **آمار زنده سیستم:**\n\n"
        f"👥 کل کاربران: **{t_users:,} نفر**\n"
        f"💰 کل موجودی کاربران: **{t_bal:,.0f} تومان**\n"
        f"🎲 تعداد بازی‌ها: **{t_games:,} بار**\n"
        f"💵 مجموع مبالغ شرط: **{t_bets:,.0f} تومان**\n"
        f"🏆 بردهای پرداختی: **{t_wins:,.0f} تومان**\n"
        f"📈 سود خالص سیستم: **{profit:,.0f} تومان**",
        parse_mode="Markdown"
    )

@dp.message(F.text == "🔍 مدیریت کاربر")
async def search_user_start(message: types.Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID: return
    await message.answer("آیدی عددی کاربر را وارد کنید:")
    await state.set_state(AdminState.waiting_for_user_search)

@dp.message(AdminState.waiting_for_user_search)
async def process_user_search(message: types.Message, state: FSMContext):
    try:
        uid = int(message.text)
        user = db.get_user(uid)
        if not user:
            await message.answer("❌ کاربر یافت نشد.")
        else:
            ban_status = "🔴 مسدود" if len(user) > 7 and user[7] == 1 else "🟢 فعال"
            await message.answer(
                f"👤 **اطلاعات کاربر:**\n\n"
                f"🆔 شناسه: `{user[0]}`\n"
                f"👤 نام‌کاربری: @{user[1]}\n"
                f"💰 موجودی: **{user[2]:,} تومان**\n"
                f"👥 معرف: `{user[3]}`\n"
                f"🎲 بازی‌ها: {user[4]} | 🏆 بردها: {user[5]}\n"
                f"وضعیت: {ban_status}",
                parse_mode="Markdown"
            )
    except:
        await message.answer("❌ آیدی معتبر وارد کنید.")
    await state.clear()

@dp.message(F.text == "💳 شارژ/کسر موجودی")
async def balance_manage_start(message: types.Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID: return
    await message.answer("آیدی عددی کاربر مورد نظر را بفرستید:")
    await state.set_state(AdminState.waiting_for_balance_user)

@dp.message(AdminState.waiting_for_balance_user)
async def process_balance_user(message: types.Message, state: FSMContext):
    try:
        uid = int(message.text)
        await state.update_data(target_uid=uid)
        await message.answer("مبلغ را وارد کنید (مثال: `50000` برای شارژ یا `-50000` برای کسر):", parse_mode="Markdown")
        await state.set_state(AdminState.waiting_for_balance_amount)
    except:
        await message.answer("❌ آیدی معتبر وارد کنید.")
        await state.clear()

@dp.message(AdminState.waiting_for_balance_amount)
async def process_balance_amount(message: types.Message, state: FSMContext):
    try:
        amt = float(message.text)
        data = await state.get_data()
        target_uid = data['target_uid']
        db.update_balance(target_uid, amt)
        await message.answer(f"✅ حساب کاربر `{target_uid}` به میزان **{amt:,} تومان** تغییر یافت.", parse_mode="Markdown")
        await bot.send_message(target_uid, f"💳 حساب شما به میزان **{amt:,} تومان** توسط مدیریت تغییر یافت.")
    except:
        await message.answer("❌ مبلغ معتبر وارد کنید.")
    await state.clear()

@dp.message(F.text == "🚫 مسدودسازی / رفع بن")
async def ban_menu(message: types.Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID: return
    await message.answer("برای بن کردن کاربر آیدی عددی را ارسال کنید (جهت آن‌بن عبارت unban و سپس آیدی را بفرستید، مانند: `unban 123456`):")
    await state.set_state(AdminState.waiting_for_ban_id)

@dp.message(AdminState.waiting_for_ban_id)
async def process_ban_id(message: types.Message, state: FSMContext):
    txt = message.text.strip()
    if txt.startswith("unban"):
        try:
            uid = int(txt.split()[1])
            db.toggle_ban(uid, 0)
            await message.answer(f"✅ کاربر {uid} رفع مسدودیت شد.")
        except:
            await message.answer("❌ فرمت اشتباه است.")
    else:
        try:
            uid = int(txt)
            db.toggle_ban(uid, 1)
            await message.answer(f"🔴 کاربر {uid} بن شد.")
        except:
            await message.answer("❌ آیدی عددی معتبر وارد کنید.")
    await state.clear()

@dp.message(F.text == "⚙️ تنظیمات متغیر ربات")
async def settings_cmd(message: types.Message):
    if message.from_user.id != config.ADMIN_ID: return
    await message.answer(
        f"⚙️ **تنظیمات فعلی ربات:**\n\n"
        f"▫️ درصد زیرمجموعه‌گیری: **{config.REFERRAL_PERCENT * 100}%**\n"
        f"▫️ مبلغ بونوس روزانه: **{config.DAILY_BONUS_AMOUNT:,} تومان**\n"
        f"▫️ حداقل مبلغ شرط‌بندی: **{config.MIN_BET_AMOUNT:,} تومان**\n\n"
        f"گزینه مورد نظر را جهت تغییر انتخاب کنید:",
        reply_markup=kb.admin_settings_keyboard(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("set_"))
async def process_setting_change(callback: types.CallbackQuery, state: FSMContext):
    setting = callback.data
    await state.update_data(setting_key=setting)
    if setting == "set_ref_percent":
        await callback.message.answer("درصد جدید زیرمجموعه‌گیری را وارد کنید (مثلاً `15` برای ۱۵ درصد):")
    elif setting == "set_daily_bonus":
        await callback.message.answer("مبلغ جدید بونوس روزانه به تومان را وارد کنید:")
    elif setting == "set_min_bet":
        await callback.message.answer("حداقل مبلغ شرط‌بندی جدید را وارد کنید:")
    await state.set_state(AdminState.waiting_for_setting_value)

@dp.message(AdminState.waiting_for_setting_value)
async def apply_setting_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    key = data['setting_key']
    try:
        val = float(message.text)
        if key == "set_ref_percent":
            config.REFERRAL_PERCENT = val / 100.0
            await message.answer(f"✅ درصد پورسانت به {val}% تغییر یافت.")
        elif key == "set_daily_bonus":
            config.DAILY_BONUS_AMOUNT = val
            await message.answer(f"✅ بونوس روزانه به {val:,} تومان تغییر یافت.")
        elif key == "set_min_bet":
            config.MIN_BET_AMOUNT = val
            await message.answer(f"✅ حداقل شرط‌بندی به {val:,} تومان تغییر یافت.")
    except:
        await message.answer("❌ مقدار عددی معتبر وارد کنید.")
    await state.clear()

@dp.message(F.text == "📢 ارسال پیام همگانی")
async def broadcast_start(message: types.Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID: return
    await message.answer("پیام مورد نظر خود (متن، تصویر یا ویدیو) را ارسال کنید:")
    await state.set_state(AdminState.waiting_for_broadcast)

@dp.message(AdminState.waiting_for_broadcast)
async def process_broadcast(message: types.Message, state: FSMContext):
    user_ids = db.get_all_user_ids()
    sent, fail = 0, 0
    await message.answer("⏳ در حال ارسال...")
    for uid in user_ids:
        try:
            await bot.copy_message(chat_id=uid, from_chat_id=message.chat.id, message_id=message.message_id)
            sent += 1
            await asyncio.sleep(0.04)
        except:
            fail += 1
    await message.answer(f"✅ ارسال به پایان رسید.\nموفق: {sent} | ناموفق: {fail}")
    await state.clear()

# --- منوی کاربران ---
@dp.message(F.text == "👤 حساب کاربری")
async def profile_info(message: types.Message):
    user = db.get_user(message.from_user.id, message.from_user.username)
    ref_count = db.get_referrals_count(message.from_user.id)
    await message.answer(
        f"👤 **پروفایل کاربری**\n\n"
        f"🆔 شناسه: `{user[0]}`\n"
        f"💰 موجودی: **{user[2]:,} تومان**\n"
        f"🎲 تعداد بازی‌ها: {user[4]}\n"
        f"🏆 تعداد بردها: {user[5]}\n"
        f"👥 زیرمجموعه‌ها: {ref_count} نفر",
        parse_mode="Markdown"
    )

@dp.message(F.text == "👥 زیرمجموعه‌گیری")
async def referral_info(message: types.Message):
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
    ref_count = db.get_referrals_count(message.from_user.id)
    await message.answer(
        f"🤝 **سیستم کسب درآمد**\n\n"
        f"با دعوت دوستان خود، **{int(config.REFERRAL_PERCENT * 100)}٪ از هر شارژ آن‌ها** به شما تعلق می‌گیرد!\n\n"
        f"👥 زیرمجموعه‌های شما: **{ref_count} نفر**\n"
        f"🔗 لینک اختصاصی شما:\n`{ref_link}`",
        parse_mode="Markdown"
    )

@dp.message(F.text == "🎁 بونوس روزانه")
async def daily_bonus(message: types.Message):
    user = db.get_user(message.from_user.id, message.from_user.username)
    today_str = str(date.today())
    if user[6] == today_str:
        await message.answer("❌ شما هدیه امروز را دریافت کرده‌اید. فردا دوباره سر بزنید!")
    else:
        db.update_balance(message.from_user.id, config.DAILY_BONUS_AMOUNT)
        db.update_last_bonus(message.from_user.id, today_str)
        await message.answer(f"🎉 مبلغ **{config.DAILY_BONUS_AMOUNT:,} تومان** بونوس روزانه واریز شد!")

@dp.message(F.text == "📜 تاریخچه بازی‌ها")
async def show_history(message: types.Message):
    history = db.get_recent_games(message.from_user.id)
    if not history:
        await message.answer("هنوز هیچ بازی ثبت نشده است.")
        return
    text = "📜 **۱۰ بازی اخیر شما:**\n\n"
    for h in history:
        status = "✅ برد" if h[3] == 1 else "❌ باخت"
        text += f"▪️ حالت: {h[0]} | مبلغ: {h[1]:,} | تاس: {h[2]} | {status} ({h[4]:,} تومان)\n"
    await message.answer(text, parse_mode="Markdown")

# --- سیستم بازی ---
@dp.message(F.text == "🎲 شروع بازی")
async def start_game(message: types.Message, state: FSMContext):
    user = db.get_user(message.from_user.id, message.from_user.username)
    if user[2] < config.MIN_BET_AMOUNT:
        await message.answer(f"❌ حداقل موجودی جهت بازی **{config.MIN_BET_AMOUNT:,} تومان** است.", parse_mode="Markdown")
        return
    await message.answer("لطفاً حالت بازی را انتخاب کنید:", reply_markup=kb.game_modes_keyboard())

@dp.callback_query(F.data.startswith("mode_"))
async def select_mode(callback: types.CallbackQuery, state: FSMContext):
    mode = callback.data.split("_")[1]
    await state.update_data(game_mode=mode)
    if mode == "exact":
        await callback.message.answer("عدد مورد نظر خود را انتخاب کنید (۱ تا ۶):", reply_markup=kb.exact_number_keyboard())
        await state.set_state(GameState.waiting_for_exact_num)
    else:
        await callback.message.answer("مبلغ شرط‌بندی را به تومان وارد کنید:")
        await state.set_state(GameState.waiting_for_bet)

@dp.callback_query(F.data.startswith("num_"))
async def select_exact_num(callback: types.CallbackQuery, state: FSMContext):
    num = int(callback.data.split("_")[1])
    await state.update_data(exact_num=num)
    await callback.message.answer(f"عدد انتخاب شده: {num}\nحالا مبلغ شرط‌بندی را وارد کنید:")
    await state.set_state(GameState.waiting_for_bet)

@dp.message(GameState.waiting_for_bet)
async def process_bet(message: types.Message, state: FSMContext):
    try:
        bet_amount = float(message.text)
        user = db.get_user(message.from_user.id, message.from_user.username)
        if bet_amount < config.MIN_BET_AMOUNT or bet_amount > user[2]:
            await message.answer(f"❌ مبلغ نامعتبر است یا کمتر از حداقل شرط ({config.MIN_BET_AMOUNT:,}) می‌باشد.")
            return

        data = await state.get_data()
        mode = data['game_mode']
        exact_num = data.get('exact_num', None)

        db.update_balance(message.from_user.id, -bet_amount)
        bot_dice = await message.answer_dice(emoji="🎲")
        await asyncio.sleep(3.5)
        dice_val = bot_dice.dice.value

        is_win, multiplier = False, 0
        if mode == "even" and dice_val % 2 == 0: is_win, multiplier = True, 1.95
        elif mode == "odd" and dice_val % 2 != 0: is_win, multiplier = True, 1.95
        elif mode == "low" and dice_val in [1, 2, 3]: is_win, multiplier = True, 1.95
        elif mode == "high" and dice_val in [4, 5, 6]: is_win, multiplier = True, 1.95
        elif mode == "1or6" and dice_val in [1, 6]: is_win, multiplier = True, 2.90
        elif mode == "3or4" and dice_val in [3, 4]: is_win, multiplier = True, 2.90
        elif mode == "1or2" and dice_val in [1, 2]: is_win, multiplier = True, 2.90
        elif mode == "exact" and dice_val == exact_num: is_win, multiplier = True, 5.50

        win_amount = bet_amount * multiplier if is_win else 0
        if is_win:
            db.update_balance(message.from_user.id, win_amount)
            db.update_stats(message.from_user.id, is_win=True)
            await message.answer(f"🎉 تبریک! تاس {dice_val} آمد و شما برنده **{win_amount:,} تومان** شدید!", parse_mode="Markdown")
        else:
            db.update_stats(message.from_user.id, is_win=False)
            await message.answer(f"باختید! تاس {dice_val} آمد.")

        db.log_game(message.from_user.id, mode, bet_amount, dice_val, is_win, win_amount)
        await state.clear()
    except:
        await message.answer("❌ مبلغ را به عدد لاتین وارد کنید.")

# --- واریز و برداشت ---
@dp.message(F.text == "💳 شارژ حساب")
async def deposit_start(message: types.Message):
    await message.answer("ارز مورد نظر جهت شارژ را انتخاب کنید:", reply_markup=kb.deposit_keyboard())

@dp.callback_query(F.data.startswith("dep_"))
async def process_dep(callback: types.CallbackQuery, state: FSMContext):
    currency = callback.data.split("_")[1]
    rates = config.get_live_rates()
    rate = rates[currency]
    wallet = getattr(config, f"ADMIN_{currency}_WALLET")
    await state.update_data(currency=currency, rate=rate)
    await callback.message.answer(
        f"برای شارژ با **{currency}**، آدرس ولت:\n`{wallet}`\n\n"
        f"نرخ زنده: ۱ {currency} = {rate:,} تومان\n\n"
        f"ابتدا مبلغ واریزی خود به تومان را بفرستید:", parse_mode="Markdown"
    )
    await state.set_state(Form.waiting_for_deposit_amount)

@dp.message(Form.waiting_for_deposit_amount)
async def process_dep_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(dep_amount=amount)
        await message.answer("اکنون عکس رسید یا Hash تراکنش را بفرستید:")
        await state.set_state(Form.waiting_for_deposit_proof)
    except:
        await message.answer("❌ مبلغ معتبر وارد کنید.")

@dp.message(Form.waiting_for_deposit_proof)
async def process_proof(message: types.Message, state: FSMContext):
    data = await state.get_data()
    trans_id = db.add_transaction(message.from_user.id, "Deposit", data['dep_amount'], data['currency'])
    
    markup = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(text="✅ تایید شارژ", callback_data=f"app_{trans_id}_{message.from_user.id}_{data['dep_amount']}"),
        types.InlineKeyboardButton(text="❌ رد", callback_data=f"rej_{trans_id}_{message.from_user.id}")
    ]])
    
    caption = f"📩 **درخواست شارژ جدید** #{trans_id}\n👤 کاربر: `{message.from_user.id}`\n💵 مبلغ: **{data['dep_amount']:,} تومان** ({data['currency']})"
    if message.photo:
        await bot.send_photo(config.ADMIN_ID, message.photo[-1].file_id, caption=caption, reply_markup=markup, parse_mode="Markdown")
    else:
        await bot.send_message(config.ADMIN_ID, f"{caption}\nمتن: {message.text}", reply_markup=markup, parse_mode="Markdown")
        
    await message.answer("✅ درخواست شارژ ثبت شد و منتظر تایید مدیریت است.")
    await state.clear()

@dp.callback_query(F.data.startswith("app_"))
async def approve_dep(callback: types.CallbackQuery):
    _, trans_id, target_uid, amount = callback.data.split("_")
    target_uid = int(target_uid)
    amount = float(amount)
    
    db.update_transaction_status(trans_id, "approved")
    db.update_balance(target_uid, amount)
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"✅ شارژ تراکنش #{trans_id} تایید شد.")
    await bot.send_message(target_uid, f"🎉 درخواست شارژ شما تایید شد! مبلغ **{amount:,} تومان** به حسابتان اضافه گردید.")
    
    # واریز پورسانت زیرمجموعه‌گیری
    user = db.get_user(target_uid)
    if user and user[3] > 0:
        comm = amount * config.REFERRAL_PERCENT
        db.update_balance(user[3], comm)
        await bot.send_message(user[3], f"🎁 مبلغ **{comm:,} تومان** پورسانت بابت شارژ زیرمجموعه‌تان واریز شد!")

@dp.callback_query(F.data.startswith("rej_"))
async def reject_dep(callback: types.CallbackQuery):
    _, trans_id, target_uid = callback.data.split("_")
    db.update_transaction_status(trans_id, "rejected")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"❌ تراکنش #{trans_id} رد شد.")
    await bot.send_message(int(target_uid), "❌ درخواست شارژ شما رد شد. در صورت نیاز با پشتیبانی تماس بگیرید.")

# --- بخش برداشت وجه (آپدیت شده و حرفه‌ای) ---
MIN_WITHDRAW_AMOUNT = 1000000  # حداقل برداشت: ۱ میلیون تومان

@dp.message(F.text == "📤 برداشت وجه")
async def withdraw_start(message: types.Message):
    user = db.get_user(message.from_user.id, message.from_user.username)
    if user[2] < MIN_WITHDRAW_AMOUNT:
        await message.answer(
            f"❌ **امکان برداشت وجود ندارد.**\n\n"
            f"💵 حداقل مبلغ جهت برداشت **{MIN_WITHDRAW_AMOUNT:,} تومان** است.\n"
            f"💰 موجودی فعلی شما: **{user[2]:,} تومان**",
            parse_mode="Markdown"
        )
        return

    await message.answer(
        f"💰 موجودی فعلی: **{user[2]:,} تومان**\n\n"
        f"لطفاً روش برداشت را انتخاب کنید:", 
        reply_markup=kb.withdraw_keyboard(), 
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("wth_"))
async def process_wth_method(callback: types.CallbackQuery, state: FSMContext):
    method = callback.data.split("_")[1]
    await state.update_data(wth_method=method)
    
    await callback.message.answer(
        f"💵 لطفاً **مبلغ برداشت** را به تومان وارد کنید:\n"
        f"⚠️ حداقل مبلغ برداشت: **{MIN_WITHDRAW_AMOUNT:,} تومان**",
        parse_mode="Markdown"
    )
    await state.set_state(Form.waiting_for_withdraw_amount)

@dp.message(Form.waiting_for_withdraw_amount)
async def process_wth_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
        user = db.get_user(message.from_user.id, message.from_user.username)

        if amount < MIN_WITHDRAW_AMOUNT:
            await message.answer(f"❌ مبلغ وارد شده کمتر از حداقل برداشت ({MIN_WITHDRAW_AMOUNT:,} تومان) است. دوباره وارد کنید:")
            return

        if amount > user[2]:
            await message.answer(f"❌ مبلغ وارد شده بیشتر از موجودی شما ({user[2]:,} تومان) است. دوباره وارد کنید:")
            return

        await state.update_data(wth_amount=amount)

        data = await state.get_data()
        method = data['wth_method']

        if method.lower() in ["card", "کارت"]:
            prompt_text = "💳 لطفاً **شماره کارت ۱۶ رقمی** خود را ارسال کنید:"
        else:
            prompt_text = "🌐 لطفاً **آدرس کیف پول** خود را ارسال کنید:"

        await message.answer(prompt_text, parse_mode="Markdown")
        await state.set_state(Form.waiting_for_withdraw_details)

    except ValueError:
        await message.answer("❌ لطفاً مبلغ را به صورت عددی و به انگلیسی وارد کنید.")

@dp.message(Form.waiting_for_withdraw_details)
async def process_wth_details(message: types.Message, state: FSMContext):
    details = message.text.strip()
    data = await state.get_data()
    wth_amount = data['wth_amount']
    wth_method = data['wth_method']

    # ثبت تراکنش در حالت معلق (کاهش موجودی تا تایید ادمین انجام نمی‌شود)
    trans_id = db.add_transaction(message.from_user.id, f"Withdraw_{wth_method}", wth_amount, wth_method)

    # ایجاد دکمه‌های تایید (تسویه) یا رد (لغو) برای ادمین
    markup = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(text="✅ تسویه شد", callback_data=f"wthapp_{trans_id}_{message.from_user.id}_{wth_amount}"),
        types.InlineKeyboardButton(text="❌ لغو درخواست", callback_data=f"wthrej_{trans_id}_{message.from_user.id}_{wth_amount}")
    ]])

    admin_msg = (
        f"🚨 **درخواست برداشت جدید** #{trans_id}\n\n"
        f"👤 کاربر: @{message.from_user.username} (`{message.from_user.id}`)\n"
        f"💳 روش برداشت: **{wth_method}**\n"
        f"💵 مبلغ درخواست: **{wth_amount:,.0f} تومان**\n"
        f"📌 شماره کارت/آدرس: `{details}`"
    )

    await bot.send_message(config.ADMIN_ID, admin_msg, reply_markup=markup, parse_mode="Markdown")
    await message.answer("✅ درخواست برداشت شما ثبت شد.\n⏳ پس از بررسی و تایید مدیریت، مبلغ واریز و تسویه خواهد شد.")
    await state.clear()

# --- کلیک ادمین روی تسویه شد ---
@dp.callback_query(F.data.startswith("wthapp_"))
async def approve_withdraw(callback: types.CallbackQuery):
    _, trans_id, target_uid, amount = callback.data.split("_")
    target_uid = int(target_uid)
    amount = float(amount)

    # کسر موجودی کاربر پس از تسویه نهایی
    db.update_balance(target_uid, -amount)
    db.update_transaction_status(trans_id, "approved")

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"✅ درخواست برداشت #{trans_id} تسویه شد و مبلغ **{amount:,.0f} تومان** از موجودی کاربر کسر گردید.")
    await bot.send_message(target_uid, f"✅ درخواست برداشت شما به مبلغ **{amount:,.0f} تومان** تسویه و به حساب شما واریز شد.")

# --- کلیک ادمین روی لغو درخواست ---
@dp.callback_query(F.data.startswith("wthrej_"))
async def reject_withdraw(callback: types.CallbackQuery):
    _, trans_id, target_uid, amount = callback.data.split("_")
    target_uid = int(target_uid)
    amount = float(amount)

    # موجودی کسر نمی‌شود زیرا قبلا کم نشده بود
    db.update_transaction_status(trans_id, "rejected")

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"❌ درخواست برداشت #{trans_id} لغو شد.")
    await bot.send_message(target_uid, f"❌ درخواست برداشت شما به مبلغ **{amount:,.0f} تومان** توسط مدیریت لغو شد و موجودی شما بدون تغییر باقی ماند.")

async def main():
    db.init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
