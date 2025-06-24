# mover-pro

Utilidad para **UNRAID** que mueve las carpetas y ficheros de un pool al array según los días de antigüedad pasados en la variable **DIAS_ANTIGUEDAD** y porcentaje de ocupación en el pool definido en la variable **PORCENTAJE_MINIMO**, respetando en el movimiento los hardlinks existentes y con la función de pausar/reanudar los torrents sedeados en qBittorrent y con notificación de todo el proceso a Telegram o Discord.


## Características principales

- Gestión automática de torrents en qBittorrent (pausa/reanudación).
- Movimiento de archivos respetando hardlinks existentes.
- El proceso de movimiento tiene en cuenta la variable ESPACIO_MINIMO (GB) para comprobar en que discos del array hay espacio suficiente, desde disk1 -> diskX.
- Configurable por antigüedad de archivos (DIAS_ANTIGUEDAD).
- Configurable por % de ocupación del pool de origen (PORCENTAJE_MINIMO) (si no llega la ocupación en ese pool a ese porcentaje definido no se ejecuta el movimiento).
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
| PORCENTAJE_MINIMO    |     ❌     | % Mínimo de ocupación en el pool para ejecutar el proceso de movimiento con rsync (expresado en %).                                   |
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
> Se recomienda hacer uso de la variable PRUEBA = 1 antes de poner el Docker en producción, la ejecución de este Docker implica movimiento de ficheros así como acceso al pool y al array en Unraid y nos tenemos que asegurar que el proceso es correcto, con la variable PRUEBA a 1 NO realizará ningún movimiento de ficheros ni borrado de carpetas, pero tendremos en el log el detalle de los ficheros que movería y que .torrents pausará el cliente de torrents. 
> 
> Activando la variable DEBUG = 0 tenemos un log básico de las operaciones que realiza.
> 
> Activando la variable DEBUG = 1 tenemos un log detallado de los torrents que pausará/reanudará en qBittorrent y los ficheros que moverá del pool al array.
>
> Activando la variable DEBUG = 2 tenemos un log súper detallado de los torrents que pausará/reanudará en qBittorrent y los ficheros que moverá del pool al array.
>
> Una vez que compruebes que el funcionamiento sería el esperado después de la primera ejecución, comprueba que ha movido los ficheros correctamente y que ha respetado los hardlinks entre ambos ficheros.

> [!IMPORTANT]
> Este es el único proceso manual que tendremos que hacer, una vez añadido un nuevo disco al array hay que crear una carpeta en la raíz de ese disco con el nombre del share que tenemos definido en shares para que pase a formar parte ese disco del conjunto de discos que utilizamos en la variable DESTINO para ejecutar el movimiento. 

> [!IMPORTANT]
> El share del pool que tenemos definido debe estar configuradod e la siguiente manera: 

> [!IMPORTANT]
> El share en el pool que tenemos definido debe estar configurado de la siguiente manera:
> 
> * Almacenamiento primario = Tu disco o grupo de discos en el pool.
> * Almacenamiento secundario = Ninguno (Ya que no hacemos uso del mover de Unraid).

### Instalación plantilla en Unraid.

- Nos vamos a una ventana de terminal en nuestro Unraid, pegamos esta línea y enter:
```sh
wget -O /boot/config/plugins/dockerMan/templates-user/my-mover-pro.xml https://raw.githubusercontent.com/unraiders/mover-pro/refs/heads/main/my-mover-pro.xml
```
- Nos vamos a DOCKER y abajo a la izquierda tenemos el botón "AGREGAR CONTENEDOR" hacemos click y en seleccionar plantilla seleccionamos mover-pro y rellenamos las variables de entorno necesarias, tienes una explicación en cada variable en la propia plantilla.

### Preview 😎

![alt text](https://github.com/unraiders/mover-pro/blob/main/imagenes/inicio.png)

Inicio...

![alt text](https://github.com/unraiders/mover-pro/blob/main/imagenes/pausa_torrents.png)

Inicio y pausa de torrents...

![alt text](https://github.com/unraiders/mover-pro/blob/main/imagenes/movimiento_hardlinks.png)

Movimiento hardlinks y ficheros individuales...

![alt text](https://github.com/unraiders/mover-pro/blob/main/imagenes/borrado_directorios.png)

Borrado de directorios vacíos en el pool de origen...

![alt text](https://github.com/unraiders/mover-pro/blob/main/imagenes/telegram.png)

Envio mensaje a Telegram...

![alt text](https://github.com/unraiders/mover-pro/blob/main/imagenes/discord.png)

Envio mensaje a Discord...

![alt text](https://github.com/unraiders/mover-pro/blob/main/imagenes/movimiento_porcentaje_minimo.png)

Movimiento solo cuando supera el % definido en el disco del pool...

Fin.


