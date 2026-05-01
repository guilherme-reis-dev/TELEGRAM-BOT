import os
import asyncio
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ---------- Configurações ----------
BOT_TOKEN = "8722628197:AAFMXrzDfLUX9Yfb1xGKL_fKA7vojQuWiq4"
DATABASE_URL = os.getenv("DATABASE_URL")  # pega do Heroku Config Vars

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------- Conexão com Postgres ----------
async def conectar_db():
    conn = await asyncpg.connect(DATABASE_URL)
    print("Conectado ao Postgres!")
    await conn.close()

# ---------- Links de assinatura ----------
LINK_SEMANAL = "https://app.syncpayments.com.br/payment-link/a1812a47-4898-4a90-a968-431ce3df4ab7"
LINK_SEMESTRAL = "https://app.syncpayments.com.br/payment-link/a1812b53-a810-44d8-8df6-ff0326c06227"
LINK_ANUAL = "https://app.sync