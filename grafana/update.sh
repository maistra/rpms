#!/bin/bash

NEW_SOURCES=""

function usage() {
    echo "Usage: $0 [-i <SHA of istio>]"
    echo
    exit 0
}

while getopts ":i:v:" opt; do
  case ${opt} in
    i) GRAFANA_VERSION="${OPTARG}";;
    *) usage;;
  esac
done

[[ -z "${GRAFANA_VERSION}" ]] && GRAFANA_VERSION="$(grep '%global version ' grafana.spec | cut -d' ' -f3)"

function update_commit() {
    local prefix="$1"
    local prefix_spec=${prefix/-/_}
    local sha="$2"

    local tarball="https://github.com/grafana/grafana/archive/v${sha}.tar.gz"
    local filename="v${sha}.tar.gz"

    echo -n "Checking Grafana...   "
		echo "Grafana version: ${sha}"
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

    sed -i "s/%global version .*/%global version ${sha}/" grafana.spec
    NEW_SOURCES="${NEW_SOURCES} ${filename}"
}

function new_sources() {
    echo
    echo "Updating sources file with ${NEW_SOURCES}"
    md5sum ${NEW_SOURCES} > sources
}

update_commit "" "${GRAFANA_VERSION}"
./make_grafana_webpack.sh "${GRAFANA_VERSION}"
new_sources
