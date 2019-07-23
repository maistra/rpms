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

[[ -z "${PROXY_SHA}" ]] && PROXY_SHA="$(grep '%global git_commit ' istio-proxy.spec | cut -d' ' -f3)"

function update_commit() {
		local sha=$1
		echo
		echo "Updating spec file with ${sha}"
		sed -i "s/%global git_commit .*/%global git_commit ${sha}/" istio-proxy.spec
}

function new_sources() {
	local filename=$1
	echo
	echo "Updating sources file with ${filename}"
	md5sum ${filename} > sources
}

function get_sources() {
	local proxy_sha=$1
	FETCH_DIR=/tmp CREATE_TARBALL=true ./fetch.sh
	local tar_name=istio-proxy.${proxy_sha}.tar.xz
	cp -p /tmp/proxy-full.tar.xz ${tar_name}

	new_sources ${tar_name}
	md5sum ${tar_name} > sources
}

update_commit "${PROXY_SHA}"
get_sources "${PROXY_SHA}"
