#!/bin/bash

NEW_SOURCES=""

function usage() {
    echo "Usage: $0 [-i <SHA of prometheus>]"
    echo
    exit 0
}

while getopts ":i:v:" opt; do
  case ${opt} in
    i) PROMETHEUS_SHA="${OPTARG}";;
    *) usage;;
  esac
done

[[ -z "${PROMETHEUS_SHA}" ]] && PROMETHEUS_SHA="$(grep '%global git_commit ' prometheus.spec | cut -d' ' -f3)"

function update_commit() {
    local prefix="$1"
    local prefix_spec=${prefix/-/_}
    local sha="$2"

    local tarball="https://github.com/openshift/prometheus/archive/${PROMETHEUS_SHA}.tar.gz"
    local filename="${prefix}${sha}.tar.gz"

    echo -n "Checking ${prefix}prometheus...   "
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

    sed -i "s/%global ${prefix_spec}git_commit .*/%global ${prefix_spec}git_commit ${sha}/" prometheus.spec
    NEW_SOURCES="${NEW_SOURCES} ${filename}"
}

function new_sources() {
    echo
    echo "Updating sources file with ${NEW_SOURCES}"
    md5sum ${NEW_SOURCES} > sources
}

update_commit "" "${PROMETHEUS_SHA}"
new_sources
