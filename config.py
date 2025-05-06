import os

from dotenv import load_dotenv

load_dotenv()

QBITTORRENT_HOST = os.getenv('QBITTORRENT_HOST')
QBITTORRENT_USER = os.getenv('QBITTORRENT_USER')
QBITTORRENT_PASSWORD = os.getenv('QBITTORRENT_PASSWORD')

ORIGEN = '/origen'

DESTINO = os.getenv('DESTINO')

DIAS_ANTIGUEDAD = int(os.getenv('DIAS_ANTIGUEDAD'))
ESPACIO_MINIMO = int(os.getenv('ESPACIO_MINIMO'))

CLIENTE_NOTIFICACION = os.getenv('CLIENTE_NOTIFICACION')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')

IMG_DISCORD_URL = 'https://github.com/unraiders/mover-pro/blob/main/imagenes/mover-pro.png?raw=true'

PRUEBA = os.getenv('PRUEBA', '0') == '1'

DEBUG = os.getenv('DEBUG', '0') == '1'

TZ = os.getenv('TZ', 'Europe/Madrid')


