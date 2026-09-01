# Resetear el servidor (empezar mundo nuevo)

## Opción 1: Reset completo (mundo + personajes)

### 1. Detener el servidor

```bash
docker compose stop projectzomboid
```

### 2. Borrar saves y datos del mundo

```bash
sudo rm -rf /srv/data/project-zomboid/server-data/Saves/*
```

### 3. Cambiar ResetID

Edita `server-data/Server/<SERVER_NAME>.ini`:

```ini
# Genera un número aleatorio entre 1 y 2147483647
ResetID=123456789
```

Esto fuerza a todos los jugadores a crear un personaje nuevo al conectarse.

### 4. Arrancar el servidor

```bash
docker compose up -d projectzomboid
```

El servidor generará un mundo nuevo desde cero.

---

## Opción 2: Reset suave (solo personajes, mantener mundo)

Si quieres mantener el mundo pero forzar a los jugadores a empezar de nuevo:

### 1. Detener el servidor

```bash
docker compose stop projectzomboid
```

### 2. Cambiar ResetID

Edita `server-data/Server/<SERVER_NAME>.ini`:

```ini
ResetID=987654321
```

### 3. Arrancar

```bash
docker compose up -d projectzomboid
```

Los jugadores deberán crear personajes nuevos, pero el mundo (edificios modificados, objetos, etc.) se mantiene.

---

## Opción 3: Reset total (incluyendo configuración)

Para empezar completamente de cero, como si fuera la primera vez:

```bash
# Detener
docker compose stop projectzomboid

# Borrar TODO
sudo rm -rf /srv/data/project-zomboid/server-data/*

# Arrancar (regenerará todo)
docker compose up -d projectzomboid
```

**Advertencia:** Esto borra:
- Saves del mundo
- Configuración del servidor (server.ini)
- Configuración de sandbox (SandboxVars.lua)
- Mods descargados
- Whitelist de jugadores

Tendrás que reconfigurar mods, server.ini, etc. desde cero.

---

## Estructura de datos

```
/srv/data/project-zomboid/server-data/
├── Server/
│   ├── pzserver.ini              ← Configuración principal
│   ├── pzserver_SandboxVars.lua  ← Configuración del mundo
│   └── pzserver_spawnregions.lua ← Regiones de spawn
├── Saves/
│   └── Multiplayer/
│       └── <SERVER_NAME>/        ← Mundo guardado
└── Workshop/                     ← Mods descargados
```

---

## Backup antes de reset

Siempre haz backup antes de resetear:

```bash
# Backup completo
sudo tar -czf /tmp/pz-backup-$(date +%Y%m%d-%H%M%S).tar.gz \
  -C /srv/data/project-zomboid .

# Solo saves
sudo tar -czf /tmp/pz-saves-$(date +%Y%m%d-%H%M%S).tar.gz \
  -C /srv/data/project-zomboid/server-data/Saves .
```

---

## Notas

- **ResetID**: Si este número cambia, los clientes deben crear un personaje nuevo.
- **ServerPlayerID**: Identifica el servidor. Cámbialo solo si quieres invalidar personajes de otros servidores.
- Los jugadores perderán sus personajes, safehouses, y progreso.
- Los mods se descargan automáticamente al arrancar si están en `WorkshopItems=`.
