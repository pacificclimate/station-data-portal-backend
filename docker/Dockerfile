# Adapted from weather-anomaly-data-service/Dockerfile and
# climate-explorer-backend/docker/Dockerfile.dev
# As always with docker, is there a better way to do this? Almost certainly.

# ── Build stage ───────────────────────────────────────────────────────────────
# Compiles C extensions (psycopg2, etc.) and assembles the virtualenv.
# None of the build tooling ends up in the final image.
FROM ubuntu:24.04 AS builder

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get -yq install \
        libpq-dev \
        python3 \
        python3-dev \
        python3-pip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Poetry (--break-system-packages required on Ubuntu 24.04 / PEP 668)
RUN pip install --break-system-packages poetry==2.4.1

# Copy dependency manifests first to leverage layer caching
COPY pyproject.toml poetry.lock ./

# Install runtime dependencies into an in-project virtualenv; skip dev deps
RUN poetry config virtualenvs.in-project true && \
    poetry install --no-root --only main,deploy

# Copy source (deps already installed; --no-root means the package itself is not installed,
# but sdpb/ is importable directly from the working directory)
COPY sdpb/ ./sdpb/


# ── Runtime stage ─────────────────────────────────────────────────────────────
# Only the shared library (libpq5), Python runtime, the venv, and app source.
# No pip, no Poetry, no compiler toolchain, no headers.
FROM ubuntu:24.04

LABEL Maintainer="Rod Glover <rglover@uvic.ca>"

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get -yq install \
        libpq5 \
        python3 \
        postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Build arguments (scope limited to build). If you wish to use a different user,
# group, or home dir, override these in the build command or change them here.
ARG USERNAME=ubuntu
ARG USER_DIR=/app

# Environment variables (scope NOT limited to build). These are set here so that
# subsequent builds and containers have access to these build arguments.
ENV USERNAME=${USERNAME}
ENV USER_DIR=${USER_DIR}

# The 'ubuntu' user (UID/GID 1000) is pre-installed in ubuntu:24.04.
# Just create the app directory and assign ownership.
RUN mkdir -p ${USER_DIR} && chown ${USERNAME}:${USERNAME} ${USER_DIR}

# Copy the virtualenv and application source from the build stage
COPY --from=builder --chown=${USERNAME}:${USERNAME} --chmod=755 /app/.venv ${USER_DIR}/.venv
COPY --from=builder --chown=${USERNAME}:${USERNAME} --chmod=755 /app/sdpb  ${USER_DIR}/sdpb


USER ${USERNAME}
WORKDIR ${USER_DIR}
ENV PATH=${USER_DIR}/.venv/bin:${PATH}

EXPOSE 8000

# gunicorn.conf is set up so that Gunicorn settings are set by environment variables.
# Gunicorn setting [setting] is set by env var GUNICORN_[setting].
CMD ["gunicorn", "--config", "gunicorn.conf", "--log-config", "logging.conf", "-b", ":8000", "-k", "uvicorn.workers.UvicornWorker", "sdpb.wsgi:connexion_app"]
