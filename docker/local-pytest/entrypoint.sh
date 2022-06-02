#!/bin/bash
# Note: we are in directory ${INSTALL_DIR}
cp -r "${CODEBASE_DIR}"/* "${INSTALL_DIR}"
# Point copied Pipfile at /codebase
# sed -i '/sdpb/s|path = "."|path = "/codebase"|' Pipfile
pipenv install --dev
/bin/bash
