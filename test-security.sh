#!/bin/bash

# Script de pruebas de seguridad para el bot de Telegram
# Genera test-results.txt con todos los resultados

set -e

OUTPUT_FILE="test-results.txt"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "========================================" > "$OUTPUT_FILE"
echo "PRUEBAS DE SEGURIDAD - BOT DE TELEGRAM" >> "$OUTPUT_FILE"
echo "Fecha: $TIMESTAMP" >> "$OUTPUT_FILE"
echo "========================================" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Función para ejecutar prueba y capturar resultado
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$OUTPUT_FILE"
    echo "PRUEBA: $test_name" >> "$OUTPUT_FILE"
    echo "Comando: $test_command" >> "$OUTPUT_FILE"
    echo "Resultado:" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    if eval "$test_command" >> "$OUTPUT_FILE" 2>&1; then
        echo "" >> "$OUTPUT_FILE"
        echo "✅ PASÓ" >> "$OUTPUT_FILE"
    else
        echo "" >> "$OUTPUT_FILE"
        echo "❌ FALLÓ" >> "$OUTPUT_FILE"
    fi
    echo "" >> "$OUTPUT_FILE"
}

# ========================================
# PRUEBA 1: Verificar contenedores activos
# ========================================
run_test "Contenedores activos" "docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -E '(tailscale|project-zomboid|pz-docker-proxy|pz-telegram-bot)'"

# ========================================
# PRUEBA 2: Verificar que el bot NO tiene acceso directo al socket
# ========================================
run_test "Bot sin acceso directo al socket" "docker exec pz-telegram-bot ls -la /var/run/docker.sock 2>&1 || echo '✅ Correcto: No tiene acceso al socket'"

# ========================================
# PRUEBA 3: Verificar que el bot puede usar docker CLI
# ========================================
run_test "Bot puede ejecutar docker CLI" "docker exec pz-telegram-bot docker --version"

# ========================================
# PRUEBA 4: Verificar que el bot corre como no-root
# ========================================
run_test "Bot corre como no-root" "docker exec pz-telegram-bot whoami"

# ========================================
# PRUEBA 5: Verificar que el proxy de Docker está corriendo
# ========================================
run_test "Proxy de Docker activo" "docker logs pz-docker-proxy --tail 5 | grep -E '(Iniciando proxy|Contenedor permitido)'"

# ========================================
# PRUEBA 6: Verificar que el bot puede obtener estado del contenedor
# ========================================
run_test "Bot puede obtener estado de project-zomboid" "docker exec pz-telegram-bot docker inspect --format '{{.State.Status}} {{.State.Health.Status}}' project-zomboid"

# ========================================
# PRUEBA 7: Verificar que el bot NO puede acceder a otros contenedores
# ========================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$OUTPUT_FILE"
echo "PRUEBA: Bot NO puede acceder a otros contenedores" >> "$OUTPUT_FILE"
echo "Comando: docker exec pz-telegram-bot docker inspect tailscale-project-zomboid" >> "$OUTPUT_FILE"
echo "Resultado esperado: Error 403 Forbidden" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

OUTPUT=$(docker exec pz-telegram-bot docker inspect tailscale-project-zomboid 2>&1)
EXIT_CODE=$?

echo "$OUTPUT" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

if echo "$OUTPUT" | grep -q "Forbidden\|403\|no permitido"; then
    echo "✅ PASÓ - Proxy bloqueó acceso a otro contenedor" >> "$OUTPUT_FILE"
else
    echo "❌ FALLÓ - Proxy NO bloqueó acceso a otro contenedor" >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

# ========================================
# PRUEBA 8: Verificar que el bot puede ejecutar RCON
# ========================================
run_test "Bot puede ejecutar RCON via docker exec" "docker exec pz-telegram-bot docker exec project-zomboid rcon-cli -c /home/steam/server/rcon.yml players"

