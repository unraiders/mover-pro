import qbittorrentapi
from datetime import datetime, UTC
from config import (QBITTORRENT_HOST, QBITTORRENT_USER, QBITTORRENT_PASSWORD, DEBUG)
from utils import setup_logger
from notificaciones import send_notification

logger = setup_logger(__name__)

def pausar_torrents(client, dias):
    # Obtener todos los torrents y ordenarlos por fecha de añadido
    torrents = sorted(
        client.torrents_info(),
        key=lambda x: x['added_on']
    )
    
    # Filtrar solo los torrents que cumplen con los días de antigüedad
    torrents_a_procesar = [
        torrent for torrent in torrents
        if (datetime.now(UTC) - datetime.fromtimestamp(torrent['added_on'], UTC)).days == dias
    ]
    
    if DEBUG in (1, 2):
        logger.debug(f"Se encontraron {len(torrents_a_procesar)} torrents de {dias} días de antigüedad")
    
    torrents_pausados = 0
    for torrent in torrents_a_procesar:
        if DEBUG in (1, 2):
            logger.debug(f"Procesando torrent: {torrent['name']}")
            logger.debug(f"  - Edad: {(datetime.now(UTC) - datetime.fromtimestamp(torrent['added_on'], UTC)).days} días")
            logger.debug(f"  - Estado: {'Pausado' if torrent['state'] == 'pausedUP' else 'Activo'}")
        
        client.torrents_pause([torrent['hash']])
        logger.info(f"Torrent {torrent['name']} pausado.")
        torrents_pausados += 1
    
    if torrents_pausados == 0:
        logger.info(f"No se encontraron torrents de {dias} días para pausar.")
        mensaje = (
            f"<b>MOVER-PRO</b>\n"
            f"💤 No se encontraron torrents de {dias} días para pausar."
        )
    else:
        logger.info(f"Total de torrents pausados: {torrents_pausados}")
        mensaje = (
            f"<b>MOVER-PRO</b>\n"
            f"⏸️ Se pausaron {torrents_pausados} torrents de {dias} días de antigüedad."
        )

    send_notification(
        message=mensaje,
        title="MOVER-PRO - Resumen de torrents pausados",
        parse_mode="HTML"
    )

def reanudar_torrents(client, dias):
    # Obtener todos los torrents y ordenarlos por fecha de añadido
    torrents = sorted(
        client.torrents_info(),
        key=lambda x: x['added_on']
    )
    
    # Filtrar solo los torrents que cumplen con los días de antigüedad
    torrents_a_procesar = [
        torrent for torrent in torrents
        if (datetime.now(UTC) - datetime.fromtimestamp(torrent['added_on'], UTC)).days == dias
    ]
    
    if DEBUG in (1, 2):
        logger.debug(f"Se encontraron {len(torrents_a_procesar)} torrents de {dias} días de antigüedad")
    
    torrents_reanudados = 0
    for torrent in torrents_a_procesar:
        if DEBUG in (1, 2):
            logger.debug(f"Procesando torrent: {torrent['name']}")
            logger.debug(f"  - Estado: {'Pausado' if torrent['state'] == 'pausedUP' else 'Activo'}")
        
        client.torrents_resume([torrent['hash']])
        logger.info(f"Torrent {torrent['name']} reanudado.")
        torrents_reanudados += 1
    
    if torrents_reanudados == 0:
        logger.info(f"No se encontraron torrents de {dias} días para reanudar.")
        mensaje = (
            f"<b>MOVER-PRO</b>\n"
            f"💤 No se encontraron torrents de {dias} días para reanudar."
        )
    else:
        logger.info(f"Total de torrents reanudados: {torrents_reanudados}")
        mensaje = (
            f"<b>MOVER-PRO</b>\n"
            f"▶️ Se reanudaron {torrents_reanudados} torrents de {dias} días de antigüedad."
        )

    send_notification(
        message=mensaje,
        title="MOVER-PRO - Resumen de torrents reanudados",
        parse_mode="HTML"
    )

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