# Troubleshooting

## Servidor no arranca

```bash
docker compose logs projectzomboid | tail -50
```

Causas comunes:
- Puerto en uso: `sudo lsof -i :16261`
- Memoria insuficiente: reducir `MEMORY_XMX_GB`
- Permisos: `sudo chown -R 1000:1000 /srv/data/project-zomboid`

## No puedo conectar desde el cliente

1. Verificar servidor corriendo: `docker compose ps`
2. Verificar logs: `docker compose logs projectzomboid`
3. Esperar inicialización: `LuaNet: Initialization [DONE]`
4. Verificar Tailscale: `docker compose exec tailscale tailscale status`
5. **Verificar versiones**: Cliente y servidor deben tener la misma versión de PZ

### Verificar versión del servidor

```bash
docker compose logs projectzomboid | grep -i "build\|version\|42\." | head -10
```

### Verificar versión del cliente

En Project Zomboid: menú principal → abajo a la derecha

Ambas deben ser **exactamente iguales** (ej: ambos 42.34).

### Síntomas de incompatibilidad de versión

- Error "nombre de usuario desconocido"
- Warning: `No packet handler for type: ...`
- Cliente se conecta pero es desconectado inmediatamente

## Error "La versión de la workshop es diferente a la del servidor"

Un mod del Workshop se actualizó mientras el servidor estaba en marcha. El servidor mantiene la versión antigua cacheada.

**Solución**: Reiniciar el servidor para que descargue la nueva versión:

```bash
docker compose restart projectzomboid
```

## Mods no se descargan

```bash
# Verificar USE_STEAM=true en .env
grep "USE_STEAM" /srv/contenedores/project-zomboid/.env

# Ver logs de descarga
docker compose logs projectzomboid | grep -i "workshop\|download"

# Reiniciar
docker compose restart projectzomboid
```

## Mods no se cargan

```bash
# Verificar server.ini
cat "/srv/data/project-zomboid/server-data/Server/<SERVER_NAME>.ini" | grep -E "Mods|WorkshopItems"

# Verificar orden (dependencias primero)
# Reiniciar
docker compose restart projectzomboid
```

## Clientes expulsados con error de checksum

```bash
# Verificar DoLuaChecksum=false
grep "DoLuaChecksum" "/srv/data/project-zomboid/server-data/Server/<SERVER_NAME>.ini"

# Si no está o está en true, cambiar a false y reiniciar
docker compose restart projectzomboid
```

## Tailscale no conecta

```bash
docker compose logs tailscale
docker compose exec tailscale tailscale status
```

Si es necesario re-autenticar:
```bash
docker compose down
sudo rm -rf /srv/data/project-zomboid/tailscale
docker compose up -d
# Seguir el enlace de autenticación en los logs
```

## Error de permisos

```bash
sudo chown -R 1000:1000 /srv/data/project-zomboid
```

## Servidor consume mucha RAM

El JVM usa ~20-30% más que `MEMORY_XMX_GB` (metaspace, JIT, buffers).

- Reducir `MEMORY_XMX_GB` en `.env`
- Ajustar `mem_limit` en `docker-compose.yml`
