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

def players_menu(players: list[dict]) -> InlineKeyboardMarkup:
    buttons = []
    for p in players:
        buttons.append([InlineKeyboardButton(f"🟢 {p['name']}", callback_data=f"player:{p['name']}")])
    buttons.append([InlineKeyboardButton("◀️ Volver", callback_data="main")])
    return InlineKeyboardMarkup(buttons)

def player_detail_menu(username: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("👢 Kick", callback_data=f"kick:{username}")],
        [InlineKeyboardButton("🚫 Ban", callback_data=f"ban:{username}")],
        [InlineKeyboardButton("🔓 Desbanear", callback_data=f"unban:{username}")],
        [InlineKeyboardButton("🛡 Cambiar rol", callback_data=f"role:{username}")],
        [InlineKeyboardButton("◀️ Volver", callback_data="players")],
    ]
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
