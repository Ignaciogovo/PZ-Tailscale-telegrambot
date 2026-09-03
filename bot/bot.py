import os
import logging
import asyncio
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from pz_rcon import get_players, get_players_fast, get_all_users, get_banned_steamids, get_user_info, set_role, remove_user, save_server, quit_server, kick_player, ban_player, unban_player, add_user, get_container_status, start_container as pz_start, stop_container as pz_stop, restart_container as pz_restart, validate_username, validate_steam_id, validate_role
from keyboards import main_menu, players_menu, player_detail_menu, admin_menu, role_menu, confirm_menu

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_CHAT_IDS = [int(x) for x in os.getenv("TELEGRAM_CHAT_ID", "").split(",") if x.strip()]
PZ_CONTAINER = os.getenv("PZ_CONTAINER", "project-zomboid")
MAX_PLAYERS = int(os.getenv("MAX_PLAYERS", "8"))

async def safe_edit(query, text, reply_markup=None):
    try:
        await query.edit_message_text(text, reply_markup=reply_markup)
    except BadRequest as e:
        if "Message is not modified" not in str(e):
            raise

def authorized(update: Update) -> bool:
    return update.effective_chat.id in ALLOWED_CHAT_IDS

async def get_pz_status() -> tuple[bool, str]:
    return await asyncio.to_thread(get_container_status)

async def start_container() -> tuple[bool, str]:
    return await asyncio.to_thread(pz_start)

async def stop_container() -> tuple[bool, str]:
    logger.info("Iniciando stop_container()")
    try:
        logger.info("Intentando guardar y cerrar servidor vía RCON...")
        await asyncio.to_thread(save_server)
        logger.info("Servidor guardado vía RCON")
        await asyncio.to_thread(quit_server)
        logger.info("Servidor cerrado vía RCON")
        return True, "Guardando y apagando..."
    except Exception as e:
        logger.warning(f"RCON falló, intentando Docker stop: {e}")
    return await asyncio.to_thread(pz_stop)

