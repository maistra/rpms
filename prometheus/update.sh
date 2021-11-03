#!/bin/bash

set -o pipefail
set -e
set -u

function usage() {
  echo "Usage: $0 [-i <SHA of prometheus>]"
  echo
  exit 0
}

while getopts ":i:" opt; do
  case ${opt} in
    i) PROMETHEUS_SHA="${OPTARG}";;
    *) usage;;
  esac
done

PROMETHEUS_SHA=${PROMETHEUS_SHA:-"$(grep '%global git_commit ' istio-prometheus.spec | cut -d' ' -f3)"}

function update_commit() {
    local sha="$1"

    local tarball="https://github.com/maistra/prometheus/archive/${sha}.tar.gz"
    local filename="${sha}.tar.gz"

    echo -n "Checking prometheus...   "
    if [ ! -f "${filename}" ]; then
        echo "Downloading ${tarball}"
        if ! curl -Lfs "${tarball}" -o "${filename}"; then
            echo "Error downloading tarball, exiting."
            exit 1
        fi
    else
        echo "Already on disk, download not necessary"
    fi

    sed -i "s/%global git_commit .*/%global git_commit ${sha}/" istio-prometheus.spec

    echo "Updating sources file with ${filename}"
    sha512sum --tag "${filename}" > sources
}

update_commit "${PROMETHEUS_SHA}"
