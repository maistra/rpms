#!/bin/bash

set -o pipefail
set -e
set -u

NEW_SOURCES=""

function usage() {
    echo "Usage: $0 [-i <version of libwee8>]"
    echo
    exit 0
}

while getopts ":i:" opt; do
  case ${opt} in
    i) SHA="${OPTARG}";;
    *) usage;;
  esac
done

SHA=${SHA:-"$(grep 'Version: ' libwee8.spec | awk '{print $2}')"}

function update_commit() {
    local sha="$1"

    local tarball="https://storage.googleapis.com/envoyproxy-wee8/wee8-${SHA}.tar.gz"
    local filename="wee8-${SHA}.tar.gz"

    echo -n "Checking tarball...   "
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

    sed -i "s/^Version: .*/Version: ${SHA}/" libwee8.spec
    md5sum "${filename}" > sources
}

update_commit "${SHA}"
