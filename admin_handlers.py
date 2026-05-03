import asyncio
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot import get_db_pool, bot
from admin import (
    is_admin, get_dashboard_stats, get_all_users, 
    broadcast_message, update_user_plan, remove_user, get_user_details
)

admin_router = Router(name="admin_router")

class BroadcastState(StatesGroup):
    waiting_for_message = State()

class ManageUserState(StatesGroup):
    waiting_for_user_id = State()

def get_admin_keyboard():
    """Retorna o teclado do painel de administração"""
    buttons = [
        [InlineKeyboardButton(text="📊 Dashboard", callback_data="admin_dashboard")],
        [InlineKeyboardButton(text="👥 Listar Clientes", callback_data="admin_list_users_0")],
        [InlineKeyboardButton(text="⚙️ Gerenciar Cliente", callback_data="admin_manage_user")],
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

@admin_router.callback_query(F.data == "admin_manage_user")
async def callback_manage_user_start(callback: CallbackQuery, state: FSMContext):
    """Inicia o fluxo de gerenciar usuário"""
    if not await is_admin(callback.from_user.id):
        await callback.answer("Acesso negado.", show_alert=True)
        return

    await state.set_state(ManageUserState.waiting_for_user_id)
    
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Cancelar", callback_data="admin_dashboard")]])
    await callback.message.edit_text(
        "⚙️ **Gerenciar Cliente**\n\nPor favor, digite o ID numérico do usuário (você pode ver o ID na Lista de Clientes).",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    await callback.answer()

@admin_router.message(ManageUserState.waiting_for_user_id)
async def process_manage_user_id(message: types.Message, state: FSMContext):
    """Recebe o ID do usuário e mostra o perfil com botões de ação"""
    if not await is_admin(message.from_user.id):
        return

    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.reply("❌ ID inválido. Por favor, digite apenas números.")
        return

    await state.clear()
    
    pool = get_db_pool()
    user = await get_user_details(pool, user_id)
    
    if not user:
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Voltar ao Painel", callback_data="admin_dashboard")]])
        await message.answer("❌ Cliente não encontrado com este ID.", reply_markup=markup)
        return

    plano = user.get('plano') or 'Gratuito'
    data_inscricao = user.get('data_inscricao')
    data_str = data_inscricao.strftime("%d/%m/%Y %H:%M") if data_inscricao else "N/A"
    
    texto = (
        "👤 **Perfil do Cliente**\n\n"
        f"**ID:** `{user['id']}`\n"
        f"**Nome:** {user['nome']}\n"
        f"**Plano Atual:** {plano}\n"
        f"**Cliente desde:** {data_str}\n"
    )

    buttons = [
        [
            InlineKeyboardButton(text="🔄 Mudar Plano", callback_data=f"admin_change_plan_{user_id}"),
            InlineKeyboardButton(text="❌ Remover", callback_data=f"admin_remove_user_{user_id}")
        ],
        [InlineKeyboardButton(text="🔙 Voltar ao Painel", callback_data="admin_dashboard")]
    ]
    
    await message.answer(texto, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="Markdown")

@admin_router.callback_query(F.data.startswith("admin_change_plan_"))
async def callback_change_plan(callback: CallbackQuery):
    """Mostra as opções de plano para o usuário"""
    if not await is_admin(callback.from_user.id):
        return

    user_id = int(callback.data.split("_")[-1])
    
    buttons = [
        [InlineKeyboardButton(text="Gratuito", callback_data=f"admin_set_plan_{user_id}_gratuito")],
        [
            InlineKeyboardButton(text="Semanal", callback_data=f"admin_set_plan_{user_id}_semanal"),
            InlineKeyboardButton(text="Semestral", callback_data=f"admin_set_plan_{user_id}_semestral")
        ],
        [InlineKeyboardButton(text="Anual", callback_data=f"admin_set_plan_{user_id}_anual")],
        [InlineKeyboardButton(text="🔙 Cancelar", callback_data="admin_dashboard")]
    ]
    
    await callback.message.edit_text(
        "🔄 **Alterar Plano**\n\nSelecione o novo plano para o cliente:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="Markdown"
    )

@admin_router.callback_query(F.data.startswith("admin_set_plan_"))
async def callback_set_plan(callback: CallbackQuery):
    """Aplica o novo plano ao usuário"""
    if not await is_admin(callback.from_user.id):
        return

    parts = callback.data.split("_")
    user_id = int(parts[3])
    novo_plano = parts[4]
    
    if novo_plano == "gratuito":
        novo_plano = None # None significa sem plano na tabela
        
    pool = get_db_pool()
    sucesso = await update_user_plan(pool, user_id, novo_plano)
    
    if sucesso:
        plano_nome = "Gratuito" if novo_plano is None else novo_plano.capitalize()
        await callback.message.edit_text(
            f"✅ **Sucesso!**\n\nO plano do cliente foi atualizado para **{plano_nome}**.",
            reply_markup=get_admin_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            "❌ **Erro!**\n\nNão foi possível atualizar o plano do cliente.",
            reply_markup=get_admin_keyboard(),
            parse_mode="Markdown"
        )
    await callback.answer()

@admin_router.callback_query(F.data.startswith("admin_remove_user_"))
async def callback_remove_user(callback: CallbackQuery):
    """Remove o usuário do banco"""
    if not await is_admin(callback.from_user.id):
        return

    user_id = int(callback.data.split("_")[-1])
    pool = get_db_pool()
    
    sucesso = await remove_user(pool, user_id)
    
    if sucesso:
        await callback.message.edit_text(
            "✅ **Sucesso!**\n\nO cliente foi removido permanentemente.",
            reply_markup=get_admin_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            "❌ **Erro!**\n\nNão foi possível remover o cliente.",
            reply_markup=get_admin_keyboard(),
            parse_mode="Markdown"
        )
    await callback.answer()
