#!/bin/bash

set -o pipefail
set -e
set -u

function usage() {
    echo "Usage: $0 [-i <SHA of istio>]"
    echo
    exit 0
}

while getopts "i:" opt; do
  case ${opt} in
    i) ISTIO_SHA="${OPTARG}";;
    *) usage;;
  esac
done

ISTIO_SHA=${ISTIO_SHA:-"$(grep '%global git_commit ' istio.spec | cut -d' ' -f3)"}

function update_commit() {
    local sha="$1"

    local tarball="https://github.com/maistra/istio/archive/${sha}/istio-${sha}.tar.gz"
    local filename="istio-${sha}.tar.gz"

    echo -n "Checking istio...   "
    if [ ! -f "${filename}" ]; then
        echo "Downloading ${tarball}"
        if ! curl -Lfs "${tarball}" -o "${filename}"; then
            echo "Error downloading tarball, exiting."
            exit 1
        fi
    else
        echo "Already on disk, download not necessary"
    fi

    sed -i "s/%global git_commit .*/%global git_commit ${sha}/" istio.spec

    echo "Updating sources file with ${filename}"
    sha512sum --tag "${filename}" > sources

}

update_commit "${ISTIO_SHA}"
