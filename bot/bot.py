import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

import docker
from pz_rcon import get_players, save_server, quit_server, kick_player, ban_player, unban_player, add_user
from keyboards import main_menu, players_menu, player_detail_menu, admin_menu, role_menu, confirm_menu

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_CHAT_IDS = [int(x) for x in os.getenv("TELEGRAM_CHAT_ID", "").split(",") if x.strip()]
PZ_CONTAINER = os.getenv("PZ_CONTAINER", "project-zomboid")
MAX_PLAYERS = int(os.getenv("MAX_PLAYERS", "8"))

docker_client = docker.from_env()

def authorized(update: Update) -> bool:
    chat_id = update.effective_chat.id
    if chat_id not in ALLOWED_CHAT_IDS:
        return False
    return True

def get_pz_status() -> tuple[bool, str]:
    try:
        container = docker_client.containers.get(PZ_CONTAINER)
        status = container.status
        online = status == "running"
        return online, status
    except Exception as e:
        return False, f"error: {e}"

def start_container() -> tuple[bool, str]:
    try:
        container = docker_client.containers.get(PZ_CONTAINER)
        container.start()
        return True, "Servidor arrancando..."
    except Exception as e:
        return False, f"Error: {e}"

def stop_container() -> tuple[bool, str]:
    try:
        save_server()
        quit_server()
        return True, "Guardando y apagando..."
    except Exception:
        pass
    try:
        container = docker_client.containers.get(PZ_CONTAINER)
        container.stop(timeout=30)
        return True, "Servidor apagado."
    except Exception as e:
        return False, f"Error: {e}"

