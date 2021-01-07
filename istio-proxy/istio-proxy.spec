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

%global git_commit a405165e3e09e57217b53846454db913cd493d10
%global shortcommit  %(c=%{git_commit}; echo ${c:0:7})
%global gn_commit 743970903a39f4122a6476f9e05f59b9af03fdf6
%global gn_hash 259564bf3c706413a7cdadf4c8cd6a49

# https://github.com/maistra/proxy
%global provider        github
%global provider_tld    com
%global project         maistra
%global repo            proxy
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}

# Use /usr/local as base dir, once upstream heavily depends on that
%global _prefix /usr/local

Name:           istio-proxy
Version:        1.1.11
Release:        1%{?dist}
Summary:        Istio Proxy
License:        ASL 2.0
URL:            https://github.com/Maistra/proxy

BuildRequires:  bazel = 1.1.0
BuildRequires:  ninja-build
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  patch
BuildRequires:  xz
BuildRequires:  git
BuildRequires:  golang
BuildRequires:  automake
BuildRequires:  python3
BuildRequires:  cmake3
BuildRequires:  openssl
BuildRequires:  openssl-devel
BuildRequires:  libatomic
BuildRequires:  platform-python-devel

Source0:        proxy-%{git_commit}.tar.gz
Source10:       gn-%{gn_hash}.tar.gz
Patch0:         0001-Preserve-LWS-from-the-middle-of-HTTP1-header-values.patch
Patch10:        0002-http-header-map-security-fixes-for-duplicate-headers.patch
Patch1000:      1000-disable-sni-too-large-test.patch

ExclusiveArch:  x86_64

%description
The Istio Proxy is a microservice proxy that can be used on the client and server side, and forms a microservice mesh. The Proxy supports a large number of features.

%prep
%setup -q -n proxy-%{git_commit}
%setup -q -D -T -n proxy-%{git_commit} -a 10
pushd maistra/vendor/envoy
%patch0 -p1
%patch10 -p1
popd
%patch1000 -p1

%build
# BEGIN GN FIXME: Move GN to its own package?
pushd gn
export CXX=%{__cxx}
python3 build/gen.py --no-static-libstdc++ --no-last-commit-position
ninja -C out
cp -f out/gn ../maistra/vendor/com_googlesource_chromium_v8/wee8/buildtools/linux64/gn
popd
# END GN

# BEGIN Python workarounds
mkdir -p "${HOME}/bin" && ln -s /usr/bin/python3 "${HOME}/bin/python"
export PATH="${HOME}/bin:${PATH}"
pathfix.py -pn -i %{__python3} maistra/vendor >/dev/null 2>&1
# END Python workarounds

# Fix path to the vendor deps
sed -i "s|=/work/|=$(pwd)/|" maistra/bazelrc-vendor

# MultiArch
ARCH=$(uname -p)
if [ "${ARCH}" = "ppc64le" ]; then
  ARCH="ppc"
fi

export BUILD_SCM_REVISION="%{git_commit}" BUILD_SCM_STATUS="Maistra %{version}-%{release}"

bazel build \
  --config=release \
  --config=${ARCH} \
  --local_resources 12288,6.0,1.0 \
  --jobs=6 \
  --host_javabase=@local_jdk//:jdk \
  //src/envoy:envoy

cp bazel-bin/src/envoy/envoy ${RPM_BUILD_DIR}

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_bindir}

#strip binaries of unnecessary data
binaries=(envoy)
pushd ${RPM_BUILD_DIR}

%if 0%{?with_debug}
    for i in "${binaries[@]}"; do
        cp -pav $i $RPM_BUILD_ROOT%{_bindir}/
    done
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

%if 0%{?with_tests}
%check
# MultiArch
ARCH=$(uname -p)
if [ "${ARCH}" = "ppc64le" ]; then
  ARCH="ppc"
fi

export BUILD_SCM_REVISION="%{git_commit}" BUILD_SCM_STATUS="Maistra %{version}-%{release}"
export PATH="${HOME}/bin:${PATH}"

bazel test \
  --config=release \
  --config=${ARCH} \
  --local_resources 12288,6.0,1.0 \
  --jobs=6 \
  //src/...

%endif

%files
/usr/local/bin/envoy

%changelog
* Tue Jan 5 2021 Kevin Conner <kconner@redhat.com> - 1.1.11-1
- Release of 1.1.11-1

* Thu Oct 29 2020 Kevin Conner <kconner@redhat.com> - 1.1.10-1
- Release of 1.1.10-1

* Tue Sep 11 2020 Brian Avery <bavery@redhat.com> - 1.1.8-1
- Release of 1.1.8-1

* Tue Jul 21 2020 Kevin Conner <kconner@redhat.com> - 1.1.5-1
- Release of 1.1.5-1

* Sun Jun 21 2020 Kevin Conner <kconner@redhat.com> - 1.1.3-2
- Release of 1.1.3-2

* Thu May 21 2020 Jonh Wendell <jwendell@redhat.com> - 1.1.3-1
- Simplify build system

* Mon May 11 2020 Product Release - 1.1.2-2
- Update to latest release

* Mon May 11 2020 Product Release - 1.1.1-1
- Update to latest release

* Wed Apr 22 2020 Product Release - 1.1.1-2
- Update to latest release

* Wed Apr 01 2020 Product Release - 1.1.0-4
- Update to latest release

* Tue Mar 31 2020 Product Release - 1.1.0-3
- Update to latest release

* Mon Mar 16 2020 Brian Avery <bavery@redhat.com> - 1.1.0-2
- Update to Istio 1.4.6 proxy
* Fri Feb 14 2020 Brian Avery <bavery@redhat.com> - 1.1.0-1
- Updated to Istio 1.4 proxy
- Added support for building based on SHA
- Simplified repositories

