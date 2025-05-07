# mover-pro

Utilidad para **Unraid** que mueve las carpetas y ficheros de un pool al array según los días de antigüedad pasados en la variable DIAS_ANTIGUEDAD, respetando en el movimiento los hardlinks existentes y con la función de pausar/reanudar los torrents sedeados en qBittorrent y con notificación a Telegram o Discord.


## Características principales

- Gestión automática de torrents en qBittorrent (pausa/reanudación).
- Movimiento de archivos respetando hardlinks existentes.
- El proceso de movimiento tiene en cuenta la variable ESPACIO_MINIMO (GB) para comprobar en que discos del array hay espacio suficiente, desde disk1 -> diskX.
- Configurable por antigüedad de archivos.
- Notificaciones vía Telegram o Discord.
- Modo PRUEBA para verificar operaciones sin realizar cambios.
- Diferentes niveles de logging.


## Configuración variables de entorno.

| VARIABLE             | NECESARIO  | VALOR                                                                                                                                 |
| :------------------- | :-------:  | :------------------------------------------------------------------------------------------------------------------------------------ |
| QBITTORRENT_HOST     |     ✅     | Host y puerto de qBittorrent, ejemplo: 192.168.2.20:8090.                                                                             |
| QBITTORRENT_USER     |     ✅     | Usuario de qBittorrent.                                                                                                               |
| QBITTORRENT_PASSWORD |     ✅     | Contraseña de qBittorrent.                                                                                                            |
| CLIENTE_NOTIFICACION |     ❌     | Cliente para notificaciones ('telegram' o 'discord').                                                                                 |
| TELEGRAM_BOT_TOKEN   |     ❌     | Token del bot de Telegram.                                                                                                            |
| TELEGRAM_CHAT_ID     |     ❌     | ID del chat de Telegram.                                                                                                              |
| DISCORD_WEBHOOK      |     ❌     | URL del webhook de Discord.                                                                                                           |
| DESTINO              |     ✅     | Carpeta/Share destino dónde moverá los ficheros y carpetas (solo el nombre de la carpeta).                                            |
| ESPACIO_MINIMO       |     ✅     | Espacio mínimo en los discos del array a la hora de realizar el rsync (expresado en GB).                                              |
| DIAS_ANTIGUEDAD      |     ✅     | Número de días de antigüedad para ejecutar el proceso de movimiento.                                                                  |
| CRON                 |     ✅     | Hora de ejecutar el script (formato crontab. ej., 0 7 * * * = 7:00 AM, visita https://crontab.guru/ para más info.).                  |
| DEBUG                |     ✅     | Salida del log: 0 = información básica, 1 = información detallada, 2 = información superdetallada.                                    |
| PRUEBA               |     ✅     | Habilita el modo Prueba, no realiza ninguna modificación, es un modo simulación. (0 = No / 1 = Si).                                   |
| TZ                   |     ✅     | Timezone (Por ejemplo: Europe/Madrid).                                                                                                |

## Configuración de rutas.

| PATH                 | NECESARIO  | CONTENEDOR | HOST                                                                                                                     |
| :------------------- | :-------:  | :-------:  | :----------------------------------------------------------------------------------------------------------------------- |
| ORIGEN               |     ✅     | /origen    | por ejemplo: /mnt/calentito/data/ (calentito sería el nombre del pool).                                                  |
| ARRAY                |     ✅     | /mnt       | /mnt (se monta /mnt para tener acceso desde dentro del contenedor a todos los discos del array).                         |


  > [!IMPORTANT]
  > Se recomienda hacer uso de la variable PRUEBA = 1 antes de poner el Docker en producción, la ejecución de este Docker implica movimiento de ficheros y nos tenemos que asegurar que el proceso es correcto, con la variable PRUEBA a 1 NO realizará ningún movimiento de ficheros pero tendremos en el log el detalle de los ficheros que movería si estuviera la variable PRUEBA a 0. 
  > 
  > Activando la variable DEBUG = 0 tenemos un log básico de las operaciones que realiza.
  > 
  > Activando la variable DEBUG = 1 tenemos un log detallado de los torrents que pausará/reanudará en qBittorrent y los ficheros que moverá del pool al array.
  >
  > 
  > Una vez que compruebes que el funcionamiento sería el esperado después de la primera ejecución, comprueba que ha movido los ficheros correctamente y que ha respetado los hardlinks entre ambos ficheros.

### Instalación plantilla en Unraid.

- Nos vamos a una ventana de terminal en nuestro Unraid, pegamos esta línea y enter:
```sh
wget -O /boot/config/plugins/dockerMan/templates-user/my-mover-pro.xml https://raw.githubusercontent.com/unraiders/mover-pro/refs/heads/main/my-mover-pro.xml
```
- Nos vamos a DOCKER y abajo a la izquierda tenemos el botón "AGREGAR CONTENEDOR" hacemos click y en seleccionar plantilla seleccionamos mover-pro y rellenamos las variables de entorno necesarias, tienes una explicación en cada variable en la propia plantilla.
