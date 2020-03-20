#!/bin/bash

set -o pipefail
set -e
set -u

NEW_SOURCES=""

function usage() {
    echo "Usage: $0 [-i <Bazel version>]"
    echo
    exit 0
}

while getopts ":i:v:" opt; do
  case ${opt} in
    i) BAZEL_VERSION="${OPTARG}";;
    *) usage;;
  esac
done

BAZEL_VERSION=${BAZEL_VERSION:-"$(grep 'Version: ' bazel.spec | awk '{print $2}')"}

function update_version() {
    local version="$2"

    local tarball="https://github.com/bazelbuild/bazel/releases/download/${version}/bazel-${version}-dist.zip"
    local filename="bazel-${version}.tar.gz"

    echo -n "Checking bazel...   "
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

    sed -i "s/Version: .*/Version:        ${version}/" bazel.spec
    NEW_SOURCES="${NEW_SOURCES} ${filename}"
}

function new_sources() {
    echo
    echo "Updating sources file with ${NEW_SOURCES}"
    md5sum ${NEW_SOURCES} > sources
}

update_version "" "${BAZEL_VERSION}"
new_sources