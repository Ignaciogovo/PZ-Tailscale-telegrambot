import os
import logging
import time
import sqlite3
import subprocess
import re
from rcon import Client

logger = logging.getLogger(__name__)

RCON_HOST = os.getenv("RCON_HOST", "127.0.0.1")
RCON_PORT = int(os.getenv("RCON_PORT", "27015"))
RCON_PASSWORD = os.getenv("RCON_PASSWORD", "")
PZ_DB_PATH = os.getenv("PZ_DB_PATH", "/pz-data/db/server-zomboid.db")
PZ_CONTAINER = os.getenv("PZ_CONTAINER", "project-zomboid")

VALID_ROLES = {"admin", "moderator", "user", "observer", "gm"}

def validate_username(username: str) -> bool:
    if not username or len(username) > 32:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', username))

def validate_steam_id(steam_id: str) -> bool:
    if not steam_id or len(steam_id) != 17:
        return False
    return bool(re.match(r'^\d{17}$', steam_id))

def validate_role(role: str) -> bool:
    return role in VALID_ROLES

def rcon_call(command: str) -> str:
    logger.info(f"Ejecutando RCON: {command}")
    last_error = None
    for attempt in range(2):
        try:
            with Client(RCON_HOST, RCON_PORT, passwd=RCON_PASSWORD, timeout=15) as client:
                result = client.run(command)
                logger.info(f"RCON resultado: {result[:100]}")
                return result
        except Exception as e:
            last_error = e
            logger.warning(f"RCON intento {attempt + 1} falló: {e}")
            if attempt == 0:
                time.sleep(2)
    logger.error("RCON agotado tras 2 intentos")
    raise last_error

def get_players_fast() -> list[dict]:
    try:
        with Client(RCON_HOST, RCON_PORT, passwd=RCON_PASSWORD, timeout=5) as client:
            result = client.run("players")
            return _parse_players(result)
    except Exception as e:
        logger.warning(f"RCON fast falló: {e}")
        return []

def _parse_players(response: str) -> list[dict]:
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
        return [{"username": row["username"], "steamid": row["steamid"] or "unknown",
                 "last_connection": row["lastConnection"] or "nunca",
                 "role": row["role_name"] or "unknown"} for row in cur.fetchall()]
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
            return {"username": row["username"], "steamid": row["steamid"] or "unknown",
                    "last_connection": row["lastConnection"] or "nunca",
                    "role": row["role_name"] or "unknown"}
        return None
    finally:
        conn.close()

def set_role(username: str, role: str) -> str:
    if not validate_username(username):
        raise ValueError(f"Username inválido: {username}")
    if not validate_role(role):
        raise ValueError(f"Rol inválido: {role}")
    return rcon_call(f"setaccesslevel {username} {role}")

def remove_user(username: str) -> str:
    if not validate_username(username):
        raise ValueError(f"Username inválido: {username}")
    return rcon_call(f"removeuserfromwhitelist {username}")

def save_server() -> str:
    return rcon_call("save")

def quit_server() -> str:
    return rcon_call("quit")

def kick_player(username: str) -> str:
    if not validate_username(username):
        raise ValueError(f"Username inválido: {username}")
    user_info = get_user_info(username)
    if user_info:
        protected_roles = ["admin", "moderator", "overseer", "gm"]
        if user_info["role"] in protected_roles:
            raise ValueError(f"⚠️ No se puede kickear a {username} (rol: {user_info['role']}). Primero cambia su rol a 'user'.")
    return rcon_call(f"kickuser {username}")

def ban_player(steam_id: str) -> str:
    if not validate_steam_id(steam_id):
        raise ValueError(f"Steam ID inválido: {steam_id}")
    return rcon_call(f"banid {steam_id}")

def unban_player(steam_id: str) -> str:
    if not validate_steam_id(steam_id):
        raise ValueError(f"Steam ID inválido: {steam_id}")
    return rcon_call(f"unbanid {steam_id}")

def _docker_command(args: list[str], timeout: int = 10) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["docker"] + args,
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def get_container_status() -> tuple[bool, str]:
    ok, output = _docker_command([
        "inspect", "--format", "{{.State.Status}} {{.State.Health.Status}}", PZ_CONTAINER
    ])
    if not ok:
        return False, "not_found" if "No such" in output else f"error: {output}"
    parts = output.split()
    status = parts[0] if parts else "unknown"
    health = parts[1] if len(parts) > 1 else "none"
    if status != "running":
        return False, status
    if health in ("starting", "unhealthy"):
        return False, health
    return True, health

def start_container() -> tuple[bool, str]:
    logger.info(f"Iniciando contenedor {PZ_CONTAINER}")
    ok, output = _docker_command(["start", PZ_CONTAINER])
    if ok:
        return True, "Servidor arrancando..."
    if "No such" in output:
        return False, "Contenedor no existe. Ejecuta: docker compose up -d projectzomboid"
    return False, f"Error: {output}"

def stop_container() -> tuple[bool, str]:
    logger.info(f"Deteniendo contenedor {PZ_CONTAINER}")
    ok, output = _docker_command(["stop", "-t", "30", PZ_CONTAINER], timeout=60)
    if ok:
        return True, "Servidor apagado."
    return False, f"Error: {output}"

def restart_container() -> tuple[bool, str]:
    logger.info(f"Reiniciando contenedor {PZ_CONTAINER}")
    ok, output = _docker_command(["restart", "-t", "30", PZ_CONTAINER], timeout=60)
    if ok:
        return True, "Reiniciando..."
    return False, f"Error: {output}"
