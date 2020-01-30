#!/bin/bash

PROXY_SHA=""
function usage() {
    echo "Usage: $0 [-i <SHA of istio>]"
    echo
    exit 0
}

while getopts ":i:" opt; do
    case ${opt} in
        i) PROXY_SHA="${OPTARG}";;
        *) usage;;
    esac
done

[[ -z "${PROXY_SHA}" ]] && PROXY_SHA="$(grep '%global proxy_git_commit ' istio-proxy.spec | cut -d' ' -f3)"
[[ -z "${PROXY_OPENSSL_SHA}" ]] && PROXY_OPENSSL_SHA="$(grep '%global proxy_openssl_git_commit ' istio-proxy.spec | cut -d' ' -f3)"
[[ -z "${ENVOY_OPENSSL_SHA}" ]] && ENVOY_OPENSSL_SHA="$(grep '%global envoy_openssl_git_commit ' istio-proxy.spec | cut -d' ' -f3)"
[[ -z "${JWT_VERIFY_LIB_OPENSSL_SHA}" ]] && JWT_VERIFY_LIB_OPENSSL_SHA="$(grep '%global jwt_openssl_git_commit ' istio-proxy.spec | cut -d' ' -f3)"


function update_commit() {
    local proxy_sha=$1
    local proxy_openssl_sha=$2
    local envoy_openssl_sha=$3
    local jwt_openssl_sha=$4

    echo
    echo "Updating spec file with Proxy SHA: ${proxy_sha}"
    sed -i "s/%global git_commit .*/%global proxy_git_commit ${proxy_sha}/" istio-proxy.spec

    echo "Updating spec file with Proxy OpenSSL SHA: ${proxy_openssl_sha}"
    sed -i "s/%global git_commit .*/%global proxy_openssl_git_commit ${proxy_openssl_sha}/" istio-proxy.spec

    echo "Updating spec file with Envoy OpenSSL SHA: ${envoy_openssl_sha}"
    sed -i "s/%global git_commit .*/%global envoy_openssl_git_commit ${envoy_openssl_sha}/" istio-proxy.spec

    echo "Updating spec file with JWT Verify Lib OpenSSL SHA: ${jwt_openssl_sha}"
    sed -i "s/%global git_commit .*/%global jwt_openssl_git_commit ${jwt_openssl_sha}/" istio-proxy.spec
}

function new_sources() {
    local filename=$1
    echo
    echo "Updating sources file with ${filename}"

    md5sum ${filename} > sources
    local checksum=$(awk '{print $1}' sources)

    sed -i "s/%global checksum .*/%global checksum ${checksum}/" istio-proxy.spec

    local checksumFilename=istio-proxy.${checksum}.tar.xz
    mv $filename $checksumFilename
    sed -i "s/${filename}/${checksumFilename}/" sources
}

function get_sources() {
    local proxy_sha=$1
    local proxy_openssl_sha=$2
    local envoy_openssl_sha=$3
    local jwt_openssl_sha=$4

    FETCH_DIR=/tmp CREATE_TARBALL=true PROXY_GIT_COMMIT_HASH=${proxy_sha} \
    ISTIO_PROXY_OPENSSL_GIT_COMMIT_HASH=${proxy_openssl_sha} \
    ENVOY_OPENSSL_GIT_COMMIT_HASH=${envoy_openssl_sha} \
    JWT_VERIFY_LIB_OPENSSL_GIT_COMMIT_HASH=${jwt_openssl_sha} \
    ./fetch.sh

    local tar_name=istio-proxy.${proxy_sha}.tar.xz
    cp -p /tmp/proxy-full.tar.xz ${tar_name}

    new_sources ${tar_name}

}

update_commit "${PROXY_SHA}" "${PROXY_OPENSSL_SHA}" "${ENVOY_OPENSSL_SHA}" "${JWT_VERIFY_LIB_OPENSSL_SHA}"
get_sources "${PROXY_SHA}" "${PROXY_OPENSSL_SHA}" "${ENVOY_OPENSSL_SHA}" "${JWT_VERIFY_LIB_OPENSSL_SHA}"
