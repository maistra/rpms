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

%global proxy_git_commit 5a49500b42f0ab296c1f0b030caf0aba625fa8be
%global proxy_shortcommit  %(c=%{proxy_git_commit}; echo ${c:0:7})

%global proxy_openssl_git_commit 10ba1241fbc9e90e3950eb45cd47c33a957cf70a
%global proxy_openssl_shortcommit  %(c=%{proxy_openssl_git_commit}; echo ${c:0:7})

%global envoy_openssl_git_commit aa6d2ff49b6c42fb6e4144866304c9024e53102a
%global envoy_openssl_shortcommit  %(c=%{envoy_openssl_git_commit}; echo ${c:0:7})

%global jwt_openssl_git_commit 21528f22d56cc20181ddb40ab27be286141ff583
%global jwt_openssl_shortcommit  %(c=%{jwt_openssl_git_commit}; echo ${c:0:7})

# https://github.com/maistra/proxy
%global provider        github
%global provider_tld    com
%global project         maistra
%global repo            proxy
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}

%global checksum 0c48e37fffa163b2cf3b8caf1b79424f

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

Source0:        istio-proxy.%{checksum}.tar.xz
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
* Mon Jan 13 2020 Kevin Conner <kconner@redhat.com> - 1.0.4-1
- Bump version to 1.0.4

* Thu Oct 17 2019 Jonh Wendell <jonh.wendell@redhat.com> - 1.0.2-1
- Updated to Maistra 1.0.2, Istio-Proxy 1.1.17

* Thu Jul 18 2019 William DeCoste <wdecoste@redhat.com>
  Release 1.0.0-0
* Mon Jul 15 2019 Brian Avery <bavery@redhat.com>
- Update to Maistra 0.12 release
* Thu Jun 20 2019 William DeCoste <wdecoste@redhat.com>
  Release 0.12.0-1
* Tue Jun 11 2019 William DeCoste <wdecoste@redhat.com>
  Release 0.12.0-0
* Tue May 14 2019 William DeCoste <wdecoste@redhat.com>
  Release 0.11.0-0
* Thu Mar 07 2019 Dmitri Dolguikh <ddolguik@redhat.com>
  Release 0.9.0-2
* Mon Mar 04 2019 Dmitri Dolguikh <ddolguik@redhat.com>
  Release 0.9.0-1
* Thu Feb 14 2019 Kevin Conner <kconner@redhat.com>
  Release 0.8.0-1
* Sun Jan 20 2019 Kevin Conner <kconner@redhat.com>
  Release 0.7.0-1
* Thu Dec 20 2018 Kevin Conner <kconner@redhat.com>
  Release 0.6.0-1
* Wed Nov 21 2018 Dmitri Dolguikh <ddolguik@redhat.com>
  Release 0.5.0-1
* Mon Oct 29 2018 Dmitri Dolguikh <ddolguik@redhat.com>
  Release 0.4.0-1
* Fri Oct 12 2018 Dmitri Dolguikh <ddolguik@redhat.com>
  Release 0.3.0-1
* Wed Sep 12 2018 Dmitri Dolguikh <ddolguik@redhat.com>
  Release 0.2.0-1
* Tue Jul 31 2018 Dmitri Dolguikh <ddolguik@redhat.com>
- Release 0.1.0-1
* Mon Mar 5 2018 Bill DeCoste <wdecoste@redhat.com>
- First package
