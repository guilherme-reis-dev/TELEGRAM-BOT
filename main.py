import os
import psycopg2
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

bot = telebot.TeleBot(BOT_TOKEN)

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
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
    cursor.close()
    conn.close()

def is_admin(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM usuarios WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result and result[0] == 'admin'

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO usuarios (user_id, first_name, username)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """, (user_id, first_name, username))
    conn.commit()
    cursor.close()
    conn.close()
    bot.reply_to(message, f"Olá, {first_name}! Bem-vindo ao bot! 🤖")

@bot.message_handler(commands=['admin'])
def admin(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Você não tem permissão de admin.")
        return
    bot.reply_to(message, "✅ Painel Admin\n\nComandos disponíveis:\n/usuarios - Ver todos os usuários")

@bot.message_handler(commands=['usuarios'])
def listar_usuarios(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Acesso negado.")
        return
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, first_name, role FROM usuarios")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    texto = "👥 *Usuários cadastrados:*\n\n"
    for row in rows:
        texto += f"• {row[1]} (ID: {row[0]}) - {row[2]}\n"
    bot.reply_to(message, texto, parse_mode="Markdown")

init_db()
print("Bot rodando...")
bot.infinity_polling(skip_pending=True, timeout=10, long_polling_timeout=5)
