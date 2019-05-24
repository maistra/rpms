#!/bin/bash

NEW_SOURCES=""

function usage() {
    echo "Usage: $0 [-i <SHA of istio-operator>] [-c <SHA of istio>]"
    echo
    exit 0
}

while getopts ":i:c:v:" opt; do
  case ${opt} in
    i) ISTIO_OPERATOR_SHA="${OPTARG}";;
    c) ISTIO_CHARTS_SHA="${OPTARG}";;
    *) usage;;
  esac
done

[[ -z "${ISTIO_OPERATOR_SHA}" ]] && ISTIO_OPERATOR_SHA="$(grep '%global git_commit ' istio-operator.spec | cut -d' ' -f3)"
[[ -z "${ISTIO_CHARTS_SHA}" ]] && ISTIO_CHARTS_SHA="$(grep '%global charts_git_commit ' istio-operator.spec | cut -d' ' -f3)"

function update_commit() {
    local prefix="$1"
    local prefix_spec=${prefix/-/_}
    local operator_sha="$2"
    local charts_sha="$3"

    local operator_tarball="https://github.com/maistra/${prefix}istio-operator/archive/${operator_sha}/${prefix}istio-operator-${operator_sha}.tar.gz"
    local operator_filename="${prefix}istio-operator-${operator_sha}.tar.gz"

    local charts_tarball="https://github.com/maistra/${prefix}istio/archive/${charts_sha}/${prefix}istio-${charts_sha}.tar.gz"
    local charts_filename="${prefix}istio-${charts_sha}.tar.gz"

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

    echo -n "Checking ${prefix}istio... (charts)  "
    if [ ! -f "${charts_filename}" ]; then
        echo "Downloading ${charts_tarball}"
        curl -Lfs ${charts_tarball} -o "${charts_filename}"
        if [ $? -ne 0 ]; then
            echo "Error downloading tarball, exiting."
            exit 1
        fi
    else
        echo "Already on disk, download not necessary"
    fi

    sed -i "s/%global ${prefix_spec}git_commit .*/%global ${prefix_spec}git_commit ${operator_sha}/" istio-operator.spec
    sed -i "s/%global ${prefix_spec}charts_git_commit .*/%global ${prefix_spec}charts_git_commit ${charts_sha}/" istio-operator.spec
    NEW_SOURCES="${NEW_SOURCES} ${operator_filename} ${charts_filename}"
}

function new_sources() {
    echo
    echo "Updating sources file with ${NEW_SOURCES}"
    md5sum ${NEW_SOURCES} > sources
}

update_commit "" "${ISTIO_OPERATOR_SHA}" "${ISTIO_CHARTS_SHA}"
new_sources
