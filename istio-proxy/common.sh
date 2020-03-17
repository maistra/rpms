set -x
set -e

#if the user has Bazelisk installed, then USE_BAZEL_VERSION will fix the bazel
#version. If not, error out.
if [ -z "${BAZEL_VERSION}" ]; then
  BAZEL_VERSION=1.1.0
fi
export USE_BAZEL_VERSION=${BAZEL_VERSION}

function check_dependencies() {
  RESULT=$(bazel version)
  rm -rf ${HOME}/.cache/bazel

  if [[ $RESULT != *"${BAZEL_VERSION}"* ]]; then
    echo "Error: Istio Proxy requires Bazel ${BAZEL_VERSION}"
    exit -1
  fi
}
function set_python_rules_date() {
  pushd ${CACHE_DIR}
    find . -type f -name "rules" | xargs touch -m -t 210012120101
  popd
}

function set_path() {
  if [ ! -f "${HOME}/python" ]; then
    cp /usr/bin/python3 ${HOME}/python
  fi

  export PATH=$PATH:$HOME
}

function replace_text() {
  if [ ! -z "$1" ]; then
    FILE="$1"
  fi
  START_LINES=$(grep -nr "${DELETE_START_PATTERN}" ${FILE} | cut -d':' -f1)
  OFFSET=0
  while read -r START; do
    START=$((${START} + ${START_OFFSET} + ${OFFSET}))
    if [[ ! -z "${DELETE_STOP_PATTERN}" ]]; then
      STOP=$(tail --lines=+${START}  ${FILE} | grep -nr "${DELETE_STOP_PATTERN}" - |  cut -d':' -f1 | head -1)
      CUT=$((${START} + ${STOP} - 1))
    else
      CUT=$((${START}))
    fi
    if [ "${START}" != "0" ]; then
      CUT_TEXT=$(sed -n "${START},${CUT} p" ${FILE})
      sed -i "${START},${CUT} d" ${FILE}
      if [[ ! -z "${ADD_TEXT}" ]]; then
        ex -s -c "${START}i|${ADD_TEXT}" -c x ${FILE}
      fi
    fi
    ADDED_LINES=$(echo "${ADD_TEXT}" | wc -l)
    OFFSET=$((${OFFSET} + ${ADDED_LINES} - 2))
  done <<< $START_LINES
}

function set_proxy_dirs() {
  PROXY_DIR=${PROXY_DIR:-istio-proxy}
  PROXY_FETCH_DIR=${FETCH_DIR}/${PROXY_DIR}
  ENVOY_DIR=${PROXY_FETCH_DIR}/envoy
}