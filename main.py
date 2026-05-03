import os
import time
import psycopg2
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

bot = telebot.TeleBot(BOT_TOKEN)

FOTO = "https://raw.githubusercontent.com/guilherme-reis-dev/TELEGRAM-BOT/74bb3a0f047937f4dac34cc1aec6c77930d1f221/WhatsApp%20Image%202026-04-09%20at%2017.10.11.jpeg"

TEXTO = """A RABUDA MAIS GOSTOSA DO PRIVACY 🍑
Conteúdo que não fica público no meu PRIVACY‼️

😈 Aqui eu mostro o que não pode subir em rede social
💨 Se tua ex ainda te persegue na mente, eu cuido disso
🔥 Conteúdos frequentes pr te manter preso
🎰 Sorteios semanais de chamadas privadas
🔒 Só pra quem tá dentro

⚠️ Você já chegou até aqui
Agora decide se entra...
ou continua só imaginando 👀👇"""

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

def menu_assinatura():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💎 Semanal — R$15", url="https://app.syncpayments.com.br/payment-link/a1812a47-4898-4a90-a968-431ce3df4ab7"))
    markup.add(InlineKeyboardButton("💎 6 meses — R$30", url="https://app.syncpayments.com.br/payment-link/a1812b53-a810-44d8-8df6-ff0326c06227"))
    markup.add(InlineKeyboardButton("💎 Anual — R$50", url="https://app.syncpayments.com.br/payment-link/a1812bc7-d076-4b49-ab75-6ec1b3148844"))
    return markup

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
    bot.send_photo(
        message.chat.id,
        photo=FOTO,
        caption=TEXTO,
        reply_markup=menu_assinatura()
    )

@bot.message_handler(commands=['assinar'])
def assinar(message):
    bot.send_photo(
        message.chat.id,
        photo=FOTO,
        caption=TEXTO,
        reply_markup=menu_assinatura()
    )

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
print("Aguardando instância anterior encerrar...")
time.sleep(15)
print("Bot rodando...")
while True:
    try:
        bot.infinity_polling(skip_pending=True, timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Erro: {e}")
        time.sleep(5)
