# Configuración

## Variables de entorno

Ver [documentación upstream](https://github.com/indifferentbroccoli/projectzomboid-server-docker#environment-variables) para la lista completa.

Variables clave en `.env`:
- `MEMORY_XMX_GB` / `MEMORY_XMS_GB` — memoria JVM
- `ADMIN_PASSWORD` / `RCON_PASSWORD` — credenciales
- `SERVER_NAME` — nombre interno del servidor
- `MAX_PLAYERS` — máximo jugadores

## Archivos de configuración

Se generan automáticamente en `server-data/Server/`:

### `<SERVER_NAME>.ini`

Configuración principal: puertos, contraseñas, mods, opciones de juego.

### `<SERVER_NAME>_SandboxVars.lua`

Configuración del mundo: zombies, loot, clima, etc.

Se editan directamente mientras el servidor está detenido.

## Mods

### Cómo funcionan

La imagen de indifferentbroccoli **NO tiene variables de entorno para mods**.

Los mods se configuran **manualmente** editando `server-data/Server/<SERVER_NAME>.ini`:

```ini
Mods=damnlib;NeatUI_Framework;ShelterHold_Beehive;Buttstroke
WorkshopItems=3171167894;3508537032;3596827035;3394044313
DoLuaChecksum=false
```

### Orden de carga

Las librerías deben ir primero:

1. `damnlib` (3171167894)
2. `StarlitLibrary` (3378285185)
3. `MoodleFramework` (3396446795)
4. `NeatUI_Framework` (3508537032)
5. Mods de gameplay
6. Mods de música (TrueMoozic + packs)

### Descarga automática

Project Zomboid descarga los mods automáticamente al arrancar usando su conexión a Steam.

### Actualizar mods

Los mods se actualizan cuando el servidor arranca. Para forzar:

```bash
docker compose restart projectzomboid
```

### DoLuaChecksum=false

Requerido por mods como TrueMoozic. Sin esto, los clientes serán expulsados con error de checksum.

### Mods del cliente

Los jugadores deben tener los mismos mods suscritos en Steam Workshop.

## Memoria

| Host RAM | MEMORY_XMX_GB | MEMORY_XMS_GB | mem_limit |
|---|---|---|---|
| 8 GB | 4 | 2 | 5g |
| 12 GB | 6 | 4 | 8g |
| 16 GB | 8 | 6 | 12g |

## Actualizar servidor

```bash
cd /srv/contenedores/project-zomboid
docker compose pull
docker compose up -d
```
