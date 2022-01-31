ARG VERSION

FROM python:3.6.15-slim-buster
LABEL MAINTAINER="Eugenio Breijo"

RUN mkdir /device && mkdir /device/data && mkdir /device/credentials && mkdir /device/credentials/certificates
WORKDIR /app
ADD ./src /app/src
ADD etc/files/supervisor.conf    /etc/supervisor/conf.d/
ADD etc/pip/requirements.txt     /app/pip/

ENV PYTHONPATH ${PYTHONPATH}:/app

RUN set -ex \
    && apt-get update \
    && pythonDeps=" \
        build-essential \
    " \
    \
    && apt-get install -y --no-install-recommends $pythonDeps \
    && rm -rf /var/lib/apt/lists/* \
    && pip install -r /app/pip/requirements.txt \
    && rm -rf /app/pip \
    && apt-get purge --auto-remove -y $pythonDeps

ENV AGENT_VERSION $VERSION

CMD ["python", "src/app.py"]