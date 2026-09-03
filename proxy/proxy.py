import os
import re
import logging
from flask import Flask, request, Response
import requests_unixsocket

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

ALLOWED_CONTAINER = os.getenv("ALLOWED_CONTAINER", "project-zomboid")
DOCKER_SOCKET = "http+unix:///var/run/docker.sock"
PROXY_PORT = int(os.getenv("PROXY_PORT", "2375"))

session = requests_unixsocket.Session()

def extract_container_name(path: str) -> str | None:
    """Extraer nombre de contenedor de la URL de Docker API"""
    # Patrones comunes en Docker API:
    # /v1.42/containers/<name>/json
    # /v1.42/containers/<name>/start
    # /v1.42/containers/<name>/stop
    # /v1.42/containers/<name>/restart
    # /v1.42/containers/<name>/exec
    # /v1.42/exec/<id>/start
    
    match = re.search(r'/containers/([^/?]+)', path)
    if match:
        return match.group(1)
    
    return None

def is_allowed_operation(path: str, method: str) -> tuple[bool, str]:
    """Verificar si la operación está permitida"""
    
    # Permitir ping de healthcheck
    if path == '/_ping' or path.endswith('/_ping'):
        return True, "Ping permitido"
    
    # Permitir listar contenedores (necesario para verificar existencia)
    if path.endswith('/containers/json') or path.endswith('/containers'):
        return True, "Listar contenedores permitido"
    
    # Extraer nombre de contenedor
    container_name = extract_container_name(path)
    
    if container_name:
        if container_name == ALLOWED_CONTAINER:
            return True, f"Operación permitida en {container_name}"
        else:
            return False, f"Contenedor no permitido: {container_name}"
    
    # Si no hay nombre de contenedor, permitir (ej. /version, /info)
    return True, "Operación general permitida"

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD'])
def proxy(path):
    """Proxy para Docker API"""
    
    # Verificar si la operación está permitida
    allowed, reason = is_allowed_operation(path, request.method)
    
    if not allowed:
        logger.warning(f"BLOQUEADO: {request.method} {path} - {reason}")
        return Response(
            f'{{"message": "Forbidden: {reason}"}}',
            status=403,
            mimetype='application/json'
        )
    
    logger.info(f"PERMITIDO: {request.method} {path} - {reason}")
    
    # Reenviar petición al socket de Docker
    try:
        url = f"{DOCKER_SOCKET}/{path}"
        
        response = session.request(
            method=request.method,
            url=url,
            headers={k: v for k, v in request.headers if k.lower() != 'host'},
            data=request.get_data(),
            params=request.args,
            timeout=30
        )
        
        # Crear respuesta
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in response.raw.headers.items()
                   if name.lower() not in excluded_headers]
        
        return Response(response.content, response.status_code, headers)
    
    except Exception as e:
        logger.error(f"Error al reenviar petición: {e}")
        return Response(
            f'{{"message": "Proxy error: {str(e)}"}}',
            status=502,
            mimetype='application/json'
        )

if __name__ == '__main__':
    logger.info(f"Iniciando proxy Docker en puerto {PROXY_PORT}")
    logger.info(f"Contenedor permitido: {ALLOWED_CONTAINER}")
    app.run(host='0.0.0.0', port=PROXY_PORT, threaded=True)
