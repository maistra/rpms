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

%global git_commit 29093158179dc65392f41e664617e3574e56f124
%global shortcommit  %(c=%{git_commit}; echo ${c:0:7})

# https://github.com/maistra/proxy
%global provider        github
%global provider_tld    com
%global project         maistra
%global repo            proxy
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}

# Use /usr/local as base dir, once upstream heavily depends on that
%global _prefix /usr/local

Name:           istio-proxy
Version:        2.0.0
Release:        1%{?dist}
Summary:        Istio Proxy
License:        ASL 2.0
URL:            https://github.com/Maistra/proxy

BuildRequires:  bazel = 2.2.0
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

%description
The Istio Proxy is a microservice proxy that can be used on the client and server side, and forms a microservice mesh. The Proxy supports a large number of features.

%prep
%setup -q -n proxy-%{git_commit}

%build

# BEGIN Python workarounds
mkdir -p "${HOME}/bin" && ln -s /usr/bin/python3 "${HOME}/bin/python"
export PATH="${HOME}/bin:${PATH}"
pathfix.py -pn -i %{__python3} maistra/vendor >/dev/null 2>&1
# END Python workarounds

# Fix path to the vendor deps
sed -i "s|=/work/|=$(pwd)/|" maistra/bazelrc-vendor

export BUILD_SCM_REVISION="%{git_commit}" BUILD_SCM_STATUS="Maistra %{version}-%{release}"

bazel build \
  --config=release \
  --config=${ARCH} \
  --local_resources 12288,6.0,1.0 \
  --jobs=6 \
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
* Fri Oct 30 2020 Brian Avery <bavery@redhat.com> - 2.0.0-1
- Bump to 2.0
* Wed Jun 10 2020 Jonh Wendell <jwendell@redhat.com> - 1.2.0-1
- Simplify build system
- Bump to 1.2
