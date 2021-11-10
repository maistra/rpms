# Run unit tests
%global with_tests 0
%global debug_package %{nil}

%global git_commit d74a7daea5635d00c86968d6620201301b02d4cc
%global git_shortcommit  %(c=%{git_commit}; echo ${c:0:7})

%global provider        github
%global provider_tld    com
%global project         maistra
%global repo            istio-operator

# https://github.com/maistra/istio-operator
%global provider_prefix %{provider}.%{provider_tld}/%{project}

# Use /usr/local as base dir, once upstream heavily depends on that
%global _prefix /usr/local

Name:           istio-operator
Version:        2.1.0
Release:        0%{?dist}
Summary:        A Kubernetes operator to manage Istio.
License:        ASL 2.0
URL:            https://%{provider_prefix}/%{repo}

Source0:        https://%{provider_prefix}/%{repo}/archive/%{git_commit}/%{repo}-%{git_commit}.tar.gz

%global goipath github.com/maistra/istio-operator
%gometa

%description
Istio-operator is a kubernetes operator to manage the lifecycle of Istio.

%prep

rm -rf %{name}-%{version} && mkdir -p %{name}-%{version}
tar zxf %{SOURCE0} -C %{name}-%{version} --strip=1

%setup -D -T

%build

%ifarch ppc64le s390x
export MINIMUM_SUPPORTED_VERSION=v1.1
%endif

export GOPROXY=off
export CGO_ENABLED=0
export COMMUNITY=false
export GO111MODULE=on
export VERSION=%{version}-%{release}
export GITREVISION=%{git_shortcommit}
export GITSTATUS=Clean
export GITTAG=%{version}
export GIT_UPSTREAM_REMOTE="_DUMMY_"
export OFFLINE_BUILD="true"
export MINIMUM_SUPPORTED_VERSION="${MINIMUM_SUPPORTED_VERSION}"

make compile collect-resources

echo "Operator built succesfully:"
./tmp/_output/bin/istio-operator --version

%install
rm -rf $RPM_BUILD_ROOT && mkdir -p $RPM_BUILD_ROOT%{_bindir}
cp ./tmp/_output/bin/istio-operator $RPM_BUILD_ROOT%{_bindir}/

# install the charts
CHARTS_DIR=$RPM_BUILD_ROOT%{_datadir}/istio-operator/helm
mkdir -p ${CHARTS_DIR}
cp -rpavT tmp/_output/resources/helm/ ${CHARTS_DIR}

# install the templates
TEMPLATES_DIR=$RPM_BUILD_ROOT%{_datadir}/istio-operator/default-templates
mkdir -p ${TEMPLATES_DIR}
cp -rpavT tmp/_output/resources/default-templates/ ${TEMPLATES_DIR}

#install manifests
cp -rpavT tmp/_output/resources/manifests/ $RPM_BUILD_ROOT/manifests

%files
%{_bindir}/istio-operator
%{_datadir}/istio-operator
/manifests

%changelog
* Tue Nov 2 2021 Jonh Wendell <jwendell@redhat.com> - 2.1.0-0
- Initial 2.1 release
