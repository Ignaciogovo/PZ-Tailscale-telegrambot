import os
import re
import logging
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
import httpx

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ALLOWED_CONTAINER = os.getenv("ALLOWED_CONTAINER", "project-zomboid")
PROXY_PORT = int(os.getenv("PROXY_PORT", "2375"))
DOCKER_SOCKET = "/var/run/docker.sock"

transport = httpx.HTTPTransport(uds=DOCKER_SOCKET)
client = httpx.Client(transport=transport, base_url="http://localhost", timeout=30.0)

def extract_container_name(path: str) -> str | None:
    match = re.search(r'/containers/([^/?]+)', path)
    return match.group(1) if match else None

def is_allowed(path: str) -> tuple[bool, str]:
    if path == '/_ping' or path.endswith('/_ping'):
        return True, "Ping"
    if path.endswith('/containers/json') or path.endswith('/containers'):
        return True, "List"
    container = extract_container_name(path)
    if container:
        if container == ALLOWED_CONTAINER:
            return True, f"OK: {container}"
        return False, f"Bloqueado: {container}"
    return True, "General"

def is_exec_start(path: str) -> bool:
    """Detectar si es un endpoint de exec start (streaming)"""
    return bool(re.search(r'/exec/[^/]+/start', path))

class ProxyHandler(BaseHTTPRequestHandler):
    def handle_request(self):
        allowed, reason = is_allowed(self.path)
        if not allowed:
            logger.warning(f"BLOQUEADO: {self.command} {self.path} - {reason}")
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(f'{{"message": "Forbidden: {reason}"}}'.encode())
            return
        
        logger.info(f"PERMITIDO: {self.command} {self.path} - {reason}")
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            headers = {k: v for k, v in self.headers.items() if k.lower() != 'host'}
            
            # Manejar hijacking para exec start
            if is_exec_start(self.path):
                logger.info(f"Hijacking exec start: {self.path}")
                logger.info(f"Headers recibidos del cliente: {dict(headers)}")
                self._handle_exec_hijack(headers, body)
            else:
                # Respuesta normal
                response = client.request(
                    method=self.command,
                    url=self.path,
                    headers=headers,
                    content=body
                )
                
                self.send_response(response.status_code)
                for name, value in response.headers.items():
                    if name.lower() not in ['content-encoding', 'content-length', 'transfer-encoding', 'connection']:
                        self.send_header(name, value)
                self.end_headers()
                self.wfile.write(response.content)
        except Exception as e:
            logger.error(f"Error: {e}")
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(f'{{"message": "Proxy error: {str(e)}"}}'.encode())
    
    def _handle_exec_hijack(self, headers, body):
        """Manejar HTTP hijacking para exec start"""
        docker_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        docker_sock.connect(DOCKER_SOCKET)
        
        try:
            # Construir petición HTTP con headers de upgrade requeridos por Docker
            request_line = f"{self.command} {self.path} HTTP/1.1\r\n"
            
            # Asegurar headers requeridos
            hijack_headers = {}
            for k, v in headers.items():
                hijack_headers[k] = v
            hijack_headers["Host"] = "localhost"
            hijack_headers["Connection"] = "Upgrade"
            hijack_headers["Upgrade"] = "tcp"
            if body:
                hijack_headers["Content-Length"] = str(len(body))
            
            header_lines = "".join(f"{k}: {v}\r\n" for k, v in hijack_headers.items())
            request = request_line + header_lines + "\r\n"
            
            logger.info(f"Enviando hijack request: {request_line.strip()}")
            
            docker_sock.sendall(request.encode())
            if body:
                docker_sock.sendall(body)
            
            # Leer respuesta HTTP de Docker
            response_data = b""
            while b"\r\n\r\n" not in response_data:
                chunk = docker_sock.recv(4096)
                if not chunk:
                    break
                response_data += chunk
            
            header_end = response_data.find(b"\r\n\r\n")
            if header_end == -1:
                raise Exception("Respuesta HTTP inválida de Docker")
            
            header_part = response_data[:header_end].decode()
            body_start = response_data[header_end + 4:]
            
            logger.info(f"Docker response: {header_part.split(chr(13))[0]}")
            
            # Enviar respuesta HTTP al cliente
            self.wfile.write(header_part.encode())
            self.wfile.write(b"\r\n\r\n")
            self.wfile.flush()
            
            # Enviar datos iniciales si existen
            if body_start:
                self.wfile.write(body_start)
                self.wfile.flush()
            
            # Leer output de Docker y enviar al cliente
            # Después del 101, Docker envía el output del comando y el cliente solo recibe
            while True:
                data = docker_sock.recv(4096)
                if not data:
                    break
                self.wfile.write(data)
                self.wfile.flush()
        
        finally:
            docker_sock.close()
    
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
    server = HTTPServer(('0.0.0.0', PROXY_PORT), ProxyHandler)
    server.serve_forever()
