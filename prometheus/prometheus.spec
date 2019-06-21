# Build with debug info rpm
%global with_debug 0

%if 0%{?with_debug} > 0
%global _dwz_low_mem_die_limit 0
%else
%global debug_package %{nil}
%endif

%global git_commit 625dc242457d7099b2f6e83267822b59f1c4251c
%global git_shortcommit  %(c=%{git_commit}; echo ${c:0:7})

Name:           prometheus
Version:        2.7.2
Release:        1%{?dist}
Summary:        An open-source systems monitoring and alerting toolkit 
License:        ASL 2.0
URL:            https://prometheus.io/

BuildRequires:  prometheus-promu = 0.2.0
BuildRequires:  golang >= 1.11

Source0:        https://github.com/openshift/prometheus/archive/%{git_commit}.tar.gz

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 aarch64 %{arm}}

%description
Prometheus is an open-source systems monitoring and alerting toolkit.

%package prometheus
Summary:  A monitoring and alerting toolkit

%description prometheus
Package containing prometheus files.

%prep

rm -rf PROMETHEUS
mkdir -p PROMETHEUS/src/github.com/prometheus/prometheus
tar zxf %{SOURCE0} -C PROMETHEUS/src/github.com/prometheus/prometheus --strip=1

%build
cd PROMETHEUS
export GOPATH=$(pwd):%{gopath}
cd src/github.com/prometheus/prometheus

PROMU=$(which promu) make -e build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{name}/console_libraries/
mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{name}/consoles/
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/

binaries=(prometheus promtool)
cd PROMETHEUS/src/github.com/prometheus/prometheus
%if 0%{?with_debug} > 0
  for i in "${binaries[@]}"; do
        cp -pav $i $RPM_BUILD_ROOT%{_bindir}/
   done
%else
    mkdir stripped
    touch keep_symbols
    for i in "${binaries[@]}"; do
       echo "Dumping dynamic symbols for ${i}"
        nm -D $i --format=posix --defined-only \
  | awk '{ print $1 }' | sort > dynsyms

        echo "Dumping function symbols for ${i}"
       nm $i --format=posix --defined-only \
  | awk '{ if ($2 == "T" || $2 == "t" || $2 == "D") print $1 }' \
  | sort > funcsyms

        echo "Grabbing other function symbols from ${i}"
        comm -13 dynsyms funcsyms > keep_symbols

        COMPRESSED_NAME="${i}_debuginfo"
        if [ -s keep_symbols ]; then
          echo "remove unnecessary debug info from ${i}"
          objcopy -S --remove-section .gdb_index --remove-section .comment \
  --keep-symbols=keep_symbols "${i}" "${COMPRESSED_NAME}"
        fi

        echo "stripping: ${i}"
        strip -o "stripped/${i}" -s $i

        if [ -f ${COMPRESSED_NAME} ]; then
          echo "compress debugdata for ${i} into ${COMPRESSED_NAME}.xz"
          xz "${COMPRESSED_NAME}"

          echo "inject compressed data into .gnu_debugdata for ${i}"
          objcopy --add-section ".gnu_debugdata=${COMPRESSED_NAME}.xz" "stripped/${i}"
        fi

        cp -pav "stripped/${i}" "${RPM_BUILD_ROOT}%{_bindir}/"
    done
%endif

cp -a console_libraries/ $RPM_BUILD_ROOT%{_datadir}/%{name}
ln -sf %{_datadir}/%{name}/console_libraries/ $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/
cp -a consoles/ $RPM_BUILD_ROOT%{_datadir}/%{name}/
ln -sf %{_datadir}/%{name}/consoles/ $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/
cp -a documentation/examples/prometheus.yml $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/%{name}.yml

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files
%license PROMETHEUS/src/github.com/prometheus/prometheus/LICENSE
%doc     PROMETHEUS/src/github.com/prometheus/prometheus/README.md
%{_bindir}/prometheus
%{_bindir}/promtool
%{_datadir}/%{name}/console_libraries/
%{_sysconfdir}/%{name}/console_libraries
%{_datadir}/%{name}/consoles/
%{_sysconfdir}/%{name}/consoles
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.yml

%changelog
* Wed Jun 19 2019 Dmitri Dolguikh <ddolguik@redhat.com> - 2.7.2-1
- First build
