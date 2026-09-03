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

- **Repositorio upstream**: `indifferentbroccoli/projectzomboid-server-docker` guardado en `pz-docker/` como referencia. Consultar para entender Dockerfile, scripts, variables de entorno. Actualizar cuando se quiera sincronizar con la imagen oficial.

### Medidas de seguridad del bot de Telegram
El bot gestiona el servidor de PZ desde Telegram, lo que implica riesgos de seguridad. Se implementaron las siguientes medidas para prevenir escape al host y ataques:

**Problema original**: Montar el socket de Docker directamente en el bot da control total del host. Si el bot era comprometido (token robado, vulnerabilidad en python-telegram-bot), un atacante podía leer secrets de TODOS los contenedores del host (Jellyfin, Immich, etc.), ejecutar comandos en cualquiera, o escapar al host.

**Solución**: Proxy personalizado (`proxy/`) que actúa como intermediario entre el bot y el socket de Docker. El bot envía peticiones HTTP al proxy, que filtra por nombre de contenedor y solo permite operaciones sobre `project-zomboid`. Cualquier intento de acceder a otro contenedor es bloqueado con HTTP 403 Forbidden.

1. **Docker Socket Proxy personalizado**: El bot NO tiene acceso directo al socket de Docker. Usa un proxy personalizado (en `proxy/`) que filtra operaciones POR NOMBRE DE CONTENEDOR. Solo permite operaciones sobre `project-zomboid`. Bloquea acceso a cualquier otro contenedor del host (jellyfin, immich, etc.). Esto previene que un atacante con acceso al bot pueda leer secrets de otros contenedores o crear contenedores privilegiados.

2. **Validación de contenedor**: Todas las operaciones de Docker están restringidas a `project-zomboid` mediante `ALLOWED_CONTAINER` en el proxy. Si alguien intenta acceder a otro contenedor, el proxy devuelve HTTP 403 Forbidden.

3. **Validación de inputs**: Usernames, Steam IDs y roles se validan con regex estrictos antes de ejecutar comandos RCON. Esto previene inyección de comandos (ej. `admin; quit`).

4. **Correr como no-root**: El bot y el proxy corren como usuarios no-root (`botuser` y `proxyuser`). Si el contenedor es comprometido, el atacante no tiene privilegios de root dentro del contenedor, lo que reduce el impacto de un escape.

5. **Red interna**: El bot y el proxy de Docker están en una red aislada (`pz-internal`), separada de la red de Tailscale. Esto limita el alcance de un posible compromiso.

**Por qué estas medidas**: Telegram es un punto de entrada público. Si el chat autorizado es comprometido (token robado, sesión hackeada), el atacante tendría control del bot. Estas medidas aseguran que incluso en ese caso, el atacante solo puede controlar el contenedor de PZ, no el host ni otros contenedores.

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