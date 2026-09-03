import os
import re
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import httpx

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ALLOWED_CONTAINER = os.getenv("ALLOWED_CONTAINER", "project-zomboid")
PROXY_PORT = int(os.getenv("PROXY_PORT", "2375"))

transport = httpx.HTTPTransport(uds="/var/run/docker.sock")
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
    return bool(re.match(r'/exec/[^/]+/start', path))

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
            
            # Manejar streaming para exec start
            if is_exec_start(self.path):
                logger.info(f"Streaming exec start: {self.path}")
                with client.stream(
                    method=self.command,
                    url=self.path,
                    headers=headers,
                    content=body
                ) as response:
                    self.send_response(response.status_code)
                    for name, value in response.headers.items():
                        if name.lower() not in ['content-encoding', 'content-length', 'transfer-encoding', 'connection']:
                            self.send_header(name, value)
                    self.end_headers()
                    
                    # Stream chunked response
                    for chunk in response.iter_bytes():
                        if chunk:
                            self.wfile.write(chunk)
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
