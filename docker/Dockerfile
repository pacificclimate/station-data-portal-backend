# Adapted from weather-anomaly-data-service/Dockerfile and
# climate-explorer-backend/docker/Dockerfile.dev
# As always with docker, is there a better way to do this? Almost certainly.

FROM ubuntu:20.04

MAINTAINER Rod Glover <rglover@uvic.ca>

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get -yq install \
        libpq-dev \
        python3 \
        python3-dev \
        python3-pip \
        postgresql-client

ADD . /app
WORKDIR /app

RUN pip3 install -U pipenv --ignore-installed && \
    pipenv install

EXPOSE 8000

ENV FLASK_APP sdpb.wsgi
ENV FLASK_ENV development

CMD pipenv run flask run -p 8000 -h 0.0.0.0 --no-reload