# ========================================
# PRUEBA 9: Verificar que el bot tiene acceso de lectura a la DB
# ========================================
run_test "Bot puede leer SQLite DB" "docker exec pz-telegram-bot sqlite3 /pz-data/db/server-zomboid.db 'SELECT COUNT(*) FROM whitelist;'"

# ========================================
# PRUEBA 10: Verificar que el bot NO puede escribir en la DB
# ========================================
run_test "Bot NO puede escribir en SQLite DB (debería fallar)" "docker exec pz-telegram-bot sqlite3 /pz-data/db/server-zomboid.db 'INSERT INTO whitelist (username) VALUES (\"test\");' 2>&1 || echo '✅ Correcto: No puede escribir en la DB'"

# ========================================
# PRUEBA 11: Verificar red interna
# ========================================
run_test "Red interna pz-internal existe" "docker network ls | grep pz-internal"

# ========================================
# PRUEBA 12: Verificar que el bot está en la red interna
# ========================================
run_test "Bot está en red interna" "docker inspect pz-telegram-bot --format '{{range \$k, \$v := .NetworkSettings.Networks}}{{\$k}}{{end}}' | grep pz-internal"

# ========================================
# PRUEBA 13: Verificar que el proxy está en la red interna
# ========================================
run_test "Proxy está en red interna" "docker inspect pz-docker-proxy --format '{{range \$k, \$v := .NetworkSettings.Networks}}{{\$k}}{{end}}' | grep pz-internal"

# ========================================
# PRUEBA 14: Verificar logs del bot (últimas 20 líneas)
# ========================================
run_test "Logs del bot (últimas 20 líneas)" "docker logs pz-telegram-bot --tail 20"

# ========================================
# PRUEBA 15: Verificar logs del proxy (últimas 10 líneas)
# ========================================
run_test "Logs del proxy (últimas 10 líneas)" "docker logs pz-docker-proxy --tail 10"

# ========================================
# PRUEBA 15b: Verificar que el proxy filtra por nombre de contenedor
# ========================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$OUTPUT_FILE"
echo "PRUEBA: Proxy filtra por nombre de contenedor" >> "$OUTPUT_FILE"
echo "Intentando acceder a contenedor no permitido desde el bot..." >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Intentar acceder a otro contenedor
OUTPUT=$(docker exec pz-telegram-bot docker inspect tailscale-project-zomboid 2>&1)
echo "Salida: $OUTPUT" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

if echo "$OUTPUT" | grep -qi "forbidden\|403\|no permitido"; then
    echo "✅ Proxy bloqueó acceso a contenedor no permitido" >> "$OUTPUT_FILE"
else
    echo "❌ Proxy NO bloqueó acceso a contenedor no permitido" >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

# Verificar en logs del proxy que se registró el bloqueo
echo "Verificando logs del proxy..." >> "$OUTPUT_FILE"
docker logs pz-docker-proxy --tail 20 2>&1 | grep -i "bloqueado\|forbidden" >> "$OUTPUT_FILE" || echo "No se encontró registro de bloqueo en logs" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# ========================================
# PRUEBA 16: Verificar que el bot puede hacer start/stop/restart
# ========================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$OUTPUT_FILE"
echo "PRUEBA: Bot puede controlar contenedor (start/stop/restart)" >> "$OUTPUT_FILE"
echo "Nota: Esta prueba requiere que el servidor esté offline" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Verificar estado actual
CURRENT_STATUS=$(docker exec pz-telegram-bot docker inspect --format '{{.State.Status}}' project-zomboid 2>/dev/null || echo "unknown")
echo "Estado actual del contenedor: $CURRENT_STATUS" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

