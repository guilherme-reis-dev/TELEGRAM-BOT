import asyncio
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot import get_db_pool, bot
from admin import (
    is_admin, get_dashboard_stats, get_all_users, 
    broadcast_message, update_user_plan, remove_user
)

admin_router = Router(name="admin_router")

class BroadcastState(StatesGroup):
    waiting_for_message = State()

def get_admin_keyboard():
    """Retorna o teclado do painel de administração"""
    buttons = [
        [InlineKeyboardButton(text="📊 Dashboard", callback_data="admin_dashboard")],
        [InlineKeyboardButton(text="👥 Listar Clientes", callback_data="admin_list_users_0")],
        [InlineKeyboardButton(text="📢 Enviar Broadcast", callback_data="admin_broadcast")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@admin_router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    """Comando principal para abrir o painel admin"""
    if not await is_admin(message.from_user.id):
        # Opcional: ignorar ou enviar mensagem
        return

    pool = get_db_pool()
    if not pool:
        await message.reply("❌ Erro de conexão com o banco de dados.")
        return

    stats = await get_dashboard_stats(pool)
    
    texto = (
        "🛠 **Painel de Administração**\n\n"
        f"👥 **Total de Usuários:** {stats['total_usuarios']}\n"
        f"🆕 **Novos Hoje:** {stats['novos_hoje']}\n\n"
        f"💰 **Receita Estimada:** R$ {stats['receita']['total_estimado']:.2f}\n"
    )

    if stats['usuarios_por_plano']:
        texto += "\n📦 **Por Plano:**\n"
        for plano, count in stats['usuarios_por_plano'].items():
            texto += f" - {plano.capitalize()}: {count}\n"

    await message.answer(texto, reply_markup=get_admin_keyboard(), parse_mode="Markdown")

@admin_router.callback_query(F.data == "admin_dashboard")
async def callback_admin_dashboard(callback: CallbackQuery):
    """Atualiza a mensagem com os dados mais recentes do dashboard"""
    if not await is_admin(callback.from_user.id):
        await callback.answer("Acesso negado.", show_alert=True)
        return

    pool = get_db_pool()
    stats = await get_dashboard_stats(pool)
    
    texto = (
        "🛠 **Painel de Administração**\n\n"
        f"👥 **Total de Usuários:** {stats['total_usuarios']}\n"
        f"🆕 **Novos Hoje:** {stats['novos_hoje']}\n\n"
        f"💰 **Receita Estimada:** R$ {stats['receita']['total_estimado']:.2f}\n"
    )

    if stats['usuarios_por_plano']:
        texto += "\n📦 **Por Plano:**\n"
        for plano, count in stats['usuarios_por_plano'].items():
            texto += f" - {plano.capitalize()}: {count}\n"

    # Se a mensagem for exatamente a mesma, vai dar erro no Telegram ao editar,
    # Então a gente coloca um timestamp ou ignora o erro
    try:
        await callback.message.edit_text(texto, reply_markup=get_admin_keyboard(), parse_mode="Markdown")
        await callback.answer("Dashboard atualizado!")
    except Exception:
        await callback.answer("Já está atualizado!")

@admin_router.callback_query(F.data.startswith("admin_list_users_"))
async def callback_list_users(callback: CallbackQuery):
    """Lista usuários com paginação simples (5 por página)"""
    if not await is_admin(callback.from_user.id):
        await callback.answer("Acesso negado.", show_alert=True)
        return

    page = int(callback.data.split("_")[-1])
    limit = 5
    offset = page * limit

    pool = get_db_pool()
    users = await get_all_users(pool, limit=limit, offset=offset)
    
    if not users and page > 0:
        await callback.answer("Fim da lista.")
        return

    texto = f"👥 **Lista de Clientes (Pág. {page + 1})**\n\n"
    
    for u in users:
        plano = u.get('plano') or 'Gratuito'
        data_inscricao = u.get('data_inscricao')
        data_str = data_inscricao.strftime("%d/%m/%Y") if data_inscricao else "N/A"
        texto += f"ID: `{u['id']}`\nNome: {u['nome']}\nPlano: {plano}\nData: {data_str}\n---\n"

    buttons = []
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Anterior", callback_data=f"admin_list_users_{page - 1}"))
    
    if len(users) == limit:
        nav_buttons.append(InlineKeyboardButton(text="Próximo ➡️", callback_data=f"admin_list_users_{page + 1}"))
        
    if nav_buttons:
        buttons.append(nav_buttons)
        
    buttons.append([InlineKeyboardButton(text="🔙 Voltar", callback_data="admin_dashboard")])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    try:
        await callback.message.edit_text(texto, reply_markup=markup, parse_mode="Markdown")
        await callback.answer()
    except Exception:
        pass

@admin_router.callback_query(F.data == "admin_broadcast")
async def callback_broadcast_start(callback: CallbackQuery, state: FSMContext):
    """Inicia o fluxo de broadcast"""
    if not await is_admin(callback.from_user.id):
        await callback.answer("Acesso negado.", show_alert=True)
        return

    await state.set_state(BroadcastState.waiting_for_message)
    
    buttons = [[InlineKeyboardButton(text="Cancelar", callback_data="admin_dashboard")]]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(
        "📢 **Modo Broadcast**\n\nDigite a mensagem que deseja enviar para TODOS os clientes.\n\n"
        "(Suporta HTML básico como <b>negrito</b>, <i>itálico</i>, <a href='url'>link</a>)", 
        reply_markup=markup,
        parse_mode="Markdown"
    )
    await callback.answer()

@admin_router.message(BroadcastState.waiting_for_message)
async def process_broadcast_message(message: types.Message, state: FSMContext):
    """Recebe a mensagem de broadcast e envia para todos"""
    if not await is_admin(message.from_user.id):
        return

    # Sair do state
    await state.clear()
    
    msg_espera = await message.answer("🔄 Enviando mensagens... Isso pode demorar um pouco.")
    
    pool = get_db_pool()
    stats = await broadcast_message(pool, bot, message.text)
    
    resultado = (
        "✅ **Broadcast Concluído!**\n\n"
        f"Entregues: {stats['sucesso']}\n"
        f"Falhas: {stats['erro']}"
    )
    
    await msg_espera.edit_text(resultado, reply_markup=get_admin_keyboard(), parse_mode="Markdown")