def restart_container() -> tuple[bool, str]:
    try:
        save_server()
        quit_server()
        import time
        time.sleep(5)
        container = docker_client.containers.get(PZ_CONTAINER)
        container.start()
        return True, "Reiniciando..."
    except Exception:
        pass
    try:
        container = docker_client.containers.get(PZ_CONTAINER)
        container.restart(timeout=30)
        return True, "Reiniciando..."
    except Exception as e:
        return False, f"Error: {e}"

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        await update.message.reply_text("⛔ No autorizado.")
        return
    online, status = get_pz_status()
    text = f"🟢 Servidor ONLINE" if online else f"🔴 Servidor OFFLINE"
    text += f"\n👥 Jugadores: ?/{MAX_PLAYERS}"
    await update.message.reply_text(text, reply_markup=main_menu(online))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        await update.callback_query.answer("⛔ No autorizado")
        return

    query = update.callback_query
    await query.answer()
    data = query.data

    online, status = get_pz_status()

    if data == "main":
        text = f"🟢 Servidor ONLINE" if online else f"🔴 Servidor OFFLINE"
        text += f"\n👥 Jugadores: ?/{MAX_PLAYERS}"
        await query.edit_message_text(text, reply_markup=main_menu(online))

    elif data == "status":
        text = "🟢 ONLINE" if online else "🔴 OFFLINE"
        text += f"\nEstado Docker: {status}"
        await query.edit_message_text(text, reply_markup=main_menu(online))

    elif data == "players":
        if not online:
            await query.edit_message_text("🔴 Servidor offline", reply_markup=main_menu(online))
            return
        try:
            players = get_players()
            if not players:
                text = "👥 JUGADORES\n\nNadie conectado"
            else:
                text = f"👥 JUGADORES ({len(players)}/{MAX_PLAYERS})\n\n"
                for p in players:
                    text += f"🟢 {p['name']}\n   Steam: {p['steam_id']}\n   Estado: ONLINE\n\n"
            await query.edit_message_text(text, reply_markup=players_menu(players))
        except Exception as e:
            await query.edit_message_text(f"Error: {e}", reply_markup=main_menu(online))

    elif data.startswith("player:"):
        username = data.split(":", 1)[1]
        text = f"👤 {username.upper()}\n\nEstado: 🟢 ONLINE\nRol: user"
        await query.edit_message_text(text, reply_markup=player_detail_menu(username))

    elif data.startswith("kick:"):
        username = data.split(":", 1)[1]
        await query.edit_message_text(f"¿Kick a {username}?", reply_markup=confirm_menu("kick", username))

    elif data.startswith("ban:"):
        username = data.split(":", 1)[1]
        await query.edit_message_text(f"¿Ban a {username}?", reply_markup=confirm_menu("ban", username))

    elif data.startswith("unban:"):
        username = data.split(":", 1)[1]
        await query.edit_message_text(f"¿Desbanear a {username}?", reply_markup=confirm_menu("unban", username))

    elif data.startswith("role:"):
        username = data.split(":", 1)[1]
        await query.edit_message_text(f"🛡 Cambiar rol de {username}", reply_markup=role_menu(username))

    elif data.startswith("setrole:"):
        parts = data.split(":")
        username, role = parts[1], parts[2]
        try:
            add_user(username, "temp", role)
            await query.edit_message_text(f"✅ Rol de {username} cambiado a {role}", reply_markup=player_detail_menu(username))
        except Exception as e:
            await query.edit_message_text(f"Error: {e}", reply_markup=player_detail_menu(username))

    elif data.startswith("confirm:"):
        parts = data.split(":")
        action, username = parts[1], parts[2] if len(parts) > 2 else ""
        try:
            if action == "kick":
                kick_player(username)
                await query.edit_message_text(f"✅ {username} kickeado", reply_markup=main_menu(online))
            elif action == "ban":
                ban_player(username)
                await query.edit_message_text(f"✅ {username} baneado", reply_markup=main_menu(online))
            elif action == "unban":
                unban_player(username)
                await query.edit_message_text(f"✅ {username} desbaneado", reply_markup=main_menu(online))
        except Exception as e:
            await query.edit_message_text(f"Error: {e}", reply_markup=main_menu(online))

    elif data == "save":
        if not online:
            await query.edit_message_text("🔴 Servidor offline", reply_markup=main_menu(online))
            return
        try:
            save_server()
            await query.edit_message_text("💾 Partida guardada", reply_markup=main_menu(online))
        except Exception as e:
            await query.edit_message_text(f"Error: {e}", reply_markup=main_menu(online))

    elif data == "start":
        if online:
            await query.edit_message_text("🟢 Ya está online", reply_markup=main_menu(online))
            return
        ok, msg = start_container()
        await query.edit_message_text(f"{'✅' if ok else '❌'} {msg}", reply_markup=main_menu(ok))

    elif data == "stop":
        if not online:
            await query.edit_message_text("🔴 Ya está offline", reply_markup=main_menu(online))
            return
        await query.edit_message_text("¿Apagar servidor?", reply_markup=confirm_menu("stop"))

    elif data == "confirm:stop":
        ok, msg = stop_container()
        await query.edit_message_text(f"{'✅' if ok else '❌'} {msg}", reply_markup=main_menu(False))

    elif data == "restart":
        if not online:
            await query.edit_message_text("🔴 Servidor offline", reply_markup=main_menu(online))
            return
        await query.edit_message_text("¿Reiniciar servidor?", reply_markup=confirm_menu("restart"))

    elif data == "confirm:restart":
        ok, msg = restart_container()
        await query.edit_message_text(f"{'✅' if ok else '❌'} {msg}", reply_markup=main_menu(True))

    elif data == "admin":
        await query.edit_message_text("🛠 ADMINISTRACIÓN", reply_markup=admin_menu())

    elif data == "console":
        await query.edit_message_text("📜 Consola\n\n(Próximamente)", reply_markup=admin_menu())

def main():
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN no configurado")
        return
    if not ALLOWED_CHAT_IDS:
        logger.error("TELEGRAM_CHAT_ID no configurado")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot iniciado")
    app.run_polling()

if __name__ == "__main__":
    main()
