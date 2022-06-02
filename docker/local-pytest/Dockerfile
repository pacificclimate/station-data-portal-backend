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

# Make legacy Ubuntu 18.04 postgres packages available
RUN \
    apt-get update && \
    apt-get install -y curl ca-certificates gnupg && \
    curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    echo 'deb http://apt.postgresql.org/pub/repos/apt bionic-pgdg main' >/etc/apt/sources.list.d/pgdg.list && \
    apt-get update && \
    apt purge postgresql-client-14 postgresql-server-dev-all

# Install the packages required to install this project.
RUN apt-get install -yq \
            libpq-dev \
            python3.8 \
            python3.8-dev \
            python3.8-distutils \
#            python3.8-pip \
            python3.8-venv \
            python3-pip \
            postgresql-10 \
            postgresql-plpython-10 \
            postgresql-10-postgis-2.4
# Must install earlier version of pipenv to avoid bug that prevents installing pycds.
RUN pip3 install -U pip && \
    pip3 install pipenv==2022.3.28

# Set up non-root user. We do this for two reasons:
# - Postgres refuses to run as root for security reasons.
# - In general, we do not want to run our test environments as root on workstations, because
#   they are behind the firewall.
# This setup follows the pattern established in several other projects for non-root users.

# Build arguments (scope limited to build). If you wish to use a different user,
# group, or home dir, override these in the build command or change them here.
# If you specify build arg USERNAME=root, then the user is root.
ARG USERNAME=dockremap
ARG UID=1000
ARG GROUPNAME=${USERNAME}
ARG GID=1000
ARG USER_DIR=/opt/${USERNAME}

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

# You must mount local codebase to this directory
ENV CODEBASE_DIR=/codebase
RUN mkdir ${CODEBASE_DIR}

# This is where we do pipenv install. We don't want to overwrite Pipfile in ${CODEBASE_DIR},
# so we copy Pipfile here, modify it to install the local codebase from ${CODEBASE_DIR},
# and pipenv install in this directory.
ENV INSTALL_DIR=/install
RUN mkdir ${INSTALL_DIR} && chown ${USERNAME}:${GROUPNAME} ${INSTALL_DIR}
WORKDIR ${INSTALL_DIR}

USER ${USERNAME}

# Install the local codebase when the container starts.
ENTRYPOINT ${CODEBASE_DIR}/docker/local-pytest/entrypoint.sh
