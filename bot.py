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
    # Link da imagem no GitHub (repositório público)
    imagem_url = "https://github.com/guilherme-reis-dev/iamgem/raw/main/WhatsApp%20Image%202026-04-09%20at%2017.10.11.jpeg"

    legenda = """𝐀 𝐑𝐀𝐁𝐔𝐃𝐀 𝐌𝐀𝐈𝐒 𝐆𝐎𝐒𝐓𝐎𝐒𝐀 𝐃𝐎 𝐏𝐑𝐈𝐕𝐀𝐂𝐘 🍑
Conteúdo que não fica público no meu 𝗣𝗥𝗜𝗩𝗔𝗖𝗬‼

😈 Aqui eu mostro o que não pode subir em rede social
💭 Se tua ex ainda te persegue na mente, eu cuido disso
🔥 Conteúdos frequentes pr te manter preso
🎥 Sorteios semanais de chamadas privadas
🔒 Só pra quem tá dentro

⚠️ 𝗩𝗼𝗰ê 𝗷𝗮́ 𝗰𝗵𝗲𝗴𝗼𝘂 𝗮𝘁𝗲́ 𝗮𝗾𝘂𝗶
Agora decide se entra...
ou continua só imaginando 👀👇
"""

    await bot.send_photo(
        chat_id=message.chat.id,
        photo=imagem_url,
        caption=legenda,
        reply_markup=planos_keyboard()
    )

@dp.message()
async def fallback(message: types.Message):
    text = "Quer ver o conteúdo exclusivo? Escolha um plano abaixo."
    await message.answer(text, reply_markup=planos_keyboard())

# ---------- Inicialização ----------
async def main():
    print("Bot iniciado. Rodando em polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

