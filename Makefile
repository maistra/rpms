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

SHELL   := /bin/bash
VERBOSE ?= 0

export VERBOSE

RPMS := grafana prometheus-promu prometheus ior istio istio-cni istio-operator
UPDATE_RPMS := $(addprefix update-,${RPMS})
BUILD_RPMS := $(addprefix build-copr-,${RPMS})

update: ${UPDATE_RPMS}

update-grafana:
	cd grafana && ./update.sh -v $$GRAFANA_VERSION $$GRAFANA_PR

update-prometheus-promu:
	cd prometheus-promu && ./update.sh $$PROMETHEUS_PROMU_COMMIT $$PROMETHEUS_PROMU_PR

update-istio-proxy:
	cd istio-proxy && ./update.sh $$ISTIO_PROXY_COMMIT $$ISTIO_PROXY_PR

update-%: COMMIT_VARNAME=$(shell echo $* | tr a-z A-Z | sed -e 's,-,_,g')_COMMIT
update-%: PR_VARNAME=$(shell echo $* | tr a-z A-Z | sed -e 's,-,_,g')_PR
update-%:
	cd $* && \
	REPO=$* ../common/update.sh $$$(COMMIT_VARNAME) $$$(PR_VARNAME)

lint:
	find . -name '*.sh' -print0 | xargs -0 -r shellcheck

build-copr: ${BUILD_RPMS}

build-copr-grafana:
	cd grafana && DEV_VERSION= REPO=grafana ../common/build-copr.sh

build-copr-prometheus-promu:
	cd prometheus-promu && DEV_VERSION= REPO=prometheus-promu ../common/build-copr.sh

build-copr-istio-proxy:
	cd istio-proxy && DEV_VERSION= REPO=istio-proxy ../common/build-copr.sh

build-copr-%:
	cd $* && \
	REPO=$* ../common/build-copr.sh

test: lint update build-copr
