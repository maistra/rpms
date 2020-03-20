#!/bin/bash

set -o pipefail
set -e
set -u

NEW_SOURCES=""

function usage() {
    echo "Usage: $0 [-i <SHA of istio-operator>]"
    echo
    exit 0
}

while getopts ":i:v:" opt; do
  case ${opt} in
    i) ISTIO_OPERATOR_SHA="${OPTARG}";;
    *) usage;;
  esac
done

ISTIO_OPERATOR_SHA=${ISTIO_OPERATOR_SHA:="$(grep '%global git_commit ' istio-operator.spec | cut -d' ' -f3)"}

function update_commit() {
    local prefix="$1"
    local prefix_spec=${prefix/-/_}
    local operator_sha="$2"

    local operator_tarball="https://github.com/maistra/${prefix}istio-operator/archive/${operator_sha}/${prefix}istio-operator-${operator_sha}.tar.gz"
    local operator_filename="${prefix}istio-operator-${operator_sha}.tar.gz"

    echo -n "Checking ${prefix}istio-operator...   "
    if [ ! -f "${operator_filename}" ]; then
        echo "Downloading ${operator_tarball}"
        curl -Lfs ${operator_tarball} -o "${operator_filename}"
        if [ $? -ne 0 ]; then
            echo "Error downloading tarball, exiting."
            exit 1
        fi
    else
        echo "Already on disk, download not necessary"
    fi

    sed -i "s/%global ${prefix_spec}git_commit .*/%global ${prefix_spec}git_commit ${operator_sha}/" istio-operator.spec
    NEW_SOURCES="${NEW_SOURCES} ${operator_filename}"
}

function new_sources() {
    echo
    echo "Updating sources file with ${NEW_SOURCES}"
    md5sum ${NEW_SOURCES} > sources
}

update_commit "" "${ISTIO_OPERATOR_SHA}"
new_sources