async def restart_container() -> tuple[bool, str]:
    logger.info("Iniciando restart_container()")
    try:
        logger.info("Intentando guardar y cerrar servidor vía RCON...")
        await asyncio.to_thread(save_server)
        logger.info("Servidor guardado vía RCON")
        await asyncio.to_thread(quit_server)
        logger.info("Servidor cerrado vía RCON")
        logger.info("Esperando 5 segundos...")
        await asyncio.sleep(5)
        return await asyncio.to_thread(pz_start)
    except Exception as e:
        logger.warning(f"RCON falló, intentando Docker restart: {e}")
    return await asyncio.to_thread(pz_restart)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        await update.message.reply_text("⛔ No autorizado.")
        return
    online, status = await get_pz_status()
    if status == "starting":
        text = "🔄 REINICIANDO..."
    elif status == "unhealthy":
        text = "🔴 Problemas con el servidor"
    else:
        text = f"🟢 Servidor ONLINE" if online else f"🔴 Servidor OFFLINE"
    text += f"\n👥 Jugadores: ?/{MAX_PLAYERS}"
    await update.message.reply_text(text, reply_markup=main_menu(online))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        await update.callback_query.answer("⛔ No autorizado")
        return

    query = update.callback_query
    data = query.data
    logger.info(f"Callback recibido: {data}")
    
    await query.answer()

    logger.info(f"Obteniendo estado PZ...")
    online, status = await get_pz_status()
    logger.info(f"Estado PZ: online={online}, status={status}")

    if data == "main":
        if status == "not_found":
            text = "⚠️ Contenedor PZ no existe\n\nEjecuta en el host:\n`docker compose up -d projectzomboid`"
        elif status == "starting":
            text = "🔄 REINICIANDO..."
            text += f"\n👥 Jugadores: ?/{MAX_PLAYERS}"
        elif status == "unhealthy":
            text = "🔴 Problemas con el servidor"
            text += f"\n👥 Jugadores: ?/{MAX_PLAYERS}"
        else:
            text = f"🟢 Servidor ONLINE" if online else f"🔴 Servidor OFFLINE"
            text += f"\n👥 Jugadores: ?/{MAX_PLAYERS}"
        await safe_edit(query, text, reply_markup=main_menu(online))

    elif data == "status":
        if status == "starting":
            text = "🔄 REINICIANDO"
        elif status == "unhealthy":
            text = "🔴 Problemas con el servidor"
        elif online:
            text = "🟢 ONLINE"
        else:
            text = "🔴 OFFLINE"
        text += f"\nEstado: {status}"
        await safe_edit(query, text, reply_markup=main_menu(online))

    elif data == "players":
        if not online:
            await safe_edit(query, "🔴 Servidor offline", reply_markup=main_menu(online))
            return
        try:
            all_users = get_all_users()
            connected = get_players_fast()
            connected_names = {p["name"] for p in connected}
            banned_ids = get_banned_steamids()
            
            if not all_users:
                text = "👥 USUARIOS\n\nNo hay usuarios registrados"
            else:
                text = f"👥 USUARIOS ({len(all_users)})\n\n"
                if not connected:
                    text += "⚠️ No se pudo verificar estado de conexión\n\n"
                for u in all_users:
                    is_connected = u["username"] in connected_names
                    is_banned = u["steamid"] in banned_ids
                    
                    status = "🟢" if is_connected else "⚫"
                    role_badge = f" [{u['role']}]"
                    ban_badge = " 🚫" if is_banned else ""
                    
                    text += f"{status} {u['username']}{role_badge}{ban_badge}\n"
                    text += f"   Steam: {u['steamid']}\n"
                    text += f"   Última conexión: {u['last_connection']}\n\n"
            
            await safe_edit(query, text, reply_markup=players_menu(all_users, connected_names, banned_ids))
        except Exception as e:
            await safe_edit(query, f"Error: {e}", reply_markup=main_menu(online))

    elif data.startswith("player:"):
        username = data.split(":", 1)[1]
        try:
            user_info = get_user_info(username)
            if not user_info:
                await safe_edit(query, f"❌ Usuario {username} no encontrado", reply_markup=main_menu(online))
                return
            
            connected = get_players_fast()
            connected_names = {p["name"] for p in connected}
            banned_ids = get_banned_steamids()
            
            is_connected = username in connected_names
            is_banned = user_info["steamid"] in banned_ids
            
            status = "🟢 ONLINE" if is_connected else "⚫ OFFLINE"
            ban_status = " 🚫 BANEADO" if is_banned else ""
            
            text = f"👤 {username.upper()}\n\n"
            text += f"Estado: {status}{ban_status}\n"
            text += f"Rol: {user_info['role']}\n"
            text += f"Steam: {user_info['steamid']}\n"
            text += f"Última conexión: {user_info['last_connection']}"
            
            await safe_edit(query, text, reply_markup=player_detail_menu(username, user_info["steamid"], is_banned))
        except Exception as e:
            await safe_edit(query, f"Error: {e}", reply_markup=main_menu(online))

    elif data.startswith("kick:"):
        username = data.split(":", 1)[1]
        if not validate_username(username):
            await safe_edit(query, f"❌ Username inválido: {username}", reply_markup=main_menu(online))
            return
        await safe_edit(query, f"¿Kick a {username}?", reply_markup=confirm_menu("kick", username))

    elif data.startswith("ban:"):
        username = data.split(":", 1)[1]
        if not validate_username(username):
            await safe_edit(query, f"❌ Username inválido: {username}", reply_markup=main_menu(online))
            return
        await safe_edit(query, f"¿Ban a {username}?", reply_markup=confirm_menu("ban", username))

    elif data.startswith("unban:"):
        username = data.split(":", 1)[1]
        if not validate_username(username):
            await safe_edit(query, f"❌ Username inválido: {username}", reply_markup=main_menu(online))
            return
        await safe_edit(query, f"¿Desbanear a {username}?", reply_markup=confirm_menu("unban", username))

    elif data.startswith("role:"):
        username = data.split(":", 1)[1]
        if not validate_username(username):
            await safe_edit(query, f"❌ Username inválido: {username}", reply_markup=main_menu(online))
            return
        await safe_edit(query, f"🛡 Cambiar rol de {username}", reply_markup=role_menu(username))

    elif data.startswith("setrole:"):
        parts = data.split(":")
        username, role = parts[1], parts[2]
        if not validate_username(username):
            await safe_edit(query, f"❌ Username inválido: {username}", reply_markup=main_menu(online))
            return
        if not validate_role(role):
            await safe_edit(query, f"❌ Rol inválido: {role}", reply_markup=main_menu(online))
            return
        try:
            set_role(username, role)
            user_info = get_user_info(username)
            banned_ids = get_banned_steamids()
            is_banned = user_info["steamid"] in banned_ids if user_info else False
            await safe_edit(query, f"✅ Rol de {username} cambiado a {role}", reply_markup=player_detail_menu(username, user_info["steamid"] if user_info else "", is_banned))
        except Exception as e:
            await safe_edit(query, f"Error: {e}", reply_markup=player_detail_menu(username, "", False))

    elif data == "save":
        if not online:
            await safe_edit(query, "🔴 Servidor offline", reply_markup=main_menu(online))
            return
        try:
            save_server()
            await safe_edit(query, "💾 Partida guardada", reply_markup=main_menu(online))
        except Exception as e:
            await safe_edit(query, f"Error: {e}", reply_markup=main_menu(online))

    elif data == "start":
        if online:
            await safe_edit(query, "🟢 Ya está online", reply_markup=main_menu(online))
            return
        ok, msg = await start_container()
        if not ok and "no existe" in msg:
            await safe_edit(query, f"❌ {msg}", reply_markup=main_menu(False))
        else:
            await safe_edit(query, f"{'✅' if ok else '❌'} {msg}", reply_markup=main_menu(ok))

    elif data == "stop":
        logger.info("Handler stop ejecutado")
        if not online:
            logger.info("Servidor offline, no se puede apagar")
            await safe_edit(query, "🔴 Ya está offline", reply_markup=main_menu(online))
            return
        logger.info("Mostrando confirmación de apagado")
        await safe_edit(query, "¿Apagar servidor?", reply_markup=confirm_menu("stop"))

    elif data == "confirm:stop":
        logger.info("Handler confirm:stop ejecutado")
        ok, msg = await stop_container()
        logger.info(f"Resultado stop_container: ok={ok}, msg={msg}")
        await safe_edit(query, f"{'✅' if ok else '❌'} {msg}", reply_markup=main_menu(False))

    elif data == "restart":
        logger.info("Handler restart ejecutado")
        if not online:
            logger.info("Servidor offline, no se puede reiniciar")
            await safe_edit(query, "🔴 Servidor offline", reply_markup=main_menu(online))
            return
        logger.info("Mostrando confirmación de reinicio")
        await safe_edit(query, "¿Reiniciar servidor?", reply_markup=confirm_menu("restart"))

    elif data == "confirm:restart":
        logger.info("Handler confirm:restart ejecutado")
        ok, msg = await restart_container()
        logger.info(f"Resultado restart_container: ok={ok}, msg={msg}")
        await safe_edit(query, f"{'✅' if ok else '❌'} {msg}", reply_markup=main_menu(True))

    elif data.startswith("confirm:"):
        parts = data.split(":")
        action, username = parts[1], parts[2] if len(parts) > 2 else ""
        if username and not validate_username(username):
            await safe_edit(query, f"❌ Username inválido: {username}", reply_markup=main_menu(online))
            return
        try:
            if action == "kick":
                kick_player(username)
                await safe_edit(query, f"✅ {username} kickeado", reply_markup=main_menu(online))
            elif action == "ban":
                user_info = get_user_info(username)
                if user_info and user_info["steamid"] != "unknown":
                    if not validate_steam_id(user_info["steamid"]):
                        await safe_edit(query, f"❌ Steam ID inválido para {username}", reply_markup=main_menu(online))
                        return
                    ban_player(user_info["steamid"])
                    await safe_edit(query, f"✅ {username} baneado (Steam: {user_info['steamid']})", reply_markup=main_menu(online))
                else:
                    await safe_edit(query, f"❌ No se pudo obtener SteamID de {username}", reply_markup=main_menu(online))
            elif action == "unban":
                user_info = get_user_info(username)
                if user_info and user_info["steamid"] != "unknown":
                    if not validate_steam_id(user_info["steamid"]):
                        await safe_edit(query, f"❌ Steam ID inválido para {username}", reply_markup=main_menu(online))
                        return
                    unban_player(user_info["steamid"])
                    await safe_edit(query, f"✅ {username} desbaneado (Steam: {user_info['steamid']})", reply_markup=main_menu(online))
                else:
                    await safe_edit(query, f"❌ No se pudo obtener SteamID de {username}", reply_markup=main_menu(online))
            elif action == "remove":
                remove_user(username)
                await safe_edit(query, f"✅ {username} eliminado de la whitelist", reply_markup=main_menu(online))
        except Exception as e:
            await safe_edit(query, f"Error: {e}", reply_markup=main_menu(online))

    elif data == "admin":
        await safe_edit(query, "🛠 ADMINISTRACIÓN", reply_markup=admin_menu())

    elif data == "console":
        await safe_edit(query, "📜 Consola\n\n(Próximamente)", reply_markup=admin_menu())

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
