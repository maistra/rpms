#!/bin/bash -eu

[ $# -ne 1 ] && echo "Usage: $0 grafana-X.Y.Z/" && exit 1
GRAFANA_SOURCES="$(readlink -f "$1")"

cd "$(mktemp -d)"
mkdir -p src/github.com/grafana
ln -s "${GRAFANA_SOURCES}" src/github.com/grafana/grafana
ln -s "${GRAFANA_SOURCES}/vendor/github.com/grafana/grafana-plugin-model" src/github.com/grafana/grafana-plugin-model
ln -s "${GRAFANA_SOURCES}/vendor/github.com/grafana/grafana-plugin-sdk-go" src/github.com/grafana/grafana-plugin-sdk-go

for pkg in grafana grafana-plugin-model grafana-plugin-sdk-go
do
    GOPATH=$(pwd) golist --imported --package-path "github.com/grafana/$pkg" --skip-self --template 'BuildRequires: golang({{.}})\n'
done | sed \
    -e "s,github.com/linkedin/goavro/v2,github.com/linkedin/goavro,g" \
    -e "s,github.com/go-xorm/xorm,xorm.io/xorm,g" \
    -e "s,github.com/robfig/cron/v3,gopkg.in/robfig/cron.v3,g" \
    -e "s,github.com/unknwon/com,github.com/Unknwon/com,g" \
    | sort | uniq
