import os
import logging
import asyncio
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

import docker
import docker.errors
from pz_rcon import get_players, save_server, quit_server, kick_player, ban_player, unban_player, add_user
from keyboards import main_menu, players_menu, player_detail_menu, admin_menu, role_menu, confirm_menu

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_CHAT_IDS = [int(x) for x in os.getenv("TELEGRAM_CHAT_ID", "").split(",") if x.strip()]
PZ_CONTAINER = os.getenv("PZ_CONTAINER", "project-zomboid")
MAX_PLAYERS = int(os.getenv("MAX_PLAYERS", "8"))

docker_client = docker.from_env()

async def safe_edit(query, text, reply_markup=None):
    try:
        logger.info(f"Intentando editar mensaje: {text[:50]}...")
        await query.edit_message_text(text, reply_markup=reply_markup)
        logger.info("Mensaje editado correctamente")
    except BadRequest as e:
        if "Message is not modified" not in str(e):
            logger.error(f"Error al editar mensaje: {e}")
            raise
        else:
            logger.warning("Mensaje no modificado (ignorado)")

def authorized(update: Update) -> bool:
    chat_id = update.effective_chat.id
    if chat_id not in ALLOWED_CHAT_IDS:
        return False
    return True

async def get_pz_status() -> tuple[bool, str]:
    try:
        container = await asyncio.to_thread(docker_client.containers.get, PZ_CONTAINER)
        status = container.status
        online = status == "running"
        return online, status
    except docker.errors.NotFound:
        return False, "not_found"
    except Exception as e:
        return False, f"error: {e}"

async def start_container() -> tuple[bool, str]:
    logger.info("Iniciando start_container()")
    try:
        container = await asyncio.to_thread(docker_client.containers.get, PZ_CONTAINER)
        logger.info(f"Contenedor encontrado: {container.name}, estado: {container.status}")
        await asyncio.to_thread(container.start)
        logger.info("Contenedor iniciado correctamente")
        return True, "Servidor arrancando..."
    except docker.errors.NotFound:
        logger.error("Contenedor no encontrado")
        return False, "Contenedor no existe. Ejecuta: docker compose up -d projectzomboid"
    except Exception as e:
        logger.error(f"Error al iniciar contenedor: {e}")
        return False, f"Error: {e}"

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
    try:
        container = await asyncio.to_thread(docker_client.containers.get, PZ_CONTAINER)
        logger.info(f"Deteniendo contenedor {container.name} con timeout=30s")
        await asyncio.to_thread(container.stop, timeout=30)
        logger.info("Contenedor detenido correctamente")
        return True, "Servidor apagado."
    except docker.errors.NotFound:
        logger.error("Contenedor no encontrado")
        return False, "Contenedor no existe"
    except Exception as e:
        logger.error(f"Error al detener contenedor: {e}")
        return False, f"Error: {e}"

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
        container = await asyncio.to_thread(docker_client.containers.get, PZ_CONTAINER)
        logger.info(f"Iniciando contenedor {container.name}")
        await asyncio.to_thread(container.start)
        logger.info("Contenedor reiniciado correctamente vía RCON + Docker start")
        return True, "Reiniciando..."
    except Exception as e:
        logger.warning(f"RCON falló, intentando Docker restart: {e}")
    try:
        container = await asyncio.to_thread(docker_client.containers.get, PZ_CONTAINER)
        logger.info(f"Reiniciando contenedor {container.name} con timeout=30s")
        await asyncio.to_thread(container.restart, timeout=30)
        logger.info("Contenedor reiniciado correctamente vía Docker restart")
        return True, "Reiniciando..."
    except docker.errors.NotFound:
        logger.error("Contenedor no encontrado")
        return False, "Contenedor no existe"
    except Exception as e:
        logger.error(f"Error al reiniciar contenedor: {e}")
        return False, f"Error: {e}"

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        await update.message.reply_text("⛔ No autorizado.")
        return
    online, status = await get_pz_status()
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
        else:
            text = f"🟢 Servidor ONLINE" if online else f"🔴 Servidor OFFLINE"
            text += f"\n👥 Jugadores: ?/{MAX_PLAYERS}"
        await safe_edit(query, text, reply_markup=main_menu(online))

    elif data == "status":
        text = "🟢 ONLINE" if online else "🔴 OFFLINE"
        text += f"\nEstado Docker: {status}"
        await safe_edit(query, text, reply_markup=main_menu(online))

    elif data == "players":
        if not online:
            await safe_edit(query, "🔴 Servidor offline", reply_markup=main_menu(online))
            return
        try:
            players = get_players()
            if not players:
                text = "👥 JUGADORES\n\nNadie conectado"
            else:
                text = f"👥 JUGADORES ({len(players)}/{MAX_PLAYERS})\n\n"
                for p in players:
                    text += f"🟢 {p['name']}\n   Steam: {p['steam_id']}\n   Estado: ONLINE\n\n"
            await safe_edit(query, text, reply_markup=players_menu(players))
        except Exception as e:
            await safe_edit(query, f"Error: {e}", reply_markup=main_menu(online))

    elif data.startswith("player:"):
        username = data.split(":", 1)[1]
        text = f"👤 {username.upper()}\n\nEstado: 🟢 ONLINE\nRol: user"
        await safe_edit(query, text, reply_markup=player_detail_menu(username))

    elif data.startswith("kick:"):
        username = data.split(":", 1)[1]
        await safe_edit(query, f"¿Kick a {username}?", reply_markup=confirm_menu("kick", username))

    elif data.startswith("ban:"):
        username = data.split(":", 1)[1]
        await safe_edit(query, f"¿Ban a {username}?", reply_markup=confirm_menu("ban", username))

    elif data.startswith("unban:"):
        username = data.split(":", 1)[1]
        await safe_edit(query, f"¿Desbanear a {username}?", reply_markup=confirm_menu("unban", username))

    elif data.startswith("role:"):
        username = data.split(":", 1)[1]
        await safe_edit(query, f"🛡 Cambiar rol de {username}", reply_markup=role_menu(username))

    elif data.startswith("setrole:"):
        parts = data.split(":")
        username, role = parts[1], parts[2]
        try:
            add_user(username, "temp", role)
            await safe_edit(query, f"✅ Rol de {username} cambiado a {role}", reply_markup=player_detail_menu(username))
        except Exception as e:
            await safe_edit(query, f"Error: {e}", reply_markup=player_detail_menu(username))

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
        try:
            if action == "kick":
                kick_player(username)
                await safe_edit(query, f"✅ {username} kickeado", reply_markup=main_menu(online))
            elif action == "ban":
                ban_player(username)
                await safe_edit(query, f"✅ {username} baneado", reply_markup=main_menu(online))
            elif action == "unban":
                unban_player(username)
                await safe_edit(query, f"✅ {username} desbaneado", reply_markup=main_menu(online))
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
