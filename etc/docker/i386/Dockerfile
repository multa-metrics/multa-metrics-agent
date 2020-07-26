ARG BASE_IMAGE
ARG VERSION

# i386 -> python:3.7.7-slim-buster
# ARM -> balenalib/generic-armv7ahf-ubuntu-python:3.7.7-eoan-run

FROM ${BASE_IMAGE}
MAINTAINER Eugenio Breijo

RUN set -ex \
    && apt-get update

RUN set -ex \
    && pythonDeps=" \
        python3-dev \
        build-essential \
        pkg-config \
        libdbus-glib-1-dev \
        libgirepository1.0-dev \
        libcairo2-dev \
        gir1.2-gtk-3.0 \
        python3-gi \
        python-dbus \
    " \
    \
    && apt-get install -y --no-install-recommends $pythonDeps \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /device && mkdir /device/credentials && mkdir /device/credentials/certificates

WORKDIR /src
ADD ./ /src

ENV PYTHONPATH ${PYTHONPATH}:/src

RUN pip3 install -r ./etc/pip/requirements.txt
ADD etc/files/supervisor.conf    /etc/supervisor/conf.d/

ENV AGENT_VERSION ${VERSION}
VOLUME device-data:/device

VOLUME /var/run/docker.sock:/var/run/docker.sock
VOLUME /var/lib/docker/:/var/lib/docker:ro
VOLUME /sys:/sys:ro
VOLUME /:/rootfs:ro
VOLUME /var/run:/var/run:rw
VOLUME /proc:/prochost:ro

RUN set -ex \
    && pythonDeps=" \
            python3-dev \
            build-essential \
            pkg-config \
            libdbus-glib-1-dev \
            libgirepository1.0-dev \
            libcairo2-dev \
            gir1.2-gtk-3.0 \
            python3-gi \
        " \
        \
    && apt-get remove -y $pythonDeps

# HEALTHCHECK --start-period=120s --interval=60s --retries=1 CMD curl --fail http://127.0.0.1:5000/api/ || exit 1

CMD ["bash", "/src/src/start.sh"]