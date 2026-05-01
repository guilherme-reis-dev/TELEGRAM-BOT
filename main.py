import os
import psycopg2
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

bot = telebot.TeleBot(BOT_TOKEN)

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        user_id BIGINT UNIQUE,
        username TEXT,
        first_name TEXT,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        role TEXT DEFAULT 'cliente'
    )
""")
conn.commit()

def is_admin(user_id):
    cursor.execute("SELECT role FROM usuarios WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    return result and result[0] == 'admin'

@bot.message_handler(c
