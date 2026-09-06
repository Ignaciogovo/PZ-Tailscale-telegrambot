import os
import glob
import logging
import sqlite3
import re
import json
import httpx

logger = logging.getLogger(__name__)

PZ_DB_PATH = os.getenv("PZ_DB_PATH", "/pz-data/db/server-zomboid.db")
PZ_CONTAINER = os.getenv("PZ_CONTAINER", "project-zomboid")
DOCKER_HOST = os.getenv("DOCKER_HOST", "http://127.0.0.1:2375")

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

def rcon_exec(command: str, timeout: int = 15) -> str | None:
    try:
        with httpx.Client(timeout=timeout) as c:
            resp = c.post(f"{DOCKER_HOST}/rcon", json={"command": command})
            if resp.status_code == 200:
                return resp.json().get("output", "")
            logger.warning(f"RCON proxy {resp.status_code}: {resp.text[:200]}")
            return None
    except Exception as e:
        logger.warning(f"RCON proxy error: {e}")
        return None

def rcon_call(command: str) -> str:
    logger.info(f"Ejecutando RCON: {command}")
    result = rcon_exec(command)
    if result is not None:
        return result
    logger.warning("RCON proxy falló, sin fallback (red no disponible)")
    raise ConnectionError("RCON no disponible")

def get_players_fast() -> list[dict]:
    result = rcon_exec("players", timeout=8)
    if result is not None:
        return _parse_players(result)
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

def resolve_db_path() -> str:
    explicit = os.getenv("PZ_DB_PATH", PZ_DB_PATH)
    if explicit and os.path.isfile(explicit):
        return explicit
    candidates = [explicit] if explicit else []
    server_name = (os.getenv("SERVER_NAME") or "").strip()
    db_dir = os.path.dirname(explicit) if explicit else "/pz-data/db"
    if server_name and re.match(r'^[a-zA-Z0-9_.-]+$', server_name):
        derived = os.path.join(db_dir, f"{server_name}.db")
        if os.path.isfile(derived):
            return derived
        candidates.append(derived)
    found = sorted(glob.glob(os.path.join(db_dir, "*.db")))
    if len(found) == 1:
        logger.warning(f"DB {candidates} no encontrada, usando {found[0]}")
        return found[0]
    if len(found) > 1:
        for f in found:
            if server_name and os.path.basename(f) == f"{server_name}.db":
                return f
        logger.warning(f"DB {candidates} no encontrada, varias *.db: {found}, usando {found[0]}")
        return found[0]
    raise FileNotFoundError(
        f"DB no encontrada. Buscado: {', '.join(candidates) or 'nada'} "
        f"(SERVER_NAME={server_name or 'no definido'}, dir={db_dir})"
    )

def get_db_connection() -> sqlite3.Connection:
    db_path = resolve_db_path()
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
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

def _docker_api(method: str, path: str, timeout: int = 10, params: dict = None) -> tuple[bool, str]:
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = getattr(client, method)(f"{DOCKER_HOST}{path}", params=params)
            if resp.status_code in (200, 204):
                return True, resp.text.strip() if resp.text else ""
            if resp.status_code == 304:
                return True, "Ya estaba detenido."
            return False, resp.text.strip()
    except httpx.TimeoutException:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def get_container_status() -> tuple[bool, str]:
    ok, output = _docker_api("get", f"/containers/{PZ_CONTAINER}/json")
    if not ok:
        return False, "not_found" if "No such" in output or "404" in output else f"error: {output}"
    try:
        state = json.loads(output).get("State", {})
        status = state.get("Status", "unknown")
        health = state.get("Health", {}).get("Status", "none")
    except (json.JSONDecodeError, AttributeError):
        return False, "parse_error"
    if status != "running":
        return False, status
    if health in ("starting", "unhealthy"):
        return False, health
    return True, health

def start_container() -> tuple[bool, str]:
    logger.info(f"Iniciando contenedor {PZ_CONTAINER}")
    ok, output = _docker_api("post", f"/containers/{PZ_CONTAINER}/start")
    if ok or "already started" in output.lower():
        return True, "Servidor arrancando..."
    if "No such" in output or "404" in output:
        return False, "Contenedor no existe. Ejecuta: docker compose up -d projectzomboid"
    return False, f"Error: {output}"

def stop_container() -> tuple[bool, str]:
    logger.info(f"Deteniendo contenedor {PZ_CONTAINER}")
    ok, output = _docker_api("post", f"/containers/{PZ_CONTAINER}/stop", params={"t": "30"}, timeout=60)
    if ok:
        return True, "Servidor apagado."
    return False, f"Error: {output}"

def restart_container() -> tuple[bool, str]:
    logger.info(f"Reiniciando contenedor {PZ_CONTAINER}")
    ok, output = _docker_api("post", f"/containers/{PZ_CONTAINER}/restart", params={"t": "30"}, timeout=60)
    if ok:
        return True, "Reiniciando..."
    return False, f"Error: {output}"
