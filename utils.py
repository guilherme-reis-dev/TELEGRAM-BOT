"""
Funções utilitárias do bot
Lógicas compartilhadas e helpers
"""

import asyncpg
from typing import Optional
from config import logger, DATABASE_URL, DB_POOL_MIN_SIZE, DB_POOL_MAX_SIZE

db_pool: Optional[asyncpg.Pool] = None

async def init_db_pool() -> asyncpg.Pool:
    """
    Inicializa o pool de conexões com Postgres
    
    Returns:
        asyncpg.Pool: Pool de conexões
        
    Raises:
        Exception: Se não conseguir conectar ao banco
    """
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=DB_POOL_MIN_SIZE,
            max_size=DB_POOL_MAX_SIZE
        )
        logger.info("✅ Pool de conexões Postgres inicializado com sucesso")
        return db_pool
    except Exception as e:
        logger.error(f"❌ Erro ao criar pool de conexões: {e}")
        raise

async def close_db_pool() -> None:
    """
    Fecha o pool de conexões
    """
    global db_pool
    if db_pool:
        await db_pool.close()
        logger.info("✅ Pool de conexões fechado")
        db_pool = None

def get_db_pool() -> Optional[asyncpg.Pool]:
    """
    Retorna o pool de conexões atual
    
    Returns:
        asyncpg.Pool | None: Pool de conexões ou None
    """
    return db_pool

async def create_tables() -> None:
    """
    Cria as tabelas do banco de dados se não existirem
    
    Raises:
        Exception: Se houver erro ao criar tabelas
    """
    pool = get_db_pool()
    if not pool:
        raise RuntimeError("Pool de conexões não inicializado")
    
    sql = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id BIGINT PRIMARY KEY,
            nome TEXT NOT NULL,
            telegram_id TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'cliente',
            plano TEXT DEFAULT NULL,
            data_inscricao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_usuarios_telegram_id ON usuarios(telegram_id);
        CREATE INDEX IF NOT EXISTS idx_usuarios_role ON usuarios(role);
    """
    
    try:
        async with pool.acquire() as conn:
            await conn.execute(sql)
        logger.info("✅ Tabelas criadas/verificadas com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
        raise

async def register_user(user_id: int, nome: str, plano: str = None) -> bool:
    """
    Registra novo usuário no banco de dados
    
    Args:
        user_id: ID do usuário no Telegram
        nome: Nome do usuário
        plano: Plano escolhido (opcional)
        
    Returns:
        bool: True se registrado com sucesso
    """
    pool = get_db_pool()
    if not pool:
        logger.error("Pool de conexões não inicializado")
        return False
    
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO usuarios (id, nome, telegram_id, plano) 
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO UPDATE 
                SET nome = $2, atualizado_em = CURRENT_TIMESTAMP
                """,
                user_id, nome, str(user_id), plano
            )
        logger.info(f"✅ Usuário {user_id} ({nome}) registrado")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao registrar usuário {user_id}: {e}")
        return False

async def get_user(user_id: int) -> dict:
    """
    Busca informações do usuário
    
    Args:
        user_id: ID do usuário no Telegram
        
    Returns:
        dict: Dados do usuário ou None
    """
    pool = get_db_pool()
    if not pool:
        return None
    
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM usuarios WHERE id = $1",
                user_id
            )
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"❌ Erro ao buscar usuário {user_id}: {e}")
        return None

async def update_user_plan(user_id: int, plano: str) -> bool:
    """
    Atualiza o plano do usuário
    
    Args:
        user_id: ID do usuário
        plano: Novo plano
        
    Returns:
        bool: True se atualizado com sucesso
    """
    pool = get_db_pool()
    if not pool:
        return False
    
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE usuarios 
                SET plano = $1, atualizado_em = CURRENT_TIMESTAMP 
                WHERE id = $2
                """,
                plano, user_id
            )
        logger.info(f"✅ Plano do usuário {user_id} atualizado para {plano}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar plano: {e}")
        return False
