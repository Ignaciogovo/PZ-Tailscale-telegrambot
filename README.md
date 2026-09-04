# Project Zomboid + Tailscale + Telegram Bot

Servidor de Project Zomboid B42 accesible desde cualquier lugar
sin port-forwarding, administrable vía Telegram.

## Requisitos

- Docker + Docker Compose
- Cuenta de Tailscale (gratis)
- Bot de Telegram (crear con @BotFather)

## Paso 1: Configurar

```bash
git clone <url-del-repo>
cd projectzomboid-docker-tailscale-telegrambot
cp .env.example .env
```

Edita `.env` y cambia:

| Variable | Qué poner |
|----------|-----------|
| `RCON_PASSWORD` | Contraseña RCON del servidor |
| `ADMIN_PASSWORD` | Contraseña de administrador |
| `TELEGRAM_BOT_TOKEN` | Token de @BotFather |
| `TELEGRAM_CHAT_ID` | Tu ID de chat de Telegram |

## Paso 2: Arrancar Tailscale

```bash
docker compose up -d tailscale
```

Abre los logs y busca la URL de autenticación:

```bash
docker compose logs -f tailscale
```

Abre la URL en tu navegador, inicia sesión con tu cuenta
de Tailscale y acepta la autenticación.

## Paso 3: Arrancar el servidor

Una vez autenticado Tailscale:

```bash
docker compose up -d
```

Arrancan: Project Zomboid, Telegram Bot y Docker Proxy.

## Paso 4: Verificar

```bash
docker compose ps
docker compose logs -f projectzomboid
```

Cuando veas `*** SERVER STARTED ***`, el servidor está listo.
Conéctate desde el cliente de Project Zomboid usando la IP
de Tailscale del servidor.

## Uso diario

| Acción | Comando |
|--------|---------|
| Ver estado | `docker compose ps` |
| Ver logs | `docker compose logs -f projectzomboid` |
| Apagar | `docker compose stop projectzomboid` |
| Reiniciar | `docker compose restart projectzomboid` |
| Reiniciar mundo | `./scripts/reset-server.sh` |

## Admin vía Telegram

El bot permite:

- Ver estado del servidor
- Listar jugadores conectados
- Kickear/banear jugadores
- Cambiar roles
- Arrancar/apagar/reiniciar el servidor
- Guardar la partida

## Seguridad

- **Tailscale**: sin ports expuestos al exterior
- **Docker Proxy**: el bot solo controla el contenedor de PZ
- **Input validación**: previene inyección de comandos

## Estructura

```
├── docker-compose.yml    ← 4 servicios
├── .env.example          ← plantilla de configuración
├── scripts/
│   └── reset-server.sh   ← reiniciar mundo/personajes
├── bot/                  ← Telegram bot
├── proxy/                ← Docker socket proxy
└── docs/                 ← documentación técnica
```

## Créditos

Basado en [indifferentbroccoli/projectzomboid-server-docker](https://github.com/indifferentbroccoli/projectzomboid-server-docker)
