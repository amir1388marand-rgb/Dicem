# database.py
import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("dice_bot.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance REAL DEFAULT 0,
            referrer_id INTEGER DEFAULT 0,
            bets_count INTEGER DEFAULT 0,
            wins_count INTEGER DEFAULT 0,
            last_bonus TEXT,
            is_banned INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            amount REAL,
            currency TEXT,
            status TEXT DEFAULT 'pending',
            date TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            bet_type TEXT,
            bet_amount REAL,
            dice_result INTEGER,
            is_win INTEGER,
            win_amount REAL,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_user(user_id, username=None, referrer_id=0):
    conn = sqlite3.connect("dice_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user and username is not None:
        cursor.execute("INSERT INTO users (user_id, username, referrer_id) VALUES (?, ?, ?)", (user_id, username, referrer_id))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
    conn.close()
    return user

def update_balance(user_id, amount):
    conn = sqlite3.connect("dice_bot.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def update_stats(user_id, is_win):
    conn = sqlite3.connect("dice_bot.db")
    cursor = conn.cursor()
    if is_win:
        cursor.execute("UPDATE users SET bets_count = bets_count + 1, wins_count = wins_count + 1 WHERE user_id = ?", (user_id,))
    else:
        cursor.execute("UPDATE users SET bets_count = bets_count + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def add_transaction(user_id, trans_type, amount, currency):
    conn = sqlite3.connect("dice_bot.db")
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("INSERT INTO transactions (user_id, type, amount, currency, date) VALUES (?, ?, ?, ?, ?)",
                   (user_id, trans_type, amount, currency, now))
    trans_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return trans_id

def update_transaction_status(trans_id, status):
    conn = sqlite3.connect("dice_bot.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE transactions SET status = ? WHERE id = ?", (status, trans_id))
    conn.commit()
    conn.close()

def log_game(user_id, bet_type, bet_amount, dice_result, is_win, win_amount):
    conn = sqlite3.connect("dice_bot.db")
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute('''
        INSERT INTO game_history (user_id, bet_type, bet_amount, dice_result, is_win, win_amount, date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, bet_type, bet_amount, dice_result, 1 if is_win else 0, win_amount, now))
    conn.commit()
    conn.close()

def get_referrals_count(user_id):
    conn = sqlite3.connect("dice_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE referrer_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_recent_games(user_id, limit=10):
    conn = sqlite3.connect("dice_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT bet_type, bet_amount, dice_result, is_win, win_amount, date FROM game_history WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
    history = cursor.fetchall()
    conn.close()
    return history

def update_last_bonus(user_id, bonus_date_str):
    conn = sqlite3.connect("dice_bot.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET last_bonus = ? WHERE user_id = ?", (bonus_date_str, user_id))
    conn.commit()
    conn.close()

# --- توابع ویژه ادمین ---
def toggle_ban(user_id, status):
    conn = sqlite3.connect("dice_bot.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_banned = ? WHERE user_id = ?", (status, user_id))
    conn.commit()
    conn.close()

def get_global_stats():
    conn = sqlite3.connect("dice_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(balance) FROM users")
    total_balance = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*), SUM(bet_amount), SUM(win_amount) FROM game_history")
    games_data = cursor.fetchone()
    total_games = games_data[0] or 0
    total_bets_sum = games_data[1] or 0
    total_wins_sum = games_data[2] or 0
    conn.close()
    return total_users, total_balance, total_games, total_bets_sum, total_wins_sum

def get_all_user_ids():
    conn = sqlite3.connect("dice_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE is_banned = 0")
    users = cursor.fetchall()
    conn.close()
    return [u[0] for u in users]
