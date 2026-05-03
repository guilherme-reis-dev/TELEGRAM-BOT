import asyncio
import logging
from bot import dp, bot, init_db_pool, close_db_pool, logger

async def init_db_tables():
    """Cria tabelas se não existirem"""
    conn = await dp.storage._client if hasattr(dp.storage, '_client') else None
    
    # Usar conexão do bot para criar tabelas
    import asyncpg
    db_url = __import__('os').getenv("DATABASE_URL")
    conn = await asyncpg.connect(db_url)
    
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id BIGINT PRIMARY KEY,
                nome TEXT NOT NULL,
                telegram_id TEXT UNIQUE NOT NULL,
                role TEXT DEFAULT 'cliente',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("✅ Tabela 'usuarios' verificada/criada com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabela: {e}")
    finally:
        await conn.close()

async def register_user(user_id: int, nome: str):
    """Registra novo usuário no banco de dados"""
    try:
        from bot import get_db_pool
        
        pool = get_db_pool()
        if not pool:
            await init_db_pool()
            pool = get_db_pool()
        
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO usuarios (id, nome, telegram_id) 
                VALUES ($1, $2, $3) 
                ON CONFLICT (id) DO NOTHING
                """,
                user_id, nome, str(user_id)
            )
        logger.info(f"✅ Usuário {user_id} ({nome}) registrado")
    except Exception as e:
        logger.error(f"❌ Erro ao registrar usuário {user_id}: {e}")

async def on_startup():
    """Inicializa a aplicação"""
    logger.info("🚀 Iniciando bot...")
    await init_db_pool()
    await init_db_tables()

async def on_shutdown():
    """Desliga a aplicação"""
    logger.info("🛑 Desligando bot...")
    await close_db_pool()

async def main():
    """Função principal"""
    from aiogram import types
    from aiogram.filters import Command
    
    # Registrar handlers
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        """Handler do comando /start"""
        await register_user(message.from_user.id, message.from_user.first_name or "Usuário")
        await message.reply(f"👋 Bem-vindo, {message.from_user.first_name}!\n\nVocê foi registrado com sucesso!")
    
    try:
        await on_startup()
        logger.info("✅ Bot iniciado com sucesso!")
        await dp.start_polling(bot, allowed_updates=['message', 'callback_query'])
    except KeyboardInterrupt:
        logger.info("⚠️ Bot interrompido pelo usuário")
    finally:
        await on_shutdown()

if __name__ == "__main__":
    asyncio.run(main())