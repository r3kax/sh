import os
import zipfile

# Имя ZIP-файла
zip_name = "sho.zip"

# Структура файлов
files_content = {
    ".python-version": "3.11.9",
    "runtime.txt": "python-3.11.9",
    "requirements.txt": """aiogram==2.25.1
aiohttp==3.8.6
fastapi==0.110.0
uvicorn==0.29.0
pydantic==2.12.5""",
    "config.py": """BOT_TOKEN = "ВАШ_TELEGRAM_BOT_TOKEN"
BOT_ADMIN_ID = 123456789
CRYPTO_TOKEN = "ВАШ_CRYPTO_BOT_TOKEN"
APP_URL = "https://ваш-домен-на-render.com"
FILES_FOLDER = "files" """,
    "database.py": """import sqlite3

conn = sqlite3.connect("shop.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    total_purchases INTEGER DEFAULT 0
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    price INTEGER,
    description TEXT,
    file_path TEXT
)''')

conn.commit()

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def create_user(user_id):
    cursor.execute("INSERT INTO users(user_id) VALUES(?)", (user_id,))
    conn.commit()

def add_balance(user_id, amount):
    cursor.execute("UPDATE users SET balance = balance + ?, total_purchases = total_purchases + 1 WHERE user_id=?", (amount, user_id))
    conn.commit()

def get_items():
    cursor.execute("SELECT id, price, description FROM items")
    return cursor.fetchall()

def get_item(item_id):
    cursor.execute("SELECT id, price, description, file_path FROM items WHERE id=?", (item_id,))
    return cursor.fetchone()
""",
    "bot_webhook.py": """from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import config, database, os

bot = Bot(config.BOT_TOKEN)
dp = Dispatcher(bot)

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("Профиль"))
keyboard.add(KeyboardButton("Товары"))
keyboard.add(KeyboardButton("Промокод"))

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=keyboard)

@dp.message_handler(lambda m: m.text == "Профиль")
async def profile(message: types.Message):
    user = database.get_user(message.from_user.id)
    if not user:
        database.create_user(message.from_user.id)
        user = database.get_user(message.from_user.id)
    await message.answer(f"Ваш баланс: {user[1]}₽\\nПокупок всего: {user[2]}")

@dp.message_handler(lambda m: m.text == "Товары")
async def products(message: types.Message):
    items = database.get_items()
    text = "\\n".join([f"{i[0]} - {i[1]}₽ - {i[2]}" for i in items])
    await message.answer(f"Список товаров:\\n{text}")

@dp.message_handler(lambda m: m.text == "Промокод")
async def promo(message: types.Message):
    await message.answer("Введите промокод:")

if __name__ == "__main__":
    if not os.path.exists(config.FILES_FOLDER):
        os.makedirs(config.FILES_FOLDER)
    executor.start_polling(dp, skip_updates=True)
""",
    "webhook.py": """from fastapi import FastAPI, Request
import config, database
from aiogram import Bot

app = FastAPI()
bot = Bot(config.BOT_TOKEN)

@app.post("/crypto")
async def crypto_webhook(request: Request):
    data = await request.json()
    if data.get("update_type") == "invoice_paid":
        payload = data.get("payload")
        user_id, product_id = payload.split(":")
        item = database.get_item(product_id)
        if item:
            database.add_balance(user_id, -item[1])
            if item[3]:
                await bot.send_document(user_id, open(item[3], "rb"))
            else:
                await bot.send_message(user_id, f"✅ Оплата прошла!\\nВаш товар: {item[2]}")
    return {"ok": True}
"""
}

# Создаём ZIP
with zipfile.ZipFile(zip_name, "w") as zf:
    for path, content in files_content.items():
        # Создаём пустые папки, если нужно
        if "/" in path:
            folder = os.path.dirname(path)
            if folder:
                os.makedirs(folder, exist_ok=True)
        zf.writestr(path, content)
    # Создаём пустую папку files
    zf.writestr("files/", "")

print(f"ZIP-файл {zip_name} создан успешно!")