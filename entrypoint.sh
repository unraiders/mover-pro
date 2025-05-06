#!/bin/sh

validar_cron() {
    if ! echo "$1" | grep -qE '^[*/0-9,-]+ [*/0-9,-]+ [*/0-9,-]+ [*/0-9,-]+ [*/0-9,-]+$'; then
        echo "Error: Formato cron inválido: $1"
        echo "Debe tener 5 campos: minuto hora día-mes mes día-semana"
        exit 1
    fi
}

if [ -z "$CRON" ]; then
    echo "La variable CRON no está definida."
    exit 1
fi

validar_cron "$CRON"

echo "$(date +'%d-%m-%Y %H:%M:%S') - Arrancando MOVER-PRO entrypoint.sh" >&2
echo "$(date +'%d-%m-%Y %H:%M:%S') - Versión: $VERSION" >&2
echo "$(date +'%d-%m-%Y %H:%M:%S') - Carpeta destino Array: $DESTINO" >&2
echo "$(date +'%d-%m-%Y %H:%M:%S') - Espacio mínimo en discos de Array: $ESPACIO_MINIMO GB" >&2
echo "$(date +'%d-%m-%Y %H:%M:%S') - Notificación a: $CLIENTE_NOTIFICACION" >&2
echo "$(date +'%d-%m-%Y %H:%M:%S') - Programación CRON: $CRON" >&2
echo "$(date +'%d-%m-%Y %H:%M:%S') - Debug: $DEBUG" >&2
echo "$(date +'%d-%m-%Y %H:%M:%S') - Prueba: $PRUEBA" >&2
echo "$(date +'%d-%m-%Y %H:%M:%S') - Zona horaria: $TZ" >&2


CRON_JOB="$CRON python3 /app/mover_pool_a_array.py >> /proc/1/fd/1 2>> /proc/1/fd/2"

echo "$CRON_JOB" > /etc/crontabs/root

echo "$(date +'%d-%m-%Y %H:%M:%S') - Arrancando cron..."
crond -f -l 2 || { echo "Error arrancando cron"; exit 1; }



