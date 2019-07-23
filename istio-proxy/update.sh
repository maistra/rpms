#!/bin/bash

NEW_SOURCES=""

function usage() {
	echo "Usage: $0 [-i <SHA of istio>]"
	echo
	exit 0
}

while getopts ":i:v:" opt; do
	case ${opt} in
		i) PROXY_SHA="${OPTARG}";;
		*) usage;;
	esac
done

[[ -z "${PROXY_SHA}" ]] && PROXY_SHA="$(grep '%global git_commit ' istio-proxy.spec | cut -d' ' -f3)"

function update_commit() {
		sha=$1
		echo
		echo "Updating spec file with $1"
    sed -i "s/%global git_commit .*/%global git_commit ${sha}/" istio-proxy.spec
}

function new_sources() {
	sha=$1
	echo
	echo "Updating sources file with ${sha}"
	md5sum ${sha} > sources
}

function get_sources() {
	FETCH_DIR=/tmp CREATE_TARBALL=true ./fetch.sh
	TAR_NAME=istio-proxy.${PROXY_SHA}.tar.xz
	cp -p /tmp/proxy-full.tar.xz ${TAR_NAME}

	new_sources ${TAR_NAME}
	md5sum ${TAR_NAME} > sources
}

update_commit "${PROXY_SHA}"
get_sources "" "${PROXY_SHA}"
