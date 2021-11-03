#!/bin/bash

set -o pipefail
set -e
set -u

PROXY_NAME=istio-proxy

function usage() {
    echo "Usage: $0 [-p <SHA of proxy>]"
    echo
    exit 0
}

while getopts ":p:" opt; do
  case ${opt} in
    p) SHA="${OPTARG}";;
    *) usage;;
  esac
done

SHA=${SHA:-"$(grep '%global git_commit ' ${PROXY_NAME}.spec | cut -d' ' -f3)"}

function update_commit() {
    local name="$1"
    local commit="$2"
    local sha="$3"
    local tarball="$4"

    local filename="$(echo $tarball | sed -s 's+^.*/++')"

    echo -n "Checking ${name}...   "
    if [ ! -f "${filename}" ]; then
        echo "Downloading ${tarball}"
        if ! curl -Lfs "${tarball}" -o "${filename}"; then
            echo "Error downloading tarball, exiting."
            exit 1
        fi
    else
        echo "Already on disk, download not necessary"
    fi

    sed -i "s/%global ${commit} .*/%global ${commit} ${sha}/" "${PROXY_NAME}.spec"
}

update_commit "proxy" "git_commit" "${SHA}" "https://github.com/maistra/proxy/archive/${SHA}/proxy-${SHA}.tar.gz"
sha512sum --tag "proxy-${SHA}.tar.gz" > sources
