# Adapted from weather-anomaly-data-service/Dockerfile and
# climate-explorer-backend/docker/Dockerfile.dev
# As always with docker, is there a better way to do this? Almost certainly.

FROM ubuntu:18.04

MAINTAINER Rod Glover <rglover@uvic.ca>

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

RUN pip3 install -U pip
RUN pip3 install -i https://pypi.pacificclimate.org/simple/ -r requirements.txt
RUN pip3 install .

EXPOSE 8000

ENV FLASK_APP sdpb.wsgi
ENV FLASK_ENV development
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

CMD flask run -p 8000 -h 0.0.0.0 --no-reload
