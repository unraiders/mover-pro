FROM python:3.13-alpine

LABEL maintainer="unraiders"
LABEL description="Ejecutar rsync con días de antigüedad, teniendo en cuenta hardlinks y pausar/reanudar los torrents sedeados en qBittorrent con notificación a Telegram o Discord."

ARG VERSION=1.0.0
ENV VERSION=${VERSION}

# Instalar cron y otros paquetes
RUN apk add --no-cache dcron rsync findutils mc

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mover_pool_a_array.py .
COPY mover_torrents.py .

COPY utils.py .
COPY config.py .
COPY notificaciones.py .

COPY entrypoint.sh .
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]