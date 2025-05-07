import os
import subprocess
import time
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

from config import (DIAS_ANTIGUEDAD, ESPACIO_MINIMO, ORIGEN, DESTINO, PRUEBA, DEBUG)
from mover_torrents import gestionar_torrents
from utils import setup_logger, generate_trace_id
from notificaciones import send_notification

logger = setup_logger(__name__)

# Configuración discos array Unraid
def ordenar_discos(disco):
    """
    Extrae el número del nombre del disco (ejemplo: '/mnt/disk1/' -> 1)
    Solo procesa discos que sigan el patrón 'diskN' donde N es un número
    """
    try:
        nombre_disco = disco.name  # Obtiene solo el nombre de la carpeta
        if nombre_disco.startswith('disk'):
            numero = ''.join(filter(str.isdigit, nombre_disco))
            if numero:
                return int(numero)
    except (AttributeError, ValueError):
        pass
    return float('inf')  # Coloca al final cualquier disco con formato inválido

# Filtrar solo los discos que siguen el patrón correcto
DISCOS_ARRAY = sorted(
    [d for d in Path('/mnt').glob('disk*/')
     if d.name.startswith('disk') and any(c.isdigit() for c in d.name)],
    key=ordenar_discos
)
ORIGEN_PATH = Path(ORIGEN)

def espacio_disponible(path):
    """Devuelve espacio disponible en bytes en un punto de montaje"""
    stat = os.statvfs(path)
    return stat.f_bavail * stat.f_frsize

def verificar_espacio(disco, tamano_necesario):
    """Verifica si hay espacio suficiente considerando el mínimo en GB"""
    espacio_minimo_bytes = ESPACIO_MINIMO * 1024 * 1024 * 1024  # Convertir GB a bytes
    espacio_actual = espacio_disponible(disco)
    return espacio_actual > (tamano_necesario + espacio_minimo_bytes)

def encontrar_hardlinks(origen):
    """Busca archivos con hardlinks y agrupa por inode"""
    inodes = defaultdict(list)
    for root, dirs, files in os.walk(origen):
        for file in files:
            filepath = Path(root) / file
            try:
                stat = filepath.stat()
                if stat.st_nlink > 1:
                    inodes[(stat.st_ino, stat.st_dev)].append(filepath)
            except FileNotFoundError:
                continue
    return inodes

def es_archivo_antiguo(archivo):
    """Verifica si un archivo es más antiguo que DIAS_ANTIGUEDAD"""
    tiempo_actual = datetime.now(timezone.utc)
    tiempo_modificacion = datetime.fromtimestamp(archivo.stat().st_mtime, timezone.utc)
    dias_transcurridos = (tiempo_actual - tiempo_modificacion).days
    return dias_transcurridos >= DIAS_ANTIGUEDAD

def mover_fichero_con_hardlinks(grupo, discos):
    # Primero verificamos si el grupo cumple con la antigüedad
    if not all(es_archivo_antiguo(f) for f in grupo):
        if DEBUG == 2:  # Solo mostrar si DEBUG es 2
            logger.debug("Archivos en el grupo de hardlinks (no cumplen antigüedad):")
            for archivo in grupo:
                logger.debug(f"  - {archivo}")
            logger.info(f"Grupo de archivos no cumple con la antigüedad mínima de {DIAS_ANTIGUEDAD} días")
        return False

    if DEBUG in (1, 2):
        logger.debug("Archivos en el grupo de hardlinks a procesar:")
        for archivo in grupo:
            logger.debug(f"  - {archivo}")

    tamano_total = sum(f.stat().st_size for f in grupo)
    for disco in discos:
        logger.info(f"Verificando espacio en {disco}...")
        if verificar_espacio(disco, tamano_total):
            destino_base = disco / DESTINO
            destino_base.mkdir(parents=True, exist_ok=True)
            logger.info(f"{'[SIMULACIÓN] ' if PRUEBA else ''}Moviendo grupo de hardlinks a {destino_base}")

            cmd = ["rsync", "-aHAX", "--relative"]
            if PRUEBA:
                cmd.append("--dry-run")
            else:
                cmd.append("--remove-source-files")
            cmd += ["--files-from=-", str(ORIGEN_PATH), str(destino_base)]

            input_files = "\n".join(str(f.relative_to(ORIGEN_PATH)) for f in grupo)
            res = subprocess.run(cmd, input=input_files.encode())
            
            if res.returncode == 0:
                logger.info(f"🚀 {'[SIMULACIÓN] ' if PRUEBA else ''}Grupo movido correctamente a {destino_base}")
                return True
            else:
                logger.error(f"🔴 Falló el rsync al mover a {destino_base}")
                continue
        else:
            logger.warning(f"🟠 No hay espacio suficiente en {disco}, probando siguiente disco...")
    
    logger.error("🔴 No hay ningún disco con suficiente espacio para este grupo.")
    return False

