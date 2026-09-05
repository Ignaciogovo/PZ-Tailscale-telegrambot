#!/bin/bash
set -e

echo "========================================="
echo "  RESET PROJECT ZOMBOID"
echo "========================================="

# --- Detectar docker-compose.yml ---
COMPOSE_FILE=""
for CANDIDATE in \
    "$(pwd)/docker-compose.yml" \
    "$(dirname "$0")/../docker-compose.yml"; do
    if [ -f "$CANDIDATE" ]; then
        COMPOSE_FILE="$CANDIDATE"
        break
    fi
done

if [ -z "$COMPOSE_FILE" ]; then
    echo "No se encontró docker-compose.yml en:"
    echo "  - $(pwd)"
    echo "  - $(dirname "$0")"
    echo ""
    read -p "Ruta completa al docker-compose.yml: " COMPOSE_FILE
fi

if [ ! -f "$COMPOSE_FILE" ]; then
    echo "Error: $COMPOSE_FILE no existe."
    exit 1
fi

COMPOSE_FILE="$(realpath "$COMPOSE_FILE")"
COMPOSE_DIR="$(dirname "$COMPOSE_FILE")"

echo ""
echo "docker-compose.yml: $COMPOSE_FILE"
echo "Directorio: $COMPOSE_DIR"

# --- Preguntar ruta ---
echo ""
read -p "¿Es la ruta correcta? [s/N]: " ROUTE_OK
if [ "$ROUTE_OK" != "s" ] && [ "$ROUTE_OK" != "S" ]; then
    read -p "Ruta completa al docker-compose.yml: " COMPOSE_FILE
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo "Error: $COMPOSE_FILE no existe."
        exit 1
    fi
    COMPOSE_FILE="$(realpath "$COMPOSE_FILE")"
    COMPOSE_DIR="$(dirname "$COMPOSE_FILE")"
fi

# --- Parsear volume mount del host ---
HOST_DATA_PATH=""

# Método 1: docker compose config (resuelve rutas absolutas)
if command -v docker &>/dev/null; then
    HOST_DATA_PATH=$(docker compose -f "$COMPOSE_FILE" config --format json 2>/dev/null | \
        jq -r '.services.projectzomboid.volumes[] | select(.target == "/project-zomboid-config") | .source' 2>/dev/null)
    if [ -z "$HOST_DATA_PATH" ]; then
        echo "  Aviso: docker compose config no pudo resolver rutas, usando fallback..."
    fi
fi

# Método 2: grep por línea que contiene /project-zomboid-config (absoluta o relativa)
if [ -z "$HOST_DATA_PATH" ]; then
    HOST_DATA_PATH=$(grep -m1 '/project-zomboid-config' "$COMPOSE_FILE" | sed 's/^ *- //' | sed 's/:.*//')
fi

# Método 3: grep por server-data (absoluta o relativa)
if [ -z "$HOST_DATA_PATH" ]; then
    HOST_DATA_PATH=$(grep -m1 'server-data:' "$COMPOSE_FILE" | sed 's/^ *- //' | sed 's/:.*//')
    if [[ "$HOST_DATA_PATH" != /* ]]; then
        HOST_DATA_PATH="$COMPOSE_DIR/$HOST_DATA_PATH"
    fi
fi

if [ -z "$HOST_DATA_PATH" ]; then
    echo "Error: No se pudo determinar la ruta de datos del servidor."
    echo "  No se encontró '/project-zomboid-config' ni 'server-data:' en $COMPOSE_FILE"
    exit 1
fi
HOST_DATA_PATH="$(realpath "$HOST_DATA_PATH")"

SAVES_PATH="$HOST_DATA_PATH/Saves/Multiplayer"

# --- Obtener nombre del servidor ---
# Método 1: buscar .ini en Server/ y leer ServerName
SERVER_INI=""
SERVER_NAME=""
INI_FILE=$(find "$HOST_DATA_PATH/Server" -maxdepth 1 -name "*.ini" 2>/dev/null | head -1)
if [ -n "$INI_FILE" ]; then
    SERVER_INI="$INI_FILE"
    SERVER_NAME=$(grep '^ServerName=' "$INI_FILE" 2>/dev/null | cut -d= -f2)
fi

# Método 2: fallback a .env
if [ -z "$SERVER_NAME" ]; then
    if [ -f "$COMPOSE_DIR/.env" ]; then
        SERVER_NAME=$(grep '^SERVER_NAME=' "$COMPOSE_DIR/.env" | cut -d= -f2)
    fi
fi
if [ -z "$SERVER_NAME" ]; then
    SERVER_NAME="server-zomboid"
fi

# Si no encontramos .ini, construir ruta por defecto
if [ -z "$SERVER_INI" ]; then
    SERVER_INI="$HOST_DATA_PATH/Server/$SERVER_NAME.ini"
fi

echo ""
echo "Ruta datos servidor: $HOST_DATA_PATH"
echo "Server INI: $SERVER_INI"
echo "Saves: $SAVES_PATH"

# Verificar que el server.ini existe
if [ ! -f "$SERVER_INI" ]; then
    echo "Error: $SERVER_INI no encontrado."
    exit 1
fi

SAVE_WORLD="$SAVES_PATH/$SERVER_NAME"

echo "World save: $SAVE_WORLD"

# --- Menú ---
echo ""
echo "Opciones:"
echo "  1) Solo personajes (mundo se mantiene)"
echo "  2) Mundo + personajes (reset completo)"
echo ""
read -p "Elige una opción [1/2]: " OPTION

echo ""
if [ "$OPTION" = "1" ]; then
    echo "Se cambiará el ResetID. Los jugadores deberán crear personajes nuevos."
    echo "El mundo (edificios, objetos, mapas) se mantiene."
elif [ "$OPTION" = "2" ]; then
    echo "Se BORRARÁN todos los saves del mundo."
    echo "Se generará un mundo nuevo desde cero."
else
    echo "Opción no válida. Saliendo."
    exit 1
fi

read -p "¿Confirmar? [s/N]: " CONFIRM
if [ "$CONFIRM" != "s" ] && [ "$CONFIRM" != "S" ]; then
    echo "Cancelado."
    exit 0
fi

# --- Ejecutar reset ---
echo ""
echo "[1/4] Deteniendo servidor..."
cd "$COMPOSE_DIR" && docker compose stop projectzomboid

echo "[2/4] Leyendo ResetID actual..."
OLD_RESET=$(grep "^ResetID=" "$SERVER_INI" | cut -d= -f2)
echo "  ResetID anterior: $OLD_RESET"

if [ "$OPTION" = "2" ]; then
    echo "[3/4] Borrando saves del mundo..."
    rm -rf "$SAVE_WORLD"/*
    echo "  Saves eliminados."
else
    echo "[3/4] Saves conservados (solo personajes)."
fi

NEW_RESET_ID=$((RANDOM * RANDOM % 2147483647 + 1))
echo "[4/4] Nuevo ResetID: $NEW_RESET_ID"
sed -i "s/^ResetID=.*/ResetID=$NEW_RESET_ID/" "$SERVER_INI"

echo ""
echo "Arrancando servidor..."
cd "$COMPOSE_DIR" && docker compose up -d projectzomboid

echo ""
echo "========================================="
echo "  COMPLETADO"
echo "========================================="
echo "  ResetID: $OLD_RESET → $NEW_RESET_ID"
if [ "$OPTION" = "2" ]; then
    echo "  Mundo: BORRADO (nuevo al arrancar)"
else
    echo "  Mundo: CONSERVADO"
fi
echo "  Jugadores: deberán crear personaje nuevo"
echo "========================================="
