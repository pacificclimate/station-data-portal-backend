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

# Build arguments (scope limited to build). If you wish to use a different user,
# group, or home dir, override these in the build command or change them here.
# If you specify build arg USERNAME=root, then the user is root.
ARG USERNAME=dockremap
ARG UID=1000
ARG GROUPNAME=${USERNAME}
ARG GID=1000
ARG USER_DIR=/app

# Environment variables (scope NOT limited to build). These are set here so that
# subsequent builds and containers have access to these build arguments.
ENV USERNAME=${USERNAME}
ENV UID=${UID}
ENV GROUPNAME=${GROUPNAME}
ENV GID=${GID}
ENV USER_DIR=${USER_DIR}

# Create non-privileged user, group, and its directory. This is only done if USERNAME is not root.
RUN if [ "$USERNAME" != "root" ]; \
    then \
        echo "Creating non-root user"; \
        groupadd -r -g ${GID} ${GROUPNAME}; \
        useradd -r -d ${USER_DIR} -g ${GROUPNAME} -u ${UID} ${USERNAME}; \
        mkdir -p ${USER_DIR}; \
        chown ${USERNAME}:${GROUPNAME} ${USER_DIR}; \
    fi

# Set user
USER ${USERNAME}

ADD --chown=${USERNAME}:${GROUPNAME} . ${USER_DIR}
WORKDIR ${USER_DIR}
ENV PATH=${USER_DIR}/.local/bin:${PATH}

RUN \
    # Install Poetry \
    echo ">> Install Poetry" \
    curl -sSL https://install.python-poetry.org | python3 - \
    # Add Gunicorn \
    echo ">> Add Gunicorn" \
    poetry add gunicorn \
    # Install the project \
    echo ">> Install the project" \
    poetry install

EXPOSE 8000

# gunicorn.conf is set up so that Gunicorn settings are set by environment variables.
# Gunicorn setting [setting] is set by env var GUNICORN_[setting].
CMD pipenv run gunicorn --config gunicorn.conf --log-config logging.conf -b ":8000" sdpb.wsgi:flask_app
