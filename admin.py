"""
Módulo de administração do bot
Gerencia painel admin, estatísticas e controle de usuários
"""

import os
from typing import List, Dict, Any
from datetime import datetime, timedelta
import asyncpg
from config import logger

# ID do administrador (adicionar em variáveis de ambiente)
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

async def is_admin(user_id: int) -> bool:
    """
    Verifica se o usuário é administrador
    
    Args:
        user_id: ID do usuário no Telegram
        
    Returns:
        bool: True se é admin
    """
    return user_id == ADMIN_ID

async def get_total_users(pool: asyncpg.Pool) -> int:
    """
    Obtém o total de usuários registrados
    
    Args:
        pool: Pool de conexões
        
    Returns:
        int: Total de usuários
    """
    try:
        async with pool.acquire() as conn:
            count = await conn.fetchval("SELECT COUNT(*) FROM usuarios")
            return count or 0
    except Exception as e:
        logger.error(f"❌ Erro ao contar usuários: {e}")
        return 0

async def get_users_by_plan(pool: asyncpg.Pool) -> Dict[str, int]:
    """
    Obtém contagem de usuários por plano
    
    Args:
        pool: Pool de conexões
        
    Returns:
        dict: Contagem por plano
    """
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT plano, COUNT(*) as count 
                FROM usuarios 
                WHERE plano IS NOT NULL
                GROUP BY plano
                """
            )
            return {row['plano']: row['count'] for row in rows}
    except Exception as e:
        logger.error(f"❌ Erro ao obter planos: {e}")
        return {}

async def get_new_users_today(pool: asyncpg.Pool) -> int:
    """
    Obtém novos usuários registrados hoje
    
    Args:
        pool: Pool de conexões
        
    Returns:
        int: Número de novos usuários
    """
    try:
        async with pool.acquire() as conn:
            count = await conn.fetchval(
                """
                SELECT COUNT(*) FROM usuarios 
                WHERE DATE(data_inscricao) = CURRENT_DATE
                """
            )
            return count or 0
    except Exception as e:
        logger.error(f"❌ Erro ao contar novos usuários: {e}")
        return 0

async def get_revenue_stats(pool: asyncpg.Pool) -> Dict[str, Any]:
    """
    Obtém estatísticas de receita estimada
    
    Args:
        pool: Pool de conexões
        
    Returns:
        dict: Estatísticas de receita
    """
    precos = {
        "semanal": 9.90,
        "semestral": 49.90,
        "anual": 89.90
    }
    
    try:
        by_plan = await get_users_by_plan(pool)
        total_revenue = sum(by_plan.get(plano, 0) * precos.get(plano, 0) for plano in precos)
        
        return {
            "total_estimado": total_revenue,
            "por_plano": {plano: by_plan.get(plano, 0) * precos[plano] for plano in precos}
        }
    except Exception as e:
        logger.error(f"❌ Erro ao calcular receita: {e}")
        return {"total_estimado": 0, "por_plano": {}}

async def get_all_users(pool: asyncpg.Pool, limit: int = 10, offset: int = 0) -> List[Dict]:
    """
    Obtém lista de usuários com paginação
    
    Args:
        pool: Pool de conexões
        limit: Número de usuários por página
        offset: Deslocamento
        
    Returns:
        list: Lista de usuários
    """
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, nome, telegram_id, plano, data_inscricao 
                FROM usuarios 
                ORDER BY data_inscricao DESC 
                LIMIT $1 OFFSET $2
                """,
                limit, offset
            )
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"❌ Erro ao listar usuários: {e}")
        return []

async def get_user_details(pool: asyncpg.Pool, user_id: int) -> Dict:
    """
    Obtém detalhes completos de um usuário
    
    Args:
        pool: Pool de conexões
        user_id: ID do usuário
        
    Returns:
        dict: Dados do usuário
    """
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM usuarios WHERE id = $1",
                user_id
            )
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"❌ Erro ao buscar usuário: {e}")
        return None

async def remove_user(pool: asyncpg.Pool, user_id: int) -> bool:
    """
    Remove um usuário do sistema
    
    Args:
        pool: Pool de conexões
        user_id: ID do usuário
        
    Returns:
        bool: True se removido com sucesso
    """
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM usuarios WHERE id = $1",
                user_id
            )
        logger.info(f"✅ Usuário {user_id} removido pelo admin")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao remover usuário: {e}")
        return False

async def update_user_plan(pool: asyncpg.Pool, user_id: int, new_plan: str) -> bool:
    """
    Atualiza o plano de um usuário
    
    Args:
        pool: Pool de conexões
        user_id: ID do usuário
        new_plan: Novo plano
        
    Returns:
        bool: True se atualizado com sucesso
    """
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE usuarios 
                SET plano = $1, atualizado_em = CURRENT_TIMESTAMP 
                WHERE id = $2
                """,
                new_plan, user_id
            )
        logger.info(f"✅ Plano do usuário {user_id} atualizado para {new_plan}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar plano: {e}")
        return False

async def get_dashboard_stats(pool: asyncpg.Pool) -> Dict[str, Any]:
    """
    Obtém todas as estatísticas do dashboard
    
    Args:
        pool: Pool de conexões
        
    Returns:
        dict: Todas as estatísticas
    """
    return {
        "total_usuarios": await get_total_users(pool),
        "novos_hoje": await get_new_users_today(pool),
        "usuarios_por_plano": await get_users_by_plan(pool),
        "receita": await get_revenue_stats(pool),
    }

async def broadcast_message(pool: asyncpg.Pool, bot, message_text: str) -> Dict[str, int]:
    """
    Envia mensagem para todos os usuários
    
    Args:
        pool: Pool de conexões
        bot: Instância do bot
        message_text: Texto da mensagem
        
    Returns:
        dict: Estatísticas de envio
    """
    users = await get_all_users(pool, limit=10000)
    
    stats = {"sucesso": 0, "erro": 0}
    
    for user in users:
        try:
            await bot.send_message(
                user['id'],
                message_text,
                parse_mode="HTML"
            )
            stats["sucesso"] += 1
        except Exception as e:
            logger.warning(f"⚠️ Erro ao enviar para {user['id']}: {e}")
            stats["erro"] += 1
    
    logger.info(f"📢 Broadcast: {stats['sucesso']} sucesso, {stats['erro']} erros")
    return stats
