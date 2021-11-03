#!/bin/bash

set -o pipefail
set -e
set -u

SPEC_NAME=istio-ratelimit.spec

function usage() {
    echo "Usage: $0 [-p <SHA of ratelimit>]"
    echo
    exit 0
}

while getopts ":p:" opt; do
  case ${opt} in
    p) SHA="${OPTARG}";;
    *) usage;;
  esac
done

SHA=${SHA:-"$(grep '%global git_commit ' ${SPEC_NAME} | cut -d' ' -f3)"}

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

    sed -i "s/%global ${commit} .*/%global ${commit} ${sha}/" "${SPEC_NAME}"
}

update_commit "ratelimit" "git_commit" "${SHA}" "https://github.com/maistra/ratelimit/archive/${SHA}/ratelimit-${SHA}.tar.gz"
sha512sum --tag "ratelimit-${SHA}.tar.gz" > sources
