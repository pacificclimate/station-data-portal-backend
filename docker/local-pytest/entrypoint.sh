# Note: we are in directory ${INSTALL_DIR}
cp "${CODEBASE_DIR}"/Pipfile .
# Point copied Pipfile at /codebase
sed -i '/sdpb/s|path = "."|path = "/codebase"|' Pipfile
pipenv install --dev
/bin/bash
