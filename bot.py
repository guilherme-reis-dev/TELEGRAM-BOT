import os
import asyncio
import logging
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ---------- Configuração de Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ---------- Configurações ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")  # pega do Heroku Config Vars

# Validar variáveis de ambiente
if not BOT_TOKEN:
    raise ValueError("Erro: BOT_TOKEN não foi definida nas variáveis de ambiente")
if not DATABASE_URL:
    raise ValueError("Erro: DATABASE_URL não foi definida nas variáveis de ambiente")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db_pool = None

# ---------- Conexão com Postgres ----------
async def init_db_pool():
    """Inicializa o pool de conexões com Postgres"""
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=10, max_size=20)
        logger.info("✅ Pool de conexões Postgres inicializado com sucesso")
        return db_pool
    except Exception as e:
        logger.error(f"❌ Erro ao criar pool de conexões: {e}")
        raise

async def close_db_pool():
    """Fecha o pool de conexões"""
    global db_pool
    if db_pool:
        await db_pool.close()
        logger.info("✅ Pool de conexões fechado")

def get_db_pool():
    """Retorna o pool de conexões atual"""
    return db_pool

# ---------- Links de assinatura ----------
LINK_SEMANAL = "https://app.syncpayments.com.br/payment-link/a1812a47-4898-4a90-a968-431ce3df4ab7"
LINK_SEMESTRAL = "https://app.syncpayments.com.br/payment-link/a1812b53-a810-44d8-8df6-ff0326c06227"
LINK_ANUAL = os.getenv("LINK_ANUAL", "https://app.syncpayments.com.br/payment-link/seu_id_aqui")  # Adicione em Heroku

PLANOS = {
    "semanal": {"link": LINK_SEMANAL, "preco": "R$ XX,XX"},
    "semestral": {"link": LINK_SEMESTRAL, "preco": "R$ XX,XX"},
    "anual": {"link": LINK_ANUAL, "preco": "R$ XX,XX"}
}