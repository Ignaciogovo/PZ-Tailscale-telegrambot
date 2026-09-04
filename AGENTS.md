# AGENTS.md

## Contexto del proyecto
Servidor dedicado de Project Zomboid B42 accesible desde cualquier lugar y gestionable vía Telegram.

**Por qué**: Permite jugar con amigos sin depender de port-forwarding ni IPs estáticas (Tailscale), y administrar el servidor desde el móvil sin acceder a la consola del host (Telegram Bot).

**Stack** (4 servicios Docker en `docker-compose.yml`, config vía `.env`):

- **Project Zomboid** (B42): Servidor dedicado de juego. Imagen `indifferentbroccoli/projectzomboid-server-docker`. Datos en `./data/project-zomboid/`. Máx 8 jugadores, 2-5 GB RAM. Mods vía Steam Workshop.
- **Tailscale**: Acceso externo a la red del servidor. Contenedor de red compartido (`network_mode: service:tailscale`). Autenticación vía `TAILSCALE_AUTHKEY`.
- **Docker Socket Proxy**: Proxy personalizado en `proxy/` que filtra todas las operaciones de Docker. Solo permite operaciones sobre el contenedor `project-zomboid`. Bloquea acceso a cualquier otro contenedor del host.
- **Telegram Bot**: Administración remota (arrancar/apagar/reiniciar, gestionar jugadores). Bot Python en `bot/`. Comunica con PZ vía RCON (`127.0.0.1:27015`) y con Docker vía proxy. Auth por `TELEGRAM_CHAT_ID`.

Arquitectura de red: PZ comparte red con Tailscale. Bot y proxy están en red interna aislada (`pz-internal`).

- **Repositorio upstream**: `indifferentbroccoli/projectzomboid-server-docker` guardado en `pz-docker/` como referencia. Consultar para entender Dockerfile, scripts, variables de entorno. Ver `pz-docker/VERSION.md` para versión del commit sincronizado. Actualizar cuando se quiera sincronizar con la imagen oficial.
- **Script de reset**: `scripts/reset-server.sh` reinicia el mundo/personajes desde el host. Detecta `docker-compose.yml` automáticamente, pregunta ruta y tipo de reset (solo personajes o mundo completo). Opera directamente sobre archivos del host sin `docker compose exec`.
- **Guía de usuario**: `README.md` contiene la guía de instalación para usuarios finales (clonar, configurar `.env`, arrancar Tailscale, autenticar, arrancar el resto).

### Medidas de seguridad del bot de Telegram
El bot necesita acceso a Docker para arrancar/parar/reiniciar el contenedor de PZ. Esto implica riesgos de seguridad que se mitigaron así:

**Problema**: Socket de Docker directo = control total del host. Si el bot era comprometido, un atacante podía leer secrets de TODOS los contenedores del host, ejecutar comandos en cualquiera, o escapar al host.

**Solución**: Proxy personalizado (`proxy/`) que filtra operaciones POR NOMBRE DE CONTENEDOR. Solo permite operaciones sobre `project-zomboid`. Cualquier otro contenedor es bloqueado con HTTP 403.

**Medidas implementadas**:
1. **Proxy de Docker**: Bot no tiene acceso directo al socket. Proxy filtra por nombre de contenedor (solo `project-zomboid`)
2. **Validación de inputs**: Usernames, Steam IDs y roles validados con regex estrictos (previene inyección de comandos)
3. **No-root**: Bot corre como usuario no-root (`botuser`). Proxy necesita root para acceder al socket de Docker.
4. **Red aislada**: Bot y proxy en red interna (`pz-internal`), separada de Tailscale

**Por qué**: Si el chat de Telegram es comprometido, el atacante solo puede controlar PZ, no el host ni otros contenedores.

---


## 1. Flujo de Trabajo por Fases

### Estructura de Ramas
- `master` → producción estable
- `develop` → integración de fases completadas
- `feature/fase-X-descripcion` → desarrollo de cada fase

### Proceso por Fase
1. Crear rama `feature/fase-X-descripcion` desde `develop`
2. Dividir fase en **todos** específicos (el usuario los define)
3. Trabajar cada todo con autonomía
4. Al completar un todo → preguntar antes de continuar
5. Al completar la fase → esperar validación explícita del usuario
6. Validación completada → merge a `develop`

### Regla de Oro
**Ninguna fase está completa hasta que el usuario lo confirme explícitamente.**
Sin validación del usuario = sin merge, sin avanzar.

---

## 2. Autonomía y Comunicación

### Dentro de un Todo
- **Autonomía total** para implementar
- Tomar decisiones técnicas (estructura, librerías, patrones)
- Hacer commits intermedios si es necesario

### Entre Todos o Fases
- **OBLIGATORIO preguntar** antes de:
  - Pasar al siguiente todo
  - Iniciar nueva fase
  - Cambiar arquitectura o diseño
  - Modificar archivos críticos sin contexto

### Planes Detallados
- **Siempre mostrar plan detallado antes de ejecutar**
- Incluir: qué se va a hacer, por qué, archivos afectados
- Esperar confirmación antes de proceder

---

## 3. Reglas de seguridad
- Nunca hardcodear secretos, tokens o credenciales en el código.
- Nunca hacer commit de archivos `.env`.
- Antes de instalar una dependencia nueva, verificar que sea necesaria y de fuente confiable.
- No ejecutar `git push --force` sobre ramas compartidas (`master`/`develop`) sin confirmación explícita.

## 4. Uso de herramientas
- Usar **codebase-memory-mcp** para preguntas estructurales (dónde se llama X, impacto de cambiar Y)
  en vez de grep/leer archivo por archivo cuando el proyecto ya esté indexado.
- **Ponytail** está activo en modo `full` por defecto: prioriza soluciones simples,
  evita añadir dependencias o abstracciones no solicitadas.

## 5. Flujo de trabajo (commits)
- Commits pequeños y descriptivos, alineados a un todo.
- Antes de cerrar un todo o fase, correr los tests si existen.