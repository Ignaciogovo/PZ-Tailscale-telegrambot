# AntiCheat persistente y configuración de Skills

## 1. AntiCheat que se resetea al reiniciar

### Problema

Project Zomboid reescribe `<SERVER_NAME>.ini` al arrancar y resetea los valores `AntiCheat*=2` a sus defaults. Editar el archivo con el servidor parado no siempre persiste.

### Solución recomendada: editar con el servidor parado

1. Detener el servidor:
   ```bash
   docker compose stop projectzomboid
   ```
2. Editar `server-data/Server/<SERVER_NAME>.ini` y cambiar:
   ```ini
   AntiCheatSafety=0
   AntiCheatSpeed=0
   AntiCheatNoClip=0
   AntiCheatHit=0
   AntiCheatPacketException=0
   AntiCheatPermission=0
   AntiCheatXP=0
   AntiCheatSafeHouse=0
   AntiCheatPlayer=0
   AntiCheatChecksum=0
   ```
3. Arrancar:
   ```bash
   docker compose up -d projectzomboid
   ```

Si PZ sigue reseteando los valores, usar el script de post-arranque.

### Solución alternativa: script de post-arranque

Crear `scripts/fix-anticheat.sh` en el host:

```bash
#!/bin/bash
# Espera a que PZ genere el server.ini y fuerza valores
sleep 15
INI="/project-zomboid-config/Server/pzserver.ini"
[ -f "$INI" ] || exit 0
for key in Safety Speed NoClip Hit PacketException Permission XP SafeHouse Player Checksum; do
    sed -i "s/^AntiCheat${key}=.*/AntiCheat${key}=0/" "$INI"
done
```

Montarlo en `docker-compose.yml`:

```yaml
volumes:
  - ./scripts/fix-anticheat.sh:/home/steam/server/fix-anticheat.sh:ro
```

Y ejecutarlo manualmente tras el arranque:

```bash
docker compose exec projectzomboid bash /home/steam/server/fix-anticheat.sh
```

### Valores AntiCheat

| Valor | Significado |
|---|---|
| 0 | Desactivado |
| 2 | Advertencia / umbral bajo |
| 4 | Estricto |

---

## 2. Skills, puntos iniciales y traits

### Dónde se configuran

**NO** están en `server.ini`. Se configuran en:

```
server-data/Server/<SERVER_NAME>_SandboxVars.lua
```

### Variables principales

```lua
SandboxVars = SandboxVars or {}

-- Puntos libres al crear personaje
SandboxVars.CharacterFreePoints = 2

-- Puntos de traits gratuitos al crear personaje
SandboxVars.CharacterFreeTraitPoints = 4
```

### Traits bloqueados/prohibidos

```lua
-- Traits que los jugadores NO pueden seleccionar
SandboxVars.DisabledTraits = {
    -- "Organised",
    -- "Lucky",
}
```

### Respawn y muerte

```lua
SandboxVars.PlayerRespawnWithSelf = false       -- Respawn donde moriste
SandboxVars.SafehouseAllowRespawn = false       -- Respawn en safehouse
SandboxVars.DropOffWhiteListAfterDeath = false  -- Eliminar cuenta al morir
```

### Spawn regions

Archivo: `server-data/Server/<SERVER_NAME>_spawnregions.lua`

Define las regiones de spawn disponibles. Ejemplo mínimo:

```lua
SpawnRegions = {}
table.insert(SpawnRegions, {
    name = "Muldraugh",
    xMin = 10000, xMax = 14000,
    yMin = 8000,  yMax = 12000,
})
```

### Aplicar cambios

1. Editar con el servidor parado o en caliente (algunas variables requieren restart).
2. Reiniciar:
   ```bash
   docker compose restart projectzomboid
   ```

### Notas

- Los **perks/skills** (nivel de cada habilidad) se configuran en la creación del personaje por el jugador, no por el servidor.
- El servidor solo controla los **puntos disponibles** para repartir.
- Para dar perks iniciales específicos se necesita un mod Lua o comandos admin in-game.
