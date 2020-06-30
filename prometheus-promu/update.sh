#!/bin/bash

set -o pipefail
set -e
set -u

NEW_SOURCES=""

function usage() {
  echo "Usage: $0 [-i <version of promu>]"
  echo
  exit 0
}

while getopts ":i:" opt; do
  case ${opt} in
    i) PROMU_VERSION="${OPTARG}";;
    *) usage;;
  esac
done

PROMU_VERSION=${PROMU_VERSION:-"$(grep 'Version: ' prometheus-promu.spec | awk '{print $2}')"}

function update_version() {
    local version="$1"

    local tarball="https://github.com/prometheus/promu/archive/v${version}.tar.gz"
    local filename="v${version}.tar.gz"

    echo -n "Checking promu...   "
    if [ ! -f "${filename}" ]; then
        echo "Downloading ${tarball}"
        curl -Lfs ${tarball} -o "${filename}"
        if [ $? -ne 0 ]; then
            echo "Error downloading tarball, exiting."
            exit 1
        fi
    else
        echo "Already on disk, download not necessary"
    fi

    sed -i "s/Version:        .*/Version:        ${version}/" prometheus-promu.spec
    NEW_SOURCES="${NEW_SOURCES} ${filename}"
}

function new_sources() {
    echo
    echo "Updating sources file with ${NEW_SOURCES}"
    md5sum ${NEW_SOURCES} > sources
}

update_version "${PROMU_VERSION}"
new_sources
