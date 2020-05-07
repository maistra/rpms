#!/bin/bash

# Copyright (C) 2020 Red Hat, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# We need: copr, git, fedpkg

set -e
set -o pipefail
set -u

if [ "${VERBOSE:-}" == "1" ]; then
  set -x
fi

SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# shellcheck disable=SC1090
source "${SCRIPTPATH}/utils.sh"

START_TIME=${SECONDS}
COPR_REPO="${COPR_REPO:-@maistra-dev/istio}"
COPR_CONFIG="${COPR_CONFIG:-${HOME}/.config/copr}"
COPR_COMMAND="${COPR_COMMAND:-copr --config ${COPR_CONFIG}}"

# Max waiting time for the build to complete, in seconds
TIME_WAIT=${TIME_WAIT:-1200}

# If set, it will override the version field of the RPM
DEV_VERSION=${DEV_VERSION:-}

function patch_spec() {
  [ -z "${DEV_VERSION}" ] && return

  echo "DEV_VERSION set, patching the .spec Version field to: ${DEV_VERSION}"
  sed -i "s/^Version:.*/Version: ${DEV_VERSION}/" "${REPO}.spec"
}

function generate_srpm() {
  fedpkg --release el8 srpm
}

function invoke_copr_build() {
  local re='^[0-9]+$'
  local build_id

  build_id=$(${COPR_COMMAND} build --nowait "${COPR_REPO}" ./*.src.rpm | grep 'Created builds:' | awk '{print $3}')
  if [[ ! ${build_id} =~ ${re} ]]; then
    error "Error invoking copr to build the package"
  fi

  BUILD_ID="${build_id}"
}

function build_package() {
  echo "Building ${REPO} on COPR"

  patch_spec
  generate_srpm
  invoke_copr_build
}

function wait_for_build_to_finish() {
  local computed_time
  local start_time=${SECONDS}
  local result
  local build_url="https://copr.fedorainfracloud.org/coprs/build/${BUILD_ID}/"

  SECONDS=0
  echo
  echo "Waiting for COPR build to finish (max wait time: ${TIME_WAIT}s)"

  # Give it a little time as it's unlikely the build will finish before this
  sleep 30

  while true; do
    result=$(${COPR_COMMAND} status "${BUILD_ID}")
    case ${result} in
      succeeded)
        echo "Build ${build_url} succeeded"
        break
        ;;

      pending | importing | running)
        ;;

      *)
        echo "Build ${build_url} failed"
        break
        ;;
    esac

    computed_time=$(( SECONDS - start_time ))
    if [ ${computed_time} -ge "${TIME_WAIT}" ]; then
      echo "Time out, giving out on build ${build_url}"
      break
    fi

    sleep 10
  done

  if [ "${result}" != "succeeded" ]; then
    error
  fi
}

function main() {
  REPO=${REPO:-"$(guess_repo_name)"}
  if [ -z "${REPO}" ]; then
    echo "Unknown repository. Please set the REPO variable."
    exit 1
  fi

  build_package
  wait_for_build_to_finish

  echo
  echo "Elapsed time: $(( SECONDS - START_TIME ))s"
  echo
}

main
