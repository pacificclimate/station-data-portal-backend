# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.245.0/containers/python-3/.devcontainer/base.Dockerfile


# [Choice] Ubuntu version (use ubuntu-22.04 or ubuntu-18.04 on local arm64/Apple Silicon): ubuntu-22.04, ubuntu-20.04, ubuntu-18.04
ARG VARIANT=ubuntu-24.04
FROM mcr.microsoft.com/vscode/devcontainers/base:${VARIANT}

# Postgres & our packages. Currently not customizable via VERSION param.
# RUN apt-get update \
#     && apt-get -y install --no-install-recommends curl ca-certificates gnupg
RUN curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN apt-get update \
    && apt-get -y install --no-install-recommends postgresql-plpython3-14 postgresql-14-postgis-3 libpq-dev
    
# Keep the inner (docker-in-docker) daemon off 172.17.0.0/16. Its default
# docker0 would otherwise collide with the outer bridge, making the outer
# gateway/DNS (172.17.0.1) look local and breaking name resolution.
RUN mkdir -p /etc/docker && printf '%s\n' \
    '{' \
    '  "bip": "10.200.0.1/24",' \
    '  "default-address-pools": [{ "base": "10.201.0.0/16", "size": 24 }]' \
    '}' > /etc/docker/daemon.json
