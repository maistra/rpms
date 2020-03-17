# Generate devel rpm
%global with_devel 0
# Build with debug info rpm
%global with_debug 0
# Run unit tests
%global with_tests 1
# Build test binaries
%global with_test_binaries 0

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%global proxy_git_commit e885dd6880407edd27c81f8f42c5480a6d80751d
%global proxy_shortcommit  %(c=%{proxy_git_commit}; echo ${c:0:7})

# https://github.com/maistra/proxy
%global provider        github
%global provider_tld    com
%global project         maistra
%global repo            proxy
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}

%global checksum 5227f2f61c535d2a739a307f2102279b

%global _prefix /usr/local

Name:           istio-proxy
Version:        1.1.0
Release:        1%{?dist}
Summary:        The Istio Proxy is a microservice proxy that can be used on the client and server side, and forms a microservice mesh. The Proxy supports a large number of features.
License:        ASL 2.0
URL:            https://github.com/Maistra/proxy

BuildRequires:  bazel = 1.1.0
BuildRequires:  ninja-build
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  patch
BuildRequires:  ksh
BuildRequires:  xz
BuildRequires:  golang
BuildRequires:  automake
BuildRequires:  python3
BuildRequires:  cmake3
BuildRequires:  openssl
BuildRequires:  openssl-devel
BuildRequires:  libatomic

Source0:        istio-proxy.%{checksum}.tar.gz
Source1:        build.sh
Source2:        test.sh
Source3:        fetch.sh
Source4:        common.sh

%description
The Istio Proxy is a microservice proxy that can be used on the client and server side, and forms a microservice mesh. The Proxy supports a large number of features.

########### istio-proxy ###############
%package istio-proxy
Summary:  The istio envoy proxy

%description istio-proxy
The Istio Proxy is a microservice proxy that can be used on the client and server side, and forms a microservice mesh. The Proxy supports a large number of features.

This package contains the envoy program.

istio-proxy is the proxy required by the Istio Pilot Agent that talks to Istio pilot

%prep
%setup -q -n %{name}

%build

cd ..
#execute build.sh
FETCH_DIR= CREATE_ARTIFACTS= STRIP=false %{SOURCE1}

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_bindir}

#strip binaries of unnecessary data
binaries=(envoy)
pushd ${RPM_BUILD_DIR}
%if 0%{?with_debug}
    for i in "${binaries[@]}"; do
        cp -pav $i $RPM_BUILD_ROOT%{_bindir}/
%else
    mkdir stripped
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
        echo "remove unnecessary debug info from ${i}"
        objcopy -S --remove-section .gdb_index --remove-section .comment \
  --keep-symbols=keep_symbols "${i}" "${COMPRESSED_NAME}"

        echo "stripping: ${i}"
        strip -o "stripped/${i}" -s $i

        echo "compress debugdata for ${i} into ${COMPRESSED_NAME}.xz"
        xz "${COMPRESSED_NAME}"

        echo "inject compressed data into .gnu_debugdata for ${i}"
        objcopy --add-section ".gnu_debugdata=${COMPRESSED_NAME}.xz" "stripped/${i}"

        cp -pav "stripped/${i}" "${RPM_BUILD_ROOT}%{_bindir}/"
    done
%endif
popd

%check
cd ..
TEST_ENVOY=false RUN_TESTS=true %{SOURCE2}

%files
/usr/local/bin/envoy

%changelog
* Tue Feb 11 2020 Brian Avery <bavery@redhat.com> - 1.1.0-1
- Updated to Istio 1.4 proxy
- Added support for building based on SHA
- Simplified repositories