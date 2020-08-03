#!/bin/bash -eu

[ $# -lt 1 ] && echo "Usage: $0 fedora-version" && exit 1
FEDORA_VERSION="$1"

if [ -d deps ]; then
    INSTALL_UNPUBLISHED_DEPENDENCIES=$'COPY deps/ /deps\nRUN cd /deps && dnf -y install *.rpm'
else
    INSTALL_UNPUBLISHED_DEPENDENCIES=""
fi

cat <<EOF | podman build -f - .
FROM fedora:${FEDORA_VERSION}
RUN dnf install -y rpkg
RUN mkdir /grafana /deps

${INSTALL_UNPUBLISHED_DEPENDENCIES}

COPY grafana.spec *.patch grafana-*.tar.gz grafana_webpack-*.tar.gz make_grafana_webpack.sh distro-defaults.ini /grafana
WORKDIR /grafana
RUN dnf -y builddep grafana.spec
RUN rpkg local
EOF
