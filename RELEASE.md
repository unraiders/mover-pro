# Cambios en esta versión

## ✨ Novedades

- **Pausa/reanudación de torrents por contenido en lugar de por fecha.** Ahora se pausan los torrents cuyos ficheros están realmente en el pool a mover, en vez de filtrar por días de antigüedad. Esto desacopla correctamente "qué ficheros mover" (sigue rigiéndose por `DIAS_ANTIGUEDAD`) de "qué torrents pausar" (su contenido presente en el pool).
- **Nueva variable `CARPETA_TORRENTS`** (opcional, por defecto `torrents`): acota de forma recursiva la búsqueda de torrents a esa subcarpeta de `ORIGEN`. Si está vacía, busca en todo `ORIGEN`. Si la carpeta no existe, hace fallback a todo `ORIGEN` con un aviso.

## 🐞 Correcciones

- Corregido el filtrado de torrents que usaba igualdad exacta de días (`== DIAS`), lo que dejaba sin pausar/reanudar cualquier torrent que no tuviera *exactamente* esa antigüedad y era incoherente con el criterio `>=` usado para mover ficheros.
- La reanudación ahora actúa **exactamente sobre los torrents que se pausaron** (se recuerdan sus hashes), evitando que queden torrents sin reanudar tras mover los ficheros con `--remove-source-files`.
- La reanudación se ejecuta en un bloque `finally`: aunque el `rsync` falle a mitad del proceso, los torrents nunca quedan pausados de forma permanente.

## 🔧 Mejoras

- El **modo PRUEBA** (`PRUEBA=1`) ya no toca qBittorrent: detecta y registra con prefijo `[SIMULACIÓN]` qué torrents pausaría/reanudaría sin ejecutar ninguna acción real, coherente con el modo simulación del `rsync`.
- El matching de torrents es tolerante con la estructura de carpetas (raíz directa o subcarpetas por categoría) comparando la ruta relativa del torrent por sufijo, reduciendo falsos positivos por nombres repetidos.

## 🚀 CI/CD

- Nuevo workflow `despliegue.yml`: en cada push a `main` o `develop` crea tag + release en GitHub y publica imagen multiarch (`amd64`, `arm64/v8`, `arm/v7`) en **DockerHub** (`unraiders/mover-pro`) y **GHCR** (`ghcr.io/unraiders/mover-pro`).
- La versión se gestiona por rama mediante los ficheros `.version_main` y `.version_develop`, que se inyectan en la imagen vía `--build-arg`.
- El `Dockerfile` usa `ARG VERSION=local` como valor por defecto, de modo que los builds manuales se identifican como `local` mientras que los builds del workflow muestran la versión real.
