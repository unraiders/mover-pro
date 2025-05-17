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

echo "$(date +'%d-%m-%Y %H:%M:%S') - Arrancando MOVER-PRO entrypoint.sh" 
echo "$(date +'%d-%m-%Y %H:%M:%S') - Versión: $VERSION" 
echo "$(date +'%d-%m-%Y %H:%M:%S') - Carpeta destino Array: $DESTINO" 
echo "$(date +'%d-%m-%Y %H:%M:%S') - Espacio mínimo en discos de Array: $ESPACIO_MINIMO GB" 
echo "$(date +'%d-%m-%Y %H:%M:%S') - Días de antigüedad: $DIAS_ANTIGUEDAD"
echo "$(date +'%d-%m-%Y %H:%M:%S') - % Mínimo de ocupación: $PORCENTAJE_MINIMO %" 
echo "$(date +'%d-%m-%Y %H:%M:%S') - Notificación a: $CLIENTE_NOTIFICACION" 
echo "$(date +'%d-%m-%Y %H:%M:%S') - Programación CRON: $CRON" 
echo "$(date +'%d-%m-%Y %H:%M:%S') - Debug: $DEBUG" 
echo "$(date +'%d-%m-%Y %H:%M:%S') - Prueba: $PRUEBA" 
echo "$(date +'%d-%m-%Y %H:%M:%S') - Zona horaria: $TZ" 


CRON_JOB="$CRON python3 /app/mover_pool_a_array.py >> /proc/1/fd/1 2>> /proc/1/fd/2"

echo "$CRON_JOB" > /etc/crontabs/root

echo "$(date +'%d-%m-%Y %H:%M:%S') - Arrancando cron..."
crond -f -l 2 || { echo "Error arrancando cron"; exit 1; }



