# Cambios en esta versión

## Mejoras
- 🔧 Cambio interno en la ordenación de los discos de array para buscar el disco con tamaño suficiente antes de hacer el rsync.
- 🔧 Cambio interno en la ordenación de los torrents en qBittorrent para que solo muestre y procese los torrents que cumplen la condición.
- Añadido nivel de DEBUG = 2, quedando así:
    - DEBUG = 0: Solo mensajes INFO básicos de proceso (no muestra nombre de archivos).
    - DEBUG = 1: INFO + Muestra archivos que se van a procesar.
    - DEBUG = 2: INFO + Muestra todo, incluyendo archivos que no cumplen criterios de DIAS_ANTIGUEDAD. 
