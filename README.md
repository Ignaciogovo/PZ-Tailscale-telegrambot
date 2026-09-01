# Servidor Project Zomboid Docker + Tailscale

Servidor dedicado de Project Zomboid B42 con acceso privado mediante Tailscale.

## Arquitectura

```
Internet
   │
   X  ← NO acceso directo
   │
Tailscale (tailnet privada)
   │
   ├── tailscale container
   │     hostname: project_projectz-pollito
   │     IP: 100.x.y.z
   │     │
   │     └── projectzomboid container (network_mode: service:tailscale)
   │           ├── UDP 16261 ← juego
   │           ├── UDP 16262 ← Steam direct
   │           └── TCP 27015 ← RCON
   │
   └── Jugadores con Tailscale
         → Conectan a 100.x.y.z:16261
```

## Estructura de directorios

```
/srv/contenedores/project-zomboid/
├── docker-compose.yml
└── .env

/srv/data/project-zomboid/
├── tailscale/              ← Estado de Tailscale (NO TOCAR)
├── server-files/           ← Archivos del juego
└── server-data/            ← Configuración y datos
    ├── Server/
    │   ├── <SERVER_NAME>.ini
    │   └── <SERVER_NAME>_SandboxVars.lua
    ├── Workshop/           ← Mods descargados
    └── Saves/              ← Partidas guardadas
```

## Requisitos

- Docker y Docker Compose instalados
- Cuenta de Tailscale (gratuita)
- 4 GB RAM mínimo (8 GB recomendado)
- 10 GB disco

## Instalación rápida

```bash
# 1. Crear directorios
sudo mkdir -p /srv/contenedores/project-zomboid
sudo mkdir -p /srv/data/project-zomboid/{server-files,server-data}
sudo chown -R 1000:1000 /srv/data/project-zomboid

# 2. Copiar archivos
cp docker-compose.yml /srv/contenedores/project-zomboid/
cp .env.example /srv/contenedores/project-zomboid/.env

# 3. Editar .env (cambiar contraseñas)
nano /srv/contenedores/project-zomboid/.env

# 4. Arrancar
cd /srv/contenedores/project-zomboid
docker compose pull
docker compose up -d

# 5. Ver logs (esperar "LuaNet: Initialization [DONE]")
docker compose logs -f projectzomboid
```

## Configuración de mods

Editar `server-data/Server/<SERVER_NAME>.ini`:

```ini
Mods=damnlib;NeatUI_Framework;...
WorkshopItems=3171167894;3508537032;...
DoLuaChecksum=false
```

Reiniciar: `docker compose restart projectzomboid`

## Conectar al servidor

```bash
# Obtener IP de Tailscale
docker compose exec tailscale tailscale ip -4
```

En Project Zomboid: **Join → Favorites → Add**
- IP: `100.x.y.z` (la IP de Tailscale)
- Puerto: `16261`

El jugador debe tener Tailscale instalado y los mismos mods suscritos en Steam Workshop.

## Documentación

- [Configuración y mods](docs/configuracion.md)
- [AntiCheat y Skills](docs/anticheat-y-skills.md)
- [Resetear servidor](docs/reset-servidor.md)
- [Troubleshooting](docs/troubleshooting.md)

## Créditos

Basado en [indifferentbroccoli/projectzomboid-server-docker](https://github.com/indifferentbroccoli/projectzomboid-server-docker)
