# Generate devel rpm
%global with_devel 0
# Build with debug info rpm
%global with_debug 0
# Run unit tests
%global with_tests 0
# Build test binaries
%global with_test_binaries 0

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%global git_commit e7b48bdb25c5dd49d8fbe34acea05185719a4379
%global git_shortcommit  %(c=%{git_commit}; echo ${c:0:7})

%global provider        github
%global provider_tld    com
%global project         maistra
%global repo            istio-operator
# https://github.com/maistra/istio-operator
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}

# Use /usr/local as base dir, once upstream heavily depends on that
%global _prefix /usr/local

Name:           istio-operator
Version:        0.7.0
Release:        3%{?dist}
Summary:        A Kubernetes operator to manage Istio.
License:        ASL 2.0
URL:            https://%{provider_prefix}

Source0:        https://%{provider_prefix}/archive/%{git_commit}/%{repo}-%{git_commit}.tar.gz

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 aarch64 %{arm}}
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  golang >= 1.9

%description
Istio-operator is a kubernetes operator to manage the lifecycle of Istio.

%if 0%{?with_devel}
%package devel
Summary:       %{summary}
BuildArch:     noarch

%description devel
Istio-operator is a kubernetes operator to manage the lifecycle of Istio.
%endif

%prep

rm -rf OPERATOR
mkdir -p OPERATOR/src/github.com/maistra/istio-operator
tar zxf %{SOURCE0} -C OPERATOR/src/github.com/maistra/istio-operator --strip=1

%build
cd OPERATOR
export GOPATH=$(pwd):%{gopath}
cd src/github.com/maistra/istio-operator/tmp/build/
./build.sh

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_bindir}
cd OPERATOR/src/github.com/maistra/istio-operator/tmp/build/

cd tmp/_output/bin/
%if 0%{?with_debug}
    cp -pav istio-operator $RPM_BUILD_ROOT%{_bindir}/
%else
    mkdir stripped
    strip -o stripped/istio-operator -s istio-operator
    cp -pav stripped/istio-operator $RPM_BUILD_ROOT%{_bindir}/
%endif

%files
%{_bindir}/istio-operator

%changelog
* Mon Jan 28 2019 Kevin Conner <kconner@redhat.com> - 0.7.0-3
- Updates to 3scale adapter integration

* Fri Jan 25 2019 Kevin Conner <kconner@redhat.com> - 0.7.0-2
- Updated to include 3scale adapter configuration

* Thu Jan 17 2019 Kevin Conner <kconner@redhat.com> - 0.7.0
- Updated to 0.7.0

* Thu Dec 20 2018 Kevin Conner <kconner@redhat.com> - 0.6.0
- Updated to 0.6.0

* Fri Nov 23 2018 Kevin Conner <kconner@redhat.com> - 0.5.0
- Updated to 0.5.0

* Wed Oct 31 2018 Kevin Conner <kconner@redhat.com> - 0.4.0
- Updated to 0.4.0

* Wed Oct 17 2018 Kevin Conner <kconner@redhat.com> - 0.3.0
- Updated to 0.3.0

* Fri Oct 12 2018 Brian Avery <bavery@redhat.com> - 0.3.0
- Added 0.3.0

* Tue Sep 4 2018 Brian Avery <bavery@redhat.com> - 0.1.0
- Stripped binaries

* Tue Aug 14 2018 Brian Avery <bavery@redhat.com> - 0.1.0
- First package
