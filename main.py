import os
import psycopg2
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

bot = telebot.TeleBot(BOT_TOKEN)

# Conexão com Postgres
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Garante que a tabela existe com as colunas certas
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

# ---------- Função helper ----------
def is_admin(user_id):
    cursor.execute("SELECT role FROM usuarios WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    return result and result[0] == 'admin'

# ---------- /start ----------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username

    cursor.execute("""
        INSERT INTO usuarios (user_id, first_name, username)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """, (user_id, first_name, username))
    conn.commit()

    bot.reply_to(message, f"Olá, {first_name}! Bem-vindo ao bot! 🤖")

# ---------- /admin ----------
@bot.message_handler(commands=['admin'])
def admin(message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        bot.reply_to(message, "❌ Você não tem permissão de admin.")
        return

    bot.reply_to(message, "✅ Painel Admin\n\nComandos disponíveis:\n/usuarios - Ver todos os usuários")

# ---------- /usuarios (só admin) ----------
@bot.message_handler(commands=['usuarios'])
def listar_usuarios(message):
    user_id = message.from_user.id

    if not is_admin(user_id):
        bot.reply_to(message, "❌ Acesso negado.")
        return

    cursor.execute("SELECT user_id, first_name, role FROM usuarios")
    rows = cursor.fetchall()

    texto = "👥 *Usuários cadastrados:*\n\n"
    for row in rows:
        texto += f"• {row[1]} (ID: {row[0]}) - {row[2]}\n"

    bot.reply_to(message, texto, parse_mode="Markdown")

# ---------- Inicia o bot ----------
print("Bot rodando...")
bot.infinity_polling()
