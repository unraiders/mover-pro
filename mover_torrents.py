from collections import defaultdict
from pathlib import Path, PurePosixPath

import qbittorrentapi

from config import (QBITTORRENT_HOST, QBITTORRENT_USER, QBITTORRENT_PASSWORD, ORIGEN, CARPETA_TORRENTS, PRUEBA, DEBUG)
from utils import setup_logger
from notificaciones import send_notification

logger = setup_logger(__name__)

ORIGEN_PATH = Path(ORIGEN)


def raiz_busqueda():
    """
    Carpeta donde buscar los torrents. Se acota a CARPETA_TORRENTS (relativa a
    /origen) si está definida y existe; si no, se busca en todo /origen.
    Las rutas del índice siempre son relativas a /origen para que el matching
    por sufijo funcione igual en ambos casos.
    """
    if CARPETA_TORRENTS:
        raiz = ORIGEN_PATH / CARPETA_TORRENTS
        if raiz.is_dir():
            return raiz
        logger.warning(
            f"🟠 La carpeta de torrents '{raiz}' no existe, se buscará en todo {ORIGEN}."
        )
    return ORIGEN_PATH


def indexar_origen():
    """
    Recorre la carpeta de torrents de forma recursiva y crea un índice
    basename -> [rutas relativas a /origen (posix) de los ficheros con ese nombre].

    Se construye antes de mover los ficheros (mientras todavía existen en el pool)
    para poder emparejar los torrents con el contenido presente en el pool.
    """
    indice = defaultdict(list)
    for f in raiz_busqueda().rglob("*"):
        try:
            if f.is_file():
                indice[f.name].append(f.relative_to(ORIGEN_PATH).as_posix())
        except FileNotFoundError:
            continue
    return indice


def torrent_en_origen(client, t_hash, indice):
    """
    Determina si un torrent tiene contenido presente en /origen.

    Matching tolerante: para cada fichero del torrent comprueba si en /origen
    existe un fichero cuya ruta relativa coincide con la ruta relativa del torrent
    (raíz directa) o termina en ella (subcarpetas por categoría). Exigir la ruta
    relativa completa del torrent —y no solo el nombre del fichero— reduce los
    falsos positivos por nombres repetidos.
    """
    try:
        files = client.torrents_files(torrent_hash=t_hash)
    except Exception as e:
        logger.warning(f"🟠 No se pudieron obtener los ficheros del torrent {t_hash}: {e}")
        return False

    for f in files:
        t_rel = PurePosixPath(f["name"]).as_posix()
        base = PurePosixPath(f["name"]).name
        for cand in indice.get(base, []):
            if cand == t_rel or cand.endswith("/" + t_rel):
                return True
    return False


def pausar_torrents(client):
    """
    Pausa todos los torrents cuyo contenido está presente en /origen.
    Devuelve una lista de (hash, name) de los torrents pausados para poder
    reanudar exactamente esos al final del proceso.
    """
    indice = indexar_origen()
    if DEBUG in (1, 2):
        logger.debug(f"Indexados {sum(len(v) for v in indice.values())} ficheros en {raiz_busqueda()}")

    pausados = []
    for torrent in client.torrents_info():
        if torrent_en_origen(client, torrent["hash"], indice):
            if DEBUG in (1, 2):
                logger.debug(f"Torrent con contenido en el pool: {torrent['name']}")
            if not PRUEBA:
                client.torrents_pause([torrent["hash"]])
            logger.info(f"{'[SIMULACIÓN] ' if PRUEBA else ''}Torrent {torrent['name']} pausado.")
            pausados.append((torrent["hash"], torrent["name"]))

    if not pausados:
        logger.info("No se encontraron torrents con contenido en el pool para pausar.")
        mensaje = (
            f"<b>MOVER-PRO</b>\n"
            f"💤 No se encontraron torrents con contenido en el pool para pausar."
        )
    else:
        logger.info(f"Total de torrents pausados: {len(pausados)}")
        mensaje = (
            f"<b>MOVER-PRO</b>\n"
            f"⏸️ Se pausaron {len(pausados)} torrents con contenido en el pool."
        )

    send_notification(
        message=mensaje,
        title="MOVER-PRO - Resumen de torrents pausados",
        parse_mode="HTML"
    )

    return pausados


def reanudar_torrents(client, pausados):
    """
    Reanuda exactamente los torrents que se pausaron al inicio del proceso.
    Recibe la lista de (hash, name) devuelta por pausar_torrents.
    """
    pausados = pausados or []

    reanudados = 0
    for t_hash, t_name in pausados:
        if DEBUG in (1, 2):
            logger.debug(f"Reanudando torrent: {t_name}")
        if not PRUEBA:
            client.torrents_resume([t_hash])
        logger.info(f"{'[SIMULACIÓN] ' if PRUEBA else ''}Torrent {t_name} reanudado.")
        reanudados += 1

    if reanudados == 0:
        logger.info("No había torrents pausados para reanudar.")
        mensaje = (
            f"<b>MOVER-PRO</b>\n"
            f"💤 No había torrents pausados para reanudar."
        )
    else:
        logger.info(f"Total de torrents reanudados: {reanudados}")
        mensaje = (
            f"<b>MOVER-PRO</b>\n"
            f"▶️ Se reanudaron {reanudados} torrents."
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


def gestionar_torrents(accion='pausar', pausados=None):
    client = get_qbittorrent_client()
    if not client:
        return [] if accion == 'pausar' else False

    if accion == 'pausar':
        return pausar_torrents(client)
    elif accion == 'reanudar':
        reanudar_torrents(client, pausados)
        return True


if __name__ == "__main__":
    gestionar_torrents()
