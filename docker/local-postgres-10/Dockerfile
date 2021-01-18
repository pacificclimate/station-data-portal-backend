FROM ubuntu:18.04

# Get set to install packages
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update

# Set the locale (for PostgreSQL)
RUN apt-get -y install locales && \
    locale-gen en_CA.utf8
ENV LANG en_CA.utf8
ENV LANGUAGE en_CA:en
ENV LC_ALL en_CA.UTF-8

# Install the packages required to install this project.
RUN apt-get install -yq \
            libpq-dev \
            python3 \
            python3-dev \
            python3-pip \
            postgresql-10 \
            postgresql-plpython-10 \
            postgresql-10-postgis-2.4 \
            && \
    pip3 install -U pip pytest

# You must mount local codebase to this directory
WORKDIR /codebase

# Install the local codebase when the container starts.
ENTRYPOINT ./docker/local-postgres-10/entrypoint.sh
