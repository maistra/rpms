Name:           istio-prometheus-promu
Version:        0.7.0
Release:        0%{?dist}
Summary:        Prometheus Utility Tool
License:        ASL 2.0
URL:            https://github.com/prometheus/promu

Source0:        https://github.com/prometheus/promu/archive/v%{version}.tar.gz

ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 s390x ppc64le aarch64 %{arm}}
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  golang >= 1.12

%description
Promu is part of Prometheus component Builds toolchain.

%package istio-prometheus-promu
Summary:  Prometheus Utility Tool

%description istio-prometheus-promu
Package containing prometheus utility tool files.

%prep

rm -rf PROMU
mkdir -p PROMU/src/github.com/prometheus/promu
tar zxf %{SOURCE0} -C PROMU/src/github.com/prometheus/promu --strip=1

%build
cd PROMU

cd src/github.com/prometheus/promu
go build -mod=vendor

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_bindir}

cd PROMU/src/github.com/prometheus/promu

mkdir stripped
strip -o stripped/promu -s promu
cp -pav stripped/promu "${RPM_BUILD_ROOT}%{_bindir}/"

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files
%license PROMU/src/github.com/prometheus/promu/LICENSE
%doc     PROMU/src/github.com/prometheus/promu/README.md
%doc     PROMU/src/github.com/prometheus/promu/.promu.yml
%{_bindir}/promu

%changelog
* Wed Nov 3 2021 Jonh Wendell <jwendell@redhat.com> - 0.7.0-0
- Initial build for maistra 2.1.0
