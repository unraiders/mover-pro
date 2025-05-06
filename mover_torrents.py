import qbittorrentapi
from datetime import datetime, UTC
from config import (QBITTORRENT_HOST, QBITTORRENT_USER, QBITTORRENT_PASSWORD, DEBUG)
from utils import setup_logger

logger = setup_logger(__name__)

def pausar_torrents(client, dias):
    torrents = client.torrents_info()
    torrents_pausados = 0
    
    if DEBUG:
        logger.debug(f"Procesando {len(torrents)} torrents para pausar...")
        
    for torrent in torrents:
        fecha_añadido = datetime.fromtimestamp(torrent['added_on'], UTC)
        dias_transcurridos = (datetime.now(UTC) - fecha_añadido).days
        
        if DEBUG:
            logger.debug(f"Torrent: {torrent['name']}")
            logger.debug(f"  - Dias desde añadido: {dias_transcurridos}")
            logger.debug(f"  - Estado: {'Pausado' if torrent['state'] == 'pausedUP' else 'Activo'}")
            
        if dias_transcurridos == dias:
            client.torrents_pause([torrent['hash']])
            logger.info(f"Torrent {torrent['name']} pausado.")
            torrents_pausados += 1
    
    if torrents_pausados == 0:
        logger.info(f"No se encontraron torrents de {dias} días para pausar.")
    else:
        logger.info(f"Total de torrents pausados: {torrents_pausados}")

def reanudar_torrents(client, dias):
    torrents = client.torrents_info()
    torrents_reanudados = 0
    
    if DEBUG:
        logger.debug(f"Procesando {len(torrents)} torrents para reanudar...")
        
    for torrent in torrents:
        fecha_añadido = datetime.fromtimestamp(torrent['added_on'], UTC)
        dias_transcurridos = (datetime.now(UTC) - fecha_añadido).days
        
        if DEBUG:
            logger.debug(f"Torrent: {torrent['name']}")
            logger.debug(f"  - Dias desde añadido: {dias_transcurridos}")
            logger.debug(f"  - Estado: {'Pausado' if torrent['state'] == 'pausedUP' else 'Activo'}")
            
        if dias_transcurridos == dias:
            client.torrents_resume([torrent['hash']])
            logger.info(f"Torrent {torrent['name']} reanudado.")
            torrents_reanudados += 1
    
    if torrents_reanudados == 0:
        logger.info(f"No se encontraron torrents de {dias} días para reanudar.")
    else:
        logger.info(f"Total de torrents reanudados: {torrents_reanudados}")

def get_qbittorrent_client():
    client = qbittorrentapi.Client(host=QBITTORRENT_HOST)
    
    try:
        client.auth_log_in(username=QBITTORRENT_USER, password=QBITTORRENT_PASSWORD)
        logger.info(f"Conexión exitosa con {QBITTORRENT_HOST}")
        return client
    except qbittorrentapi.LoginFailed as e:
        logger.error(f"Error al intentar conectar: {e}")
        return None

def gestionar_torrents(accion='pausar', dias=7):
    client = get_qbittorrent_client()
    if not client:
        return False

    if accion == 'pausar':
        pausar_torrents(client, dias)
    elif accion == 'reanudar':
        reanudar_torrents(client, dias)
    
    return True

if __name__ == "__main__":
    gestionar_torrents()