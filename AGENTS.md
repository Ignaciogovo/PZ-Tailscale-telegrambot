# AGENTS.md

## Contexto del proyecto
Servidor dedicado de Project Zomboid B42 ejecutado mediante Docker, con acceso externo a través de Tailscale.
Compose: docker-compose.yml
Configuración: .env
Datos: /srv/data/project-zomboid/
Imagen: indifferentbroccoli/projectzomboid-server-docker
Mods: configurados manualmente en server-data/Server/<SERVER_NAME>.ini (Mods= y WorkshopItems=).
Red: el contenedor de Project Zomboid utiliza la red del contenedor Tailscale (network_mode: service:tailscale).
Máximo 8 jugadores.
Memoria: 2 GB mínimo / 5 GB máximo.
Configuración mediante .env.
Mods gestionados mediante Steam Workshop (descargados por PZ al arrancar).
- **Repositorio base**: https://github.com/indifferentbroccoli/projectzomboid-server-docker
- Consultar para entender: Dockerfile, scripts de inicio, variables de entorno, cómo funciona la imagen.
- Este proyecto es una adaptación con Tailscale, no un fork.
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