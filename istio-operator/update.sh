#!/bin/bash

set -o pipefail
set -e
set -u

function usage() {
    echo "Usage: $0 [-i <SHA of istio-operator>]"
    echo
    exit 0
}

while getopts "i:" opt; do
  case ${opt} in
    i) ISTIO_OPERATOR_SHA="${OPTARG}";;
    *) usage;;
  esac
done

ISTIO_OPERATOR_SHA=${ISTIO_OPERATOR_SHA:="$(grep '%global git_commit ' istio-operator.spec | cut -d' ' -f3)"}

function update_commit() {
    local operator_sha="$1"

    local operator_tarball="https://github.com/maistra/istio-operator/archive/${operator_sha}/istio-operator-${operator_sha}.tar.gz"
    local operator_filename="istio-operator-${operator_sha}.tar.gz"

    echo -n "Checking istio-operator...   "
    if [ ! -f "${operator_filename}" ]; then
        echo "Downloading ${operator_tarball}"
        if ! curl -Lfs "${operator_tarball}" -o "${operator_filename}"; then
            echo "Error downloading tarball, exiting."
            exit 1
        fi
    else
        echo "Already on disk, download not necessary"
    fi

    sed -i "s/%global git_commit .*/%global git_commit ${operator_sha}/" istio-operator.spec

    echo "Updating sources file with ${operator_filename}"
    sha512sum --tag "${operator_filename}" > sources
}

update_commit "${ISTIO_OPERATOR_SHA}"
