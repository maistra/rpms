CONTAINER_CLI=${CONTAINER_CLI:-podman}
if ! which ${CONTAINER_CLI} >/dev/null 2>&1; then
        echo "${CONTAINER_CLI} needs to be installed"
        exit 1
fi
