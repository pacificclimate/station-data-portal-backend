# Adapted from weather-anomaly-data-service/Dockerfile and
# climate-explorer-backend/docker/Dockerfile.dev
# As always with docker, is there a better way to do this? Almost certainly.

FROM ubuntu:20.04

LABEL Maintainer="Rod Glover <rglover@uvic.ca>"

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
    pipenv install gunicorn # installs all the packages plus gunicorn

EXPOSE 8000

# gunicorn.conf is set up so that Gunicorn settings are set by environment variables.
# Gunicorn setting [setting] is set by env var GUNICORN_[setting].
CMD pipenv run gunicorn --config gunicorn.conf --log-config logging.conf -b ":8000" sdpb.wsgi:flask_app
