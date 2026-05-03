"""
Configurações centralizadas do bot
Todas as constantes e variáveis de ambiente ficam aqui
"""

import os
import logging
from typing import Optional

# ========== LOGGING ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== VARIÁVEIS DE AMBIENTE ==========
BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN")
DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

# Links de assinatura
LINK_SEMANAL: str = os.getenv(
    "LINK_SEMANAL",
    "https://app.syncpayments.com.br/payment-link/a1812a47-4898-4a90-a968-431ce3df4ab7"
)
LINK_SEMESTRAL: str = os.getenv(
    "LINK_SEMESTRAL",
    "https://app.syncpayments.com.br/payment-link/a1812b53-a810-44d8-8df6-ff0326c06227"
)
LINK_ANUAL: str = os.getenv(
    "LINK_ANUAL",
    "https://app.syncpayments.com.br/payment-link/sua_url_aqui"
)

# ========== CONFIGURAÇÕES DO BANCO ==========
DB_POOL_MIN_SIZE: int = int(os.getenv("DB_POOL_MIN_SIZE", "10"))
DB_POOL_MAX_SIZE: int = int(os.getenv("DB_POOL_MAX_SIZE", "20"))

# ========== PLANOS DE ASSINATURA ==========
PLANOS = {
    "semanal": {
        "link": LINK_SEMANAL,
        "preco": "R$ 9,90",
        "duracao": "7 dias"
    },
    "semestral": {
        "link": LINK_SEMESTRAL,
        "preco": "R$ 49,90",
        "duracao": "6 meses"
    },
    "anual": {
        "link": LINK_ANUAL,
        "preco": "R$ 89,90",
        "duracao": "12 meses"
    }
}

# ========== MENSAGENS DO BOT ==========
MENSAGENS = {
    "start": "👋 Bem-vindo! Escolha seu plano de assinatura.",
    "erro": "❌ Desculpe, ocorreu um erro. Tente novamente.",
    "sucesso": "✅ Operação realizada com sucesso!",
}

# ========== VALIDAÇÃO ==========
def validate_config() -> bool:
    """
    Valida se todas as variáveis de ambiente obrigatórias estão configuradas
    
    Returns:
        bool: True se válido, False caso contrário
    """
    errors = []
    
    if not BOT_TOKEN:
        errors.append("❌ BOT_TOKEN não configurado")
    
    if not DATABASE_URL:
        errors.append("❌ DATABASE_URL não configurado")
    
    if errors:
        for erro in errors:
            logger.error(erro)
        return False
    
    logger.info("✅ Todas as variáveis de ambiente estão configuradas")
    return True
