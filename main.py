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
            role TEXT DEFAULT 'cliente',
            banned BOOLEAN DEFAULT FALSE
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

def is_banned(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT banned FROM usuarios WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result and result[0] == True

def menu_assinatura():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💎 Semanal — R$15", url="https://app.syncpayments.com.br/payment-link/a1812a47-4898-4a90-a968-431ce3df4ab7"))
    markup.add(InlineKeyboardButton("💎 6 meses — R$30", url="https://app.syncpayments.com.br/payment-link/a1812b53-a810-44d8-8df6-ff0326c06227"))
    markup.add(InlineKeyboardButton("💎 Anual — R$50", url="https://app.syncpayments.com.br/payment-link/a1812bc7-d076-4b49-ab75-6ec1b3148844"))
    return markup

def menu_admin():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("📊 Estatísticas", callback_data="stats"))
    markup.row(InlineKeyboardButton("👥 Listar Usuários", callback_data="list_0"))
    markup.row(InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"))
    return markup

# ---------- /start ----------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, "❌ Você foi banido do bot.")
        return
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

# ---------- /assinar ----------
@bot.message_handler(commands=['assinar'])
def assinar(message):
    bot.send_photo(
        message.chat.id,
        photo=FOTO,
        caption=TEXTO,
        reply_markup=menu_assinatura()
    )

# ---------- /admin ----------
@bot.message_handler(commands=['admin'])
def admin(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Você não tem permissão de admin.")
        return
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE banned = FALSE")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE role = 'vip' AND banned = FALSE")
    vips = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE joined_at::date = CURRENT_DATE")
    novos = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    texto = (
        f"✅ *Painel Admin*\n\n"
        f"👥 Total de usuários: *{total}*\n"
        f"👑 VIPs: *{vips}*\n"
        f"🆕 Novos hoje: *{novos}*\n\n"
        f"Escolha uma opção:"
    )
    bot.send_message(message.chat.id, texto, parse_mode="Markdown", reply_markup=menu_admin())

# ---------- /usuarios ----------
@bot.message_handler(commands=['usuarios'])
def listar_usuarios(message):
    use
