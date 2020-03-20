#!/bin/bash

set -o pipefail
set -e
set -u

NEW_SOURCES=""

function usage() {
    echo "Usage: $0 [-i <SHA of istio-cni>]"
    echo
    exit 0
}

while getopts ":i:v:" opt; do
  case ${opt} in
    i) ISTIO_CNI_SHA="${OPTARG}";;
    *) usage;;
  esac
done

ISTIO_CNI_SHA=${ISTIO_CNI_SHA:-"$(grep '%global git_commit ' istio-cni.spec | cut -d' ' -f3)"}

function update_commit() {
    local sha="$1"

    local tarball="https://github.com/maistra/istio-cni/archive/${sha}/istio-cni-${sha}.tar.gz"
    local filename="istio-cni-${sha}.tar.gz"

    echo -n "Checking istio-cni...   "
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

    sed -i "s/%global git_commit .*/%global git_commit ${sha}/" istio-cni.spec
    NEW_SOURCES="${NEW_SOURCES} ${filename}"
}

function new_sources() {
    echo
    echo "Updating sources file with ${NEW_SOURCES}"
    md5sum ${NEW_SOURCES} > sources
}

update_commit "${ISTIO_CNI_SHA}"
new_sources