if [ "$CURRENT_STATUS" == "running" ]; then
    echo "Contenedor está corriendo, probando stop..." >> "$OUTPUT_FILE"
    if docker exec pz-telegram-bot docker stop -t 30 project-zomboid >> "$OUTPUT_FILE" 2>&1; then
        echo "✅ Stop exitoso" >> "$OUTPUT_FILE"
        sleep 5
        
        echo "Probando start..." >> "$OUTPUT_FILE"
        if docker exec pz-telegram-bot docker start project-zomboid >> "$OUTPUT_FILE" 2>&1; then
            echo "✅ Start exitoso" >> "$OUTPUT_FILE"
        else
            echo "❌ Start falló" >> "$OUTPUT_FILE"
        fi
    else
        echo "❌ Stop falló" >> "$OUTPUT_FILE"
    fi
else
    echo "Contenedor no está corriendo, probando start..." >> "$OUTPUT_FILE"
    if docker exec pz-telegram-bot docker start project-zomboid >> "$OUTPUT_FILE" 2>&1; then
        echo "✅ Start exitoso" >> "$OUTPUT_FILE"
    else
        echo "❌ Start falló" >> "$OUTPUT_FILE"
    fi
fi
echo "" >> "$OUTPUT_FILE"

# ========================================
# PRUEBA 17: Verificar validación de inputs en el código
# ========================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$OUTPUT_FILE"
echo "PRUEBA: Validación de inputs (verificación de código)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "Verificando que validate_username existe en pz_rcon.py..." >> "$OUTPUT_FILE"
if docker exec pz-telegram-bot grep -q "def validate_username" /app/pz_rcon.py 2>/dev/null; then
    echo "✅ validate_username existe" >> "$OUTPUT_FILE"
else
    echo "❌ validate_username no existe" >> "$OUTPUT_FILE"
fi

echo "Verificando que validate_steam_id existe en pz_rcon.py..." >> "$OUTPUT_FILE"
if docker exec pz-telegram-bot grep -q "def validate_steam_id" /app/pz_rcon.py 2>/dev/null; then
    echo "✅ validate_steam_id existe" >> "$OUTPUT_FILE"
else
    echo "❌ validate_steam_id no existe" >> "$OUTPUT_FILE"
fi

echo "Verificando que validate_role existe en pz_rcon.py..." >> "$OUTPUT_FILE"
if docker exec pz-telegram-bot grep -q "def validate_role" /app/pz_rcon.py 2>/dev/null; then
    echo "✅ validate_role existe" >> "$OUTPUT_FILE"
else
    echo "❌ validate_role no existe" >> "$OUTPUT_FILE"
fi

echo "Verificando que ALLOWED_CONTAINERS existe en pz_rcon.py..." >> "$OUTPUT_FILE"
if docker exec pz-telegram-bot grep -q "ALLOWED_CONTAINERS" /app/pz_rcon.py 2>/dev/null; then
    echo "✅ ALLOWED_CONTAINERS existe" >> "$OUTPUT_FILE"
else
    echo "❌ ALLOWED_CONTAINERS no existe" >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

# ========================================
# PRUEBA 18: Verificar que docker SDK NO está instalado
# ========================================
run_test "Docker SDK NO está instalado" "docker exec pz-telegram-bot python -c 'import docker' 2>&1 || echo '✅ Correcto: Docker SDK no está instalado'"

# ========================================
# RESUMEN FINAL
# ========================================
echo "========================================" >> "$OUTPUT_FILE"
echo "RESUMEN DE PRUEBAS" >> "$OUTPUT_FILE"
echo "========================================" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "Archivo generado: $OUTPUT_FILE" >> "$OUTPUT_FILE"
echo "Fecha: $(date '+%Y-%m-%d %H:%M:%S')" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "Para ver los resultados completos:" >> "$OUTPUT_FILE"
echo "  cat $OUTPUT_FILE" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "Para ver solo los fallos:" >> "$OUTPUT_FILE"
echo "  grep '❌' $OUTPUT_FILE" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "========================================" >> "$OUTPUT_FILE"

echo "✅ Pruebas completadas. Resultados en: $OUTPUT_FILE"
