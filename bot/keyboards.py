from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu(online: bool) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("👥 Jugadores", callback_data="players")],
        [InlineKeyboardButton("🟢 Estado" if online else "🔴 Estado", callback_data="status")],
        [InlineKeyboardButton("💾 Guardar partida", callback_data="save")],
        [InlineKeyboardButton("🔄 Reiniciar", callback_data="restart")],
        [InlineKeyboardButton("⛔ Apagar", callback_data="stop")],
        [InlineKeyboardButton("▶️ Arrancar", callback_data="start")],
        [InlineKeyboardButton("🛠 Administración", callback_data="admin")],
    ]
    return InlineKeyboardMarkup(buttons)

def players_menu(users: list[dict], connected_names: set, banned_ids: set) -> InlineKeyboardMarkup:
    buttons = []
    for u in users:
        is_connected = u["username"] in connected_names
        is_banned = u["steamid"] in banned_ids
        
        status = "🟢" if is_connected else "⚫"
        role_badge = f" [{u['role']}]"
        ban_badge = " 🚫" if is_banned else ""
        
        label = f"{status} {u['username']}{role_badge}{ban_badge}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"player:{u['username']}")])
    buttons.append([InlineKeyboardButton("◀️ Volver", callback_data="main")])
    return InlineKeyboardMarkup(buttons)

def player_detail_menu(username: str, steamid: str = "", is_banned: bool = False) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("👢 Kick", callback_data=f"kick:{username}")],
    ]
    if is_banned:
        buttons.append([InlineKeyboardButton("🔓 Desbanear", callback_data=f"confirm:unban:{username}")])
    else:
        buttons.append([InlineKeyboardButton("🚫 Ban", callback_data=f"ban:{username}")])
    buttons.extend([
        [InlineKeyboardButton("🛡 Cambiar rol", callback_data=f"role:{username}")],
        [InlineKeyboardButton("🗑 Eliminar usuario", callback_data=f"confirm:remove:{username}")],
        [InlineKeyboardButton("◀️ Volver", callback_data="players")],
    ])
    return InlineKeyboardMarkup(buttons)

def admin_menu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("📜 Consola", callback_data="console")],
        [InlineKeyboardButton("◀️ Volver", callback_data="main")],
    ]
    return InlineKeyboardMarkup(buttons)

def role_menu(username: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("👑 Admin", callback_data=f"setrole:{username}:admin")],
        [InlineKeyboardButton("🛡 Moderator", callback_data=f"setrole:{username}:moderator")],
        [InlineKeyboardButton("👤 User", callback_data=f"setrole:{username}:user")],
        [InlineKeyboardButton("◀️ Volver", callback_data=f"player:{username}")],
    ]
    return InlineKeyboardMarkup(buttons)

def confirm_menu(action: str, username: str = "") -> InlineKeyboardMarkup:
    cb_data = f"confirm:{action}:{username}" if username else f"confirm:{action}"
    buttons = [
        [
            InlineKeyboardButton("✅ Confirmar", callback_data=cb_data),
            InlineKeyboardButton("❌ Cancelar", callback_data="main"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)
