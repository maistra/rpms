#!/bin/bash

NEW_SOURCES=""

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

[[ -z "${GRAFANA_VERSION}" ]] && GRAFANA_VERSION="$(egrep '^Version:' grafana.spec | awk '{print $2}')"

sed -i -e '/^Version: / s+[0-9][0-9.]*$+'${GRAFANA_VERSION}'+' grafana.spec
sed -i -e '/^\/grafana-[0-9][0-9.]*$/d' .gitignore

echo "/grafana-${GRAFANA_VERSION}" >> .gitignore

./make_grafana_webpack.sh "${GRAFANA_VERSION}"
SHA=$(sha256sum grafana_webpack-${GRAFANA_VERSION}.tar.gz | sed -e 's+ .*$++')
mv grafana_webpack-${GRAFANA_VERSION}.tar.gz grafana_webpack-${GRAFANA_VERSION}.${SHA}.tar.gz
sed -i -e 's+\(^%global  *webpack_hash  *\)[^ ]*$+\1'${SHA}'+' grafana.spec

NEW_SOURCES="grafana_webpack-${GRAFANA_VERSION}.${SHA}.tar.gz grafana-${GRAFANA_VERSION}.tar.gz"

echo "Updating sources file with ${NEW_SOURCES}"
md5sum ${NEW_SOURCES} > sources
