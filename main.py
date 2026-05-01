import os
import psycopg2
import telebot

# Pega variáveis de ambiente do Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

bot = telebot.TeleBot(BOT_TOKEN)

# Conexão com Postgres
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Cria tabela se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id BIGINT PRIMARY KEY,
    nome TEXT,
    role TEXT DEFAULT 'cliente'
)
""")
conn.commit()

# Handler do /start → registra automaticamente
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    nome = message.from_user.first_name

    cursor.execute(
        "INSERT INTO usuarios (id, nome) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
        (user_id, nome)
    )
    conn.commit()

    bot.reply_to