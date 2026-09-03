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
RCON_CONFIG = "/home/steam/server/rcon.yml"

# Contenedores permitidos para docker exec
ALLOWED_CONTAINERS = ["project-zomboid"]

# Roles válidos
VALID_ROLES = {"admin", "moderator", "user", "observer", "gm"}

def validate_username(username: str) -> bool:
    """Validar username: solo letras, números, guiones bajos, guiones. Máx 32 chars."""
    if not username or len(username) > 32:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', username))

def validate_steam_id(steam_id: str) -> bool:
    """Validar Steam ID: solo 17 dígitos."""
    if not steam_id or len(steam_id) != 17:
        return False
    return bool(re.match(r'^\d{17}$', steam_id))

def validate_role(role: str) -> bool:
    """Validar rol: lista blanca de roles."""
    return role in VALID_ROLES

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
    
    # Verificar rol del usuario antes de kickear
    user_info = get_user_info(username)
    if user_info:
        role = user_info["role"]
        protected_roles = ["admin", "moderator", "overseer", "gm"]
        if role in protected_roles:
            raise ValueError(f"⚠️ No se puede kickear a {username} (rol: {role}). Primero cambia su rol a 'user'.")
    
    return rcon_call(f"kickuser {username}")

def ban_player(steam_id: str) -> str:
    if not validate_steam_id(steam_id):
        raise ValueError(f"Steam ID inválido: {steam_id}")
    return rcon_call(f"banid {steam_id}")

def unban_player(steam_id: str) -> str:
    if not validate_steam_id(steam_id):
        raise ValueError(f"Steam ID inválido: {steam_id}")
    return rcon_call(f"unbanid {steam_id}")

def add_user(username: str, password: str) -> str:
    if not validate_username(username):
        raise ValueError(f"Username inválido: {username}")
    return rcon_call(f"adduser {username} {password}")

def _docker_command(args: list[str], timeout: int = 10) -> tuple[bool, str]:
    """Ejecutar comando docker con validación de contenedor"""
    if PZ_CONTAINER not in ALLOWED_CONTAINERS:
        logger.error(f"Contenedor {PZ_CONTAINER} no está en la lista de permitidos")
        return False, "Contenedor no permitido"
    try:
        result = subprocess.run(
            ["docker"] + args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        logger.warning(f"docker timeout para: {args}")
        return False, "Timeout"
    except Exception as e:
        logger.error(f"docker falló: {e}")
        return False, str(e)

def _docker_container_action(action: str, args: list[str], success_msg: str, timeout: int = 10) -> tuple[bool, str]:
    """Ejecutar acción de docker sobre el contenedor con manejo de errores estandarizado"""
    logger.info(f"{action} contenedor {PZ_CONTAINER}")
    ok, output = _docker_command(args, timeout=timeout)
    if ok:
        logger.info(f"Contenedor {action.lower()} correctamente")
        return True, success_msg
    logger.error(f"Error al {action.lower()} contenedor: {output}")
    if "No such" in output:
        return False, "Contenedor no existe" if action != "Iniciando" else "Contenedor no existe. Ejecuta: docker compose up -d projectzomboid"
    return False, f"Error: {output}"

def get_container_status() -> tuple[bool, str]:
    """Obtener estado del contenedor (status y health)"""
    ok, output = _docker_command([
        "inspect",
        "--format",
        "{{.State.Status}} {{.State.Health.Status}}",
        PZ_CONTAINER
    ])
    if not ok:
        return False, "not_found" if "No such" in output else f"error: {output}"
    
    parts = output.split()
    status = parts[0] if len(parts) > 0 else "unknown"
    health = parts[1] if len(parts) > 1 else "none"
    
    logger.info(f"Container status={status}, health={health}")
    
    if status != "running":
        return False, status
    if health in ("starting", "unhealthy"):
        return False, health
    return True, health

def start_container() -> tuple[bool, str]:
    return _docker_container_action("Iniciando", ["start", PZ_CONTAINER], "Servidor arrancando...")

def stop_container() -> tuple[bool, str]:
    return _docker_container_action("Deteniendo", ["stop", "-t", "30", PZ_CONTAINER], "Servidor apagado.", timeout=60)

def restart_container() -> tuple[bool, str]:
    return _docker_container_action("Reiniciando", ["restart", "-t", "30", PZ_CONTAINER], "Reiniciando...", timeout=60)
