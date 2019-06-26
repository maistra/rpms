Name:           prometheus-promu
Version:        0.2.0
Release:        1%{?dist}
Summary:        Prometheus Utility Tool 
License:        ASL 2.0
URL:            https://github.com/prometheus/promu

Source0:        https://github.com/prometheus/promu/archive/v%{version}.tar.gz

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 aarch64 %{arm}}
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  golang >= 1.6

%description
Promu is part of Prometheus component Builds toolchain.

%package prometheus-promu
Summary:  Prometheus Utility Tool

%description prometheus-promu
Package containing prometheus utility tool files.

%prep

rm -rf PROMU
mkdir -p PROMU/src/github.com/prometheus/promu
tar zxf %{SOURCE0} -C PROMU/src/github.com/prometheus/promu --strip=1

%build
cd PROMU
export GOPATH=$(pwd):%{gopath}

cd src/github.com/prometheus/promu
go build

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
* Wed Jun 20 2019 Dmitri Dolguikh <ddolguik@redhat.com> - 0.2.0-1
- First build
