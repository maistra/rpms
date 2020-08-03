#!/bin/bash

set -o pipefail
set -e
set -u

function usage() {
  echo "Usage: $0 [-v <grafana version>]"
  echo
  exit 0
}

while getopts ":v:h" opt; do
  case ${opt} in
    v) GRAFANA_VERSION="${OPTARG}";;
    *) usage;;
  esac
done

SPEC_FILE="grafana.spec"
GRAFANA_VERSION=${GRAFANA_VERSION:-"$(grep '^Version:' ${SPEC_FILE} | awk '{print $2}')"}
CURRENT_RELEASE=$(grep '^%global release_number ' ${SPEC_FILE} | awk '{print $3}')
NEXT_RELEASE=$(( CURRENT_RELEASE + 1 ))

sed -i -e '/^Version: / s+[0-9][0-9.]*$+'"${GRAFANA_VERSION}"'+' ${SPEC_FILE}

./make_grafana_webpack.sh "${GRAFANA_VERSION}"

mv "grafana_webpack-${GRAFANA_VERSION}.tar.gz" "grafana_webpack-${GRAFANA_VERSION}-${NEXT_RELEASE}.tar.gz"
sed -i -e "s/^%global release_number .*/%global release_number ${NEXT_RELEASE}/" ${SPEC_FILE}

md5sum "grafana_webpack-${GRAFANA_VERSION}-${NEXT_RELEASE}.tar.gz" "grafana-${GRAFANA_VERSION}.tar.gz" > sources

echo "Updated release number from ${CURRENT_RELEASE} to ${NEXT_RELEASE}. Check the diff."
