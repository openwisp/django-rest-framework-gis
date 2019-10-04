FROM python:3.7-alpine3.8

# postgresql-client is required by psql
# postgresql-dev musl-dev gcc are required by psycopg
# NOTE: there is py3-psycopg2
# gdal-dev geos-dev proj4-dev are required by geodjango
# NOTE: we actually need gdal-dev not gdal

# TODO: optimize installation by using --virtual
RUN apk update && apk upgrade \
    && apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
        postgresql-client \
        postgresql-dev \
        musl-dev \
        gcc \
    && apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
        gdal-dev \
        geos-dev \
        proj-dev

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8

WORKDIR /project

COPY requirements-test.txt /project/

RUN pip install --no-cache-dir -r requirements-test.txt
