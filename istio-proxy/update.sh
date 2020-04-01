#!/bin/bash

set -o pipefail
set -e
set -u

proxy_name=istio-proxy

function usage() {
	echo "Usage: $0 [-p <SHA of istio-proxy>]"
	echo
	exit 0
}

while getopts ":p:" opt; do
	case ${opt} in
		p) PROXY_SHA="${OPTARG}";;
		*) usage;;
	esac
done

PROXY_SHA=${PROXY_SHA:-"$(grep '%global proxy_git_commit ' ${proxy_name}.spec | cut -d' ' -f3)"}

function update_commit() {
		local proxy_sha=$1

		echo
		echo "Updating spec file with Proxy SHA: ${proxy_sha}"
    sed -i "s/%global proxy_git_commit .*/%global proxy_git_commit ${proxy_sha}/" ${proxy_name}.spec

}

#update_bazel_version checks ${proxy_name}.spec for the specified bazel version and updates common.sh
function update_bazel_version() {
    bazelVersion=$(grep 'BuildRequires:  bazel =' ${proxy_name}.spec | cut -d ' ' -f5)
    sed -i "s/^[ ]*BAZEL_VERSION=.*/  BAZEL_VERSION=${bazelVersion}/" common.sh
}

function new_sources() {
	local filename=$1

	md5sum ${filename} > sources
	local checksum=$(awk '{print $1}' sources)

	sed -i "s/%global checksum .*/%global checksum ${checksum}/" ${proxy_name}.spec

	local checksumFilename=${proxy_name}.${checksum}.tar.gz
	mv $filename $checksumFilename

	echo
	echo "Updating sources file with ${checksumFilename}"
	sed -i "s/${filename}/${checksumFilename}/" sources
}

function get_sources() {
	local proxy_sha=$1

	FETCH_DIR=/tmp CREATE_TARBALL=true \
	PROXY_DIR=istio-proxy PROXY_GIT_COMMIT_HASH=${proxy_sha} \
	./fetch.sh

	local tar_name=${proxy_name}.${proxy_sha}.tar.gz
	cp -p /tmp/proxy-full.tar.gz ${tar_name}

	new_sources ${tar_name}

}

update_commit "${PROXY_SHA}"
update_bazel_version
get_sources "${PROXY_SHA}"
