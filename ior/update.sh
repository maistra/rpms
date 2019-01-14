#!/bin/bash

NEW_SOURCES=""

function usage() {
    echo "Usage: $0 [-i <SHA of ior>]"
    echo
    exit 0
}

while getopts ":i:v:" opt; do
  case ${opt} in
    i) IOR_SHA="${OPTARG}";;
    *) usage;;
  esac
done

[[ -z "${IOR_SHA}" ]] && IOR_SHA="$(grep '%global git_commit ' ior.spec | cut -d' ' -f3)"

function update_commit() {
    local sha="$1"

    local tarball="https://github.com/maistra/ior/archive/${sha}/ior-${sha}.tar.gz"
    local filename="ior-${sha}.tar.gz"

    echo -n "Checking ior...   "
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

    sed -i "s/%global git_commit .*/%global git_commit ${sha}/" ior.spec
    NEW_SOURCES="${NEW_SOURCES} ${filename}"
}

function new_sources() {
    echo
    echo "Updating sources file with ${NEW_SOURCES}"
    md5sum ${NEW_SOURCES} > sources
}

update_commit "${IOR_SHA}"
new_sources