def mover_individuales(sin_hardlinks, discos):
    for file in sin_hardlinks:
        if not es_archivo_antiguo(file):
            if DEBUG == 2:  # Solo mostrar si DEBUG es 2
                logger.debug(f"Archivo no cumple antigüedad: {file}")
                logger.info(f"Archivo {file} no cumple con la antigüedad mínima de {DIAS_ANTIGUEDAD} días")
            return False

        if DEBUG in (1, 2):
            logger.debug(f"Procesando archivo individual: {file}")

        tamano = file.stat().st_size
        for disco in discos:
            logger.info(f"Verificando espacio en {disco} para {file}...")
            if verificar_espacio(disco, tamano):
                destino_base = disco / DESTINO
                destino_base.mkdir(parents=True, exist_ok=True)

                cmd = ["rsync", "-aHAX", "--relative"]
                if PRUEBA:
                    cmd.append("--dry-run")
                else:
                    cmd.append("--remove-source-files")
                cmd += ["--files-from=-", str(ORIGEN_PATH), str(destino_base)]

                input_file = str(file.relative_to(ORIGEN_PATH))
                res = subprocess.run(cmd, input=(input_file + "\n").encode())
                
                if res.returncode == 0:
                    logger.info(f"🏗️ {'[SIMULACIÓN] ' if PRUEBA else ''}Archivo {file} movido a {destino_base}")
                    return True
                else:
                    logger.error(f"🔴 Error moviendo {file} a {destino_base}, probando siguiente disco...")
            else:
                logger.warning(f"🟠 No hay espacio suficiente en {disco}, probando siguiente disco...")
        
        logger.error(f"🔴 No hay ningún disco con espacio suficiente para {file}")
        return False

def mover_todo():
    
    generate_trace_id()
    
    logger.info(f"Iniciando el proceso de mover archivos desde {ORIGEN}")
    
    gestionar_torrents('pausar', DIAS_ANTIGUEDAD)
    
    hardlink_grupos = encontrar_hardlinks(ORIGEN_PATH)
    todos_los_archivos = set(p for p in ORIGEN_PATH.rglob("*") if p.is_file())
    archivos_en_grupos = set(f for grupo in hardlink_grupos.values() for f in grupo)
    sin_hardlinks = list(todos_los_archivos - archivos_en_grupos)

    logger.info(f"Se encontraron {len(todos_los_archivos)} archivos en total")
    logger.info(f"- {len(archivos_en_grupos)} archivos en grupos de hardlinks")
    logger.info(f"- {len(sin_hardlinks)} archivos individuales")

    hardlinks_movidos = 0
    individuales_movidos = 0

    for grupo in hardlink_grupos.values():
        if mover_fichero_con_hardlinks(grupo, DISCOS_ARRAY):
            hardlinks_movidos += len(grupo)

    for file in sin_hardlinks:
        if mover_individuales([file], DISCOS_ARRAY):
            individuales_movidos += 1

    total_movidos = hardlinks_movidos + individuales_movidos

    mensaje = (
        f"<b>MOVER-PRO</b>\n"
        f"🚀 Se movieron {total_movidos} archivos en total:\n"
        f"🔗 - {hardlinks_movidos} archivos en grupos de hardlinks.\n"
        f"⛓️‍💥 - {individuales_movidos} archivos individuales."
    )

    send_notification(
        message=mensaje,
        title="MOVER-PRO - Resumen de movimiento de archivos",
        parse_mode="HTML"
    )

    logger.info(f"{'[SIMULACIÓN] ' if PRUEBA else ''}Total de archivos movidos: {total_movidos}")

    gestionar_torrents('reanudar', DIAS_ANTIGUEDAD)

def eliminar_directorios_vacios(path, intentos=5, espera=10):
    """
    Elimina directorios vacíos con reintentos, excluyendo el directorio raíz
    :param path: Ruta a procesar
    :param intentos: Número de intentos antes de fallar
    :param espera: Segundos de espera entre intentos
    """
    for intento in range(intentos):
        if intento > 0:
            logger.info(f"⏳ Esperando {espera} segundos antes del intento {intento + 1}...")
            time.sleep(espera)

        # Encontrar directorios vacíos excluyendo el directorio raíz
        cmd_find = ["find", str(path), "-mindepth", "1", "-type", "d", "-empty"]
        resultado = subprocess.run(cmd_find, capture_output=True, text=True)
        
        if resultado.returncode == 0 and resultado.stdout:
            directorios = [d for d in resultado.stdout.strip().split('\n') if d]
            if not directorios:
                logger.info("💬 No se encontraron directorios vacíos para eliminar")
                return True
                
            logger.info(f"🔍 Se encontraron {len(directorios)} directorios vacíos")
            
            # Eliminar cada directorio individualmente
            exito = True
            for dir in directorios:
                try:
                    os.rmdir(dir)
                    logger.info(f"🧹 Eliminado directorio vacío: {dir}")
                except OSError as e:
                    logger.warning(f"🟠 No se pudo eliminar {dir}: {e}")
                    exito = False
            
            if exito:
                logger.info(f"🗑️ Directorios: {len(directorios)} directorios vacíos eliminados correctamente")
                return True
            else:
                logger.warning(f"🟠 Intento {intento + 1}/{intentos}: Algunos directorios no pudieron ser eliminados")
                continue
        else:
            logger.info("💬 No se encontraron directorios vacíos para eliminar")
            return True
    
    logger.error(f"🔴 No se pudieron eliminar los directorios vacíos después de {intentos} intentos")
    return False

if __name__ == "__main__":
    mover_todo()
    logger.info("⏳ Esperando 10 segundos antes de limpiar directorios vacíos...")
    time.sleep(10)
    eliminar_directorios_vacios(ORIGEN_PATH)
    logger.info("🕓 Esperando al próximo evento...")