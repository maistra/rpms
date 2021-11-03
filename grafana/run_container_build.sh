#!/bin/bash -eu

DIR=$(cd $(dirname $0) ; pwd -P)

[ $# -lt 1 ] && echo "Usage: $0 GRAFANA_VERSION" && exit 1
GRAFANA_VERSION=${1}

source "${DIR}/container_cli_init.sh"

if [ -d deps ]; then
    INSTALL_UNPUBLISHED_DEPENDENCIES=$'COPY deps/ /deps\nRUN cd /deps && dnf -y install *.rpm'
else
    INSTALL_UNPUBLISHED_DEPENDENCIES=""
fi

cat <<EOF | ${CONTAINER_CLI} build -t grafana-build-${GRAFANA_VERSION}  -f - .
FROM registry.fedoraproject.org/fedora:32
RUN dnf install -y rpkg make gcc gcc-g++ nodejs-12* npm wget python3-packaging
RUN mkdir /grafana /deps

${INSTALL_UNPUBLISHED_DEPENDENCIES}

COPY servicemesh-grafana.spec *.patch distro-defaults.ini Makefile build_frontend.sh list_bundled_nodejs_packages.py /grafana/
WORKDIR /grafana
RUN dnf -y builddep servicemesh-grafana.spec
RUN npm install -g yarn
EOF
