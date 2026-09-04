import os
import re
import json
import logging
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from http.client import HTTPConnection, OK

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ALLOWED_CONTAINER = os.getenv("ALLOWED_CONTAINER", "project-zomboid")
PROXY_PORT = int(os.getenv("PROXY_PORT", "2375"))
DOCKER_SOCKET = "/var/run/docker.sock"

RCON_CONFIG = "/home/steam/server/rcon.yml"
MAX_COMMAND_LENGTH = 200

ALLOWED_RCON_COMMANDS = {
    "players", "save", "quit", "servermsg",
    "kickuser", "banid", "unbanid",
    "adduser", "setaccesslevel", "removeuserfromwhitelist",
}

VALID_ROLES = {"admin", "moderator", "user", "observer", "gm"}

RE_USERNAME = re.compile(r'^[a-zA-Z0-9_-]{1,32}$')
RE_STEAM_ID = re.compile(r'^\d{17}$')


class UnixHTTPConnection(HTTPConnection):
    def __init__(self, uds_path, timeout=30):
        super().__init__("localhost", timeout=timeout)
        self.uds_path = uds_path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.uds_path)


def docker_request(method, path, body=None, timeout=30):
    conn = UnixHTTPConnection(DOCKER_SOCKET, timeout=timeout)
    try:
        conn.request(method, path, body=body, headers={"Content-Type": "application/json"} if body else {})
        resp = conn.getresponse()
        data = resp.read().decode(errors="replace")
        return resp.status, data
    finally:
        conn.close()


def validate_rcon_command(command: str) -> tuple[bool, str]:
    command = command.strip()
    if not command:
        return False, "Comando vacío"
    if len(command) > MAX_COMMAND_LENGTH:
        return False, "Comando demasiado largo"

    parts = command.split()
    base = parts[0]

    if base not in ALLOWED_RCON_COMMANDS:
        return False, f"Comando no permitido: {base}"

    if base in ("kickuser", "removeuserfromwhitelist"):
        if len(parts) < 2 or not RE_USERNAME.match(parts[1]):
            return False, f"Username inválido para {base}"
    elif base == "banid":
        if len(parts) < 2 or not RE_STEAM_ID.match(parts[1]):
            return False, "Steam ID inválido (17 dígitos)"
    elif base == "unbanid":
        if len(parts) < 2 or not RE_STEAM_ID.match(parts[1]):
            return False, "Steam ID inválido (17 dígitos)"
    elif base == "adduser":
        if len(parts) < 3 or not RE_USERNAME.match(parts[1]):
            return False, "Uso: adduser <username> <password>"
        if len(parts[2]) < 4 or len(parts[2]) > 64:
            return False, "Password debe tener 4-64 caracteres"
    elif base == "setaccesslevel":
        if len(parts) != 3:
            return False, "Uso: setaccesslevel <username> <role>"
        if not RE_USERNAME.match(parts[1]):
            return False, "Username inválido"
        if parts[2] not in VALID_ROLES:
            return False, f"Rol inválido: {parts[2]}. Válidos: {', '.join(sorted(VALID_ROLES))}"

    return True, "OK"


def docker_exec_rcon(command: str) -> tuple[bool, str]:
    try:
        status, data = docker_request("POST",
            f"/containers/{ALLOWED_CONTAINER}/exec",
            body=json.dumps({"AttachStdout": True, "AttachStderr": True,
                             "Cmd": ["rcon-cli", "-c", RCON_CONFIG, command]}))
        if status != 201:
            logger.warning(f"exec create falló: {status} {data[:200]}")
            return False, f"exec create failed: {status}"
        exec_id = json.loads(data).get("Id")
        if not exec_id:
            return False, "exec create: sin Id"

        status, data = docker_request("POST", f"/exec/{exec_id}/start",
            body=json.dumps({"Detach": False, "Tty": False}), timeout=30)
        if status != 200:
            logger.warning(f"exec start falló: {status}")
            return False, f"exec start failed: {status}"

        return True, data.strip()
    except Exception as e:
        logger.error(f"docker_exec_rcon error: {e}")
        return False, str(e)


def extract_container_name(path: str) -> str | None:
    match = re.search(r'/containers/([^/?]+)', path)
    return match.group(1) if match else None


def is_allowed(path: str) -> tuple[bool, str]:
    if path == '/_ping' or path.endswith('/_ping'):
        return True, "Ping"
    if path == '/rcon':
        return True, "RCON"
    if path.endswith('/containers/json') or path.endswith('/containers'):
        return True, "List"
    container = extract_container_name(path)
    if container:
        if container == ALLOWED_CONTAINER:
            return True, f"OK: {container}"
        return False, f"Bloqueado: {container}"
    return True, "General"


class ProxyHandler(BaseHTTPRequestHandler):
    def handle_request(self):
        allowed, reason = is_allowed(self.path)
        if not allowed:
            logger.warning(f"BLOQUEADO: {self.command} {self.path} - {reason}")
            self._send_json(403, {"message": f"Forbidden: {reason}"})
            return

        if self.path == '/rcon' and self.command == 'POST':
            self._handle_rcon()
            return

        logger.info(f"PERMITIDO: {self.command} {self.path} - {reason}")

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode() if content_length > 0 else None

            status, data = docker_request(self.command, self.path, body=body)

            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(data.encode())
        except Exception as e:
            logger.error(f"Error proxy: {e}")
            self._send_json(502, {"message": f"Proxy error: {e}"})

    def _handle_rcon(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            raw = self.rfile.read(content_length)
            body = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            self._send_json(400, {"message": "JSON inválido"})
            return

        command = body.get("command", "").strip()
        valid, msg = validate_rcon_command(command)
        if not valid:
            logger.warning(f"RCON rechazado: {msg} | cmd={command!r}")
            self._send_json(400, {"message": msg})
            return

        logger.info(f"RCON ejecutando: {command}")
        ok, output = docker_exec_rcon(command)
        if ok:
            logger.info(f"RCON resultado: {output[:200]}")
            self._send_json(200, {"output": output})
        else:
            logger.warning(f"RCON falló: {output}")
            self._send_json(502, {"message": output})

    def _send_json(self, code: int, data: dict):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self): self.handle_request()
    def do_POST(self): self.handle_request()
    def do_PUT(self): self.handle_request()
    def do_DELETE(self): self.handle_request()
    def do_HEAD(self): self.handle_request()

    def log_message(self, format, *args):
        logger.info(f"{self.client_address[0]} - {format % args}")


if __name__ == '__main__':
    logger.info(f"Iniciando proxy Docker en puerto {PROXY_PORT}")
    logger.info(f"Contenedor permitido: {ALLOWED_CONTAINER}")
    logger.info(f"RCON whitelist: {sorted(ALLOWED_RCON_COMMANDS)}")
    server = HTTPServer(('0.0.0.0', PROXY_PORT), ProxyHandler)
    server.serve_forever()
