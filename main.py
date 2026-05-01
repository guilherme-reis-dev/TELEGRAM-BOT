import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from database import SessionLocal, usuarios, init_db
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! 👋 Eu sou seu bot conectado ao Railway!")

async def registrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nome = " ".join(context.args)
    if not nome:
        await update.message.reply_text("Use /registrar <seu_nome>")
        return

    db = SessionLocal()
    db.execute(usuarios.insert().values(nome=nome, telegram_id=str(update.effective_user.id)))
    db.commit()
    db.close()

    await update.message.reply_text(f"Usuário {nome} registrado com sucesso!")

def main():
    init_db()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("registrar", registrar))

    app.run_polling()

if __name__ == "__main__":
    main()
