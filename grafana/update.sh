#!/bin/bash

set -o pipefail
set -e
set -u

DIR=$(cd $(dirname $0) ; pwd -P)
NEW_SOURCES=""

source "${DIR}/container_cli_init.sh"

function usage() {
  echo "Usage: $0 [-v <grafana version>]"
  echo
  exit 0
}

while getopts ":v:" opt; do
  case ${opt} in
    v) GRAFANA_VERSION="${OPTARG}";;
    *) usage;;
  esac
done

GRAFANA_VERSION=${GRAFANA_VERSION:-"$(egrep '^Version:' istio-grafana.spec | awk '{print $2}')"}

sed -i -e '/^Version: / s+[0-9][0-9.]*$+'${GRAFANA_VERSION}'+' istio-grafana.spec

./run_container_build.sh "${GRAFANA_VERSION}"

${CONTAINER_CLI} run -v$DIR:/grafana --security-opt label=disable grafana-build-7.2.1 make -e VER=${GRAFANA_VERSION} clean all

SHA=$(sha256sum grafana-webpack-${GRAFANA_VERSION}.tar.gz | sed -e 's+ .*$++')
mv grafana-webpack-${GRAFANA_VERSION}.tar.gz grafana-webpack-${GRAFANA_VERSION}-${SHA}.tar.gz
sed -i -e 's+\(^%global *webpack_hash *\)[^ ]*$+\1'${SHA}'+' istio-grafana.spec

NEW_SOURCES="grafana-webpack-${GRAFANA_VERSION}-${SHA}.tar.gz grafana-${GRAFANA_VERSION}.tar.gz grafana-vendor-${GRAFANA_VERSION}.tar.xz"

echo "Updating sources file with ${NEW_SOURCES}"
sha512sum --tag ${NEW_SOURCES} > sources
