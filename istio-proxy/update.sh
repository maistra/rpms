#!/bin/bash

set -o pipefail
set -e
set -u

PROXY_NAME=istio-proxy

function usage() {
    echo "Usage: $0 [-i <SHA of proxy>]"
    echo
    exit 0
}

while getopts ":i:" opt; do
  case ${opt} in
    i) SHA="${OPTARG}";;
    *) usage;;
  esac
done

SHA=${SHA:-"$(grep '%global git_commit ' ${PROXY_NAME}.spec | cut -d' ' -f3)"}

function update_commit() {
    local sha="$1"

    local tarball="https://github.com/maistra/proxy/archive/${sha}/proxy-${sha}.tar.gz"
    local filename="proxy-${sha}.tar.gz"

    echo -n "Checking proxy...   "
    if [ ! -f "${filename}" ]; then
        echo "Downloading ${tarball}"
        if ! curl -Lfs "${tarball}" -o "${filename}"; then
            echo "Error downloading tarball, exiting."
            exit 1
        fi
    else
        echo "Already on disk, download not necessary"
    fi

    sed -i "s/%global git_commit .*/%global git_commit ${sha}/" "${PROXY_NAME}.spec"
	md5sum "${filename}" > sources
}

update_commit "${SHA}"
