# Versión del upstream

Copia de: [indifferentbroccoli/projectzomboid-server-docker](https://github.com/indifferentbroccoli/projectzomboid-server-docker)
Commit: `1d8019c4db75bd71fe5d95485fdc318be6be57a1`
Fecha de sincronización: 2026-09-04

## Para actualizar

```bash
# Clonar el upstream en un directorio temporal
git clone https://github.com/indifferentbroccoli/projectzomboid-server-docker.git /tmp/upstream-pz

# Sobrescribir scripts
cp /tmp/upstream-pz/scripts/* pz-docker/scripts/

# Actualizar Dockerfile si es necesario
cp /tmp/upstream-pz/Dockerfile pz-docker/

# Actualizar este archivo con el nuevo commit
```
