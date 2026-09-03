import os
import logging
import time
import sqlite3
import subprocess
from rcon import Client

logger = logging.getLogger(__name__)

RCON_HOST = os.getenv("RCON_HOST", "127.0.0.1")
RCON_PORT = int(os.getenv("RCON_PORT", "27015"))
RCON_PASSWORD = os.getenv("RCON_PASSWORD", "")
PZ_DB_PATH = os.getenv("PZ_DB_PATH", "/pz-data/db/server-zomboid.db")
PZ_CONTAINER = os.getenv("PZ_CONTAINER", "project-zomboid")
RCON_CONFIG = "/home/steam/server/rcon.yml"

# Contenedores permitidos para docker exec
ALLOWED_CONTAINERS = ["project-zomboid"]

def rcon_exec(command: str) -> str | None:
    """Ejecutar comando RCON vía docker exec + rcon-cli"""
    if PZ_CONTAINER not in ALLOWED_CONTAINERS:
        logger.error(f"Contenedor {PZ_CONTAINER} no está en la lista de permitidos")
        return None
    try:
        result = subprocess.run(
            [
                "docker", "exec", PZ_CONTAINER,
                "rcon-cli",
                "-c", RCON_CONFIG,
                command
            ],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            logger.warning(f"rcon-cli falló: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        logger.warning(f"docker exec timeout para: {command}")
        return None
    except Exception as e:
        logger.warning(f"docker exec falló: {e}")
        return None

def rcon_call(command: str) -> str:
    """Ejecutar comando RCON con docker exec (primario) y librería rcon (fallback)"""
    logger.info(f"Ejecutando RCON: {command}")
    
    # Intentar docker exec primero
    result = rcon_exec(command)
    if result is not None:
        logger.info(f"RCON (docker exec) resultado: {result[:100]}")
        return result
    
    # Fallback a librería rcon
    logger.info(f"Usando fallback librería rcon para: {command}")
    last_error = None
    for attempt in range(2):
        try:
            with Client(RCON_HOST, RCON_PORT, passwd=RCON_PASSWORD, timeout=15) as client:
                result = client.run(command)
                logger.info(f"RCON (librería) resultado: {result[:100]}")
                return result
        except Exception as e:
            last_error = e
            logger.warning(f"RCON intento {attempt + 1} falló: {e}")
            if attempt == 0:
                time.sleep(2)
    logger.error("RCON agotado tras 2 intentos")
    raise last_error

def get_players() -> list[dict]:
    """Obtener jugadores conectados (con retry si falla)"""
    response = rcon_call("players")
    return _parse_players(response)

def get_players_fast() -> list[dict]:
    """Obtener jugadores conectados con timeout corto (5s)"""
    # Intentar docker exec primero
    result = rcon_exec("players")
    if result is not None:
        return _parse_players(result)
    
    # Fallback a librería rcon con timeout corto
    try:
        with Client(RCON_HOST, RCON_PORT, passwd=RCON_PASSWORD, timeout=5) as client:
            result = client.run("players")
            return _parse_players(result)
    except Exception as e:
        logger.warning(f"RCON fast falló: {e}")
        return []

def _parse_players(response: str) -> list[dict]:
    """Parsear respuesta del comando players"""
    players = []
    for line in response.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("Players"):
            continue
        if line.startswith("-"):
            line = line[1:]
        parts = line.split(",")
        name = parts[0].strip()
        if name:
            players.append({
                "name": name,
                "steam_id": parts[1].strip() if len(parts) > 1 else "unknown"
            })
    return players

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{PZ_DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_users() -> list[dict]:
    conn = get_db_connection()
    try:
        cur = conn.execute("""
            SELECT w.username, w.steamid, w.lastConnection, r.name as role_name
            FROM whitelist w
            LEFT JOIN role r ON w.role = r.id
            ORDER BY w.username
        """)
        users = []
        for row in cur.fetchall():
            users.append({
                "username": row["username"],
                "steamid": row["steamid"] or "unknown",
                "last_connection": row["lastConnection"] or "nunca",
                "role": row["role_name"] or "unknown"
            })
        return users
    finally:
        conn.close()

def get_banned_steamids() -> set[str]:
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT steamid FROM bannedid")
        return {row["steamid"] for row in cur.fetchall()}
    finally:
        conn.close()

def get_user_info(username: str) -> dict | None:
    conn = get_db_connection()
    try:
        cur = conn.execute("""
            SELECT w.username, w.steamid, w.lastConnection, r.name as role_name
            FROM whitelist w
            LEFT JOIN role r ON w.role = r.id
            WHERE w.username = ?
        """, (username,))
        row = cur.fetchone()
        if row:
            return {
                "username": row["username"],
                "steamid": row["steamid"] or "unknown",
                "last_connection": row["lastConnection"] or "nunca",
                "role": row["role_name"] or "unknown"
            }
        return None
    finally:
        conn.close()

def set_role(username: str, role: str) -> str:
    return rcon_call(f"setaccesslevel {username} {role}")

def remove_user(username: str) -> str:
    return rcon_call(f"removeuserfromwhitelist {username}")

def save_server() -> str:
    return rcon_call("save")

def quit_server() -> str:
    return rcon_call("quit")

def kick_player(username: str) -> str:
    return rcon_call(f"kickuser {username}")

def ban_player(steam_id: str) -> str:
    return rcon_call(f"banid {steam_id}")

def unban_player(steam_id: str) -> str:
    return rcon_call(f"unbanid {steam_id}")

def add_user(username: str, password: str) -> str:
    return rcon_call(f"adduser {username} {password}")
