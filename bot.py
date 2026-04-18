import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ---------- Configurações ----------
BOT_TOKEN = "8722628197:AAFMXrzDfLUX9Yfb1xGKL_fKA7vojQuWiq4"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------- Links de assinatura ----------
LINK_SEMANAL = "https://app.syncpayments.com.br/payment-link/a1812a47-4898-4a90-a968-431ce3df4ab7"
LINK_SEMESTRAL = "https://app.syncpayments.com.br/payment-link/a1812b53-a810-44d8-8df6-ff0326c06227"
LINK_ANUAL = "https://app.syncpayments.com.br/payment-link/a1812bc7-d076-4b49-ab75-6ec1b3148844"

# ---------- Teclado de planos ----------
def planos_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔹 Semanal — R$15", url=LINK_SEMANAL)],
        [InlineKeyboardButton(text="🔹 6 meses — R$30", url=LINK_SEMESTRAL)],
        [InlineKeyboardButton(text="🔹 Anual — R$50", url=LINK_ANUAL)],
    ])

# ---------- Handlers ----------
@dp.message(CommandStart())
async def on_user_start(message: types.Message):
    # Link raw da imagem no GitHub
    imagem_url = "https://raw.githubusercontent.com/guilherme-reis-dev/img/main/WhatsApp%20Image%202026-04-09%20
