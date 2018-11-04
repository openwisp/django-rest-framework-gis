FROM python:3.7-alpine3.8

# postgresql-client is required by psql
# postgresql-dev musl-dev gcc are required by psycopg
# NOTE: there is py3-psycopg2
# gdal-dev geos-dev proj4-dev are required by geodjango
# NOTE: we actually need gdal-dev not gdal

# TODO: optimize installation by using --virtual
RUN apk update && apk upgrade \
    && apk add postgresql-client postgresql-dev musl-dev gcc \
    && apk add --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
        gdal-dev \
        geos-dev \
        proj4-dev

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8

WORKDIR /project

COPY requirements-test.txt /project/

RUN pip install -r requirements-test.txt
