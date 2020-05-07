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

function guess_repo_name() {
  local dir_name

  dir_name="$(basename "$(pwd)")"
  if [[ ${dir_name} == rpm-* ]]; then
    echo "${dir_name#rpm-}"
  fi
}

function error() {
  [ $# -gt 0 ] && echo "$@"
  exit 1
}
