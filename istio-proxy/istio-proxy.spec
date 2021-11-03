%global wasmbuildarches x86_64

# Run unit tests
%global with_tests 0

%global git_commit 8cf470a4cab1c10163e2e6f40951108e179afd85
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
Version:        2.1.0
Release:        0%{?dist}
Summary:        Istio Proxy
License:        ASL 2.0
URL:            https://github.com/Maistra/proxy

BuildRequires:  bazel = 3.7.2
BuildRequires:  gn
BuildRequires:  ninja-build
BuildRequires:  gcc-toolset-9
BuildRequires:  gcc-toolset-9-libatomic-devel
BuildRequires:  git
BuildRequires:  make
BuildRequires:  patch
BuildRequires:  xz
BuildRequires:  golang
BuildRequires:  automake
BuildRequires:  python3
BuildRequires:  cmake
BuildRequires:  openssl
BuildRequires:  openssl-devel
BuildRequires:  platform-python-devel
%ifarch %{wasmbuildarches}
BuildRequires:  llvm-devel
BuildRequires:  binaryen
BuildRequires:  clang
BuildRequires:  lld
BuildRequires:  nodejs
%endif

Requires: istio-proxy-wasm

Source0:        proxy-%{git_commit}.tar.gz
Patch1:         0001-modify-envoy-paths.patch
Patch2:         0002-modify-proxy-paths.patch 

%description
The Istio Proxy is a microservice proxy that can be used on the client and server side, and forms a microservice mesh. The Proxy supports a large number of features.

%package wasm
Summary:        WASM extensions for Istio Proxy
BuildArch: noarch

%description wasm
Web Assembly (WASM) extensions for Istio Proxy.

%prep
rm -rf %{name}-%{version} && mkdir -p %{name}-%{version}
tar zxf %{SOURCE0} -C %{name}-%{version} --strip=1

%setup -D -T
pushd maistra/vendor/envoy

%patch1 -p1
rm -rf envoy
mv include/envoy ./
find ./envoy ./test ./source ./tools -name BUILD -print0 | xargs -0 sed -i 's/"\/\/include\//"\/\//g'
find ./source -name BUILD -print0 | xargs -0 sed -i 's/"@envoy\/\/include\//"@envoy\/\//g'
for dir in common docs exe extensions server; do
  find ./envoy ./source ./test ./tools \( -name \*.h -o -name \*.cc -o -name \*.j2 \) -print0 | xargs -0 sed -i "/Common.pb.h/!s/#include \"$dir\//#include \"source\/$dir\//g"
done

popd

%patch2 -p1
find ./src ./extensions ./test -name BUILD -print0 | xargs -0 sed -i 's/"@envoy\/\/include\//"@envoy\/\//g'
for dir in common docs exe server; do
  find ./src ./test ./extensions \( -name \*.h -o -name \*.cc \) -print0 | xargs -0 sed -i "s/#include \"$dir\//#include \"source\/$dir\//g"
done


%build
source /opt/rh/gcc-toolset-9/enable

cp -f /usr/bin/gn maistra/vendor/com_googlesource_chromium_v8/wee8/buildtools/linux64/gn

# BEGIN Python workarounds
mkdir -p "${HOME}/bin" && ln -sf /usr/bin/python3 "${HOME}/bin/python"
export PATH="${HOME}/bin:${PATH}"
pathfix.py -pn -i %{__python3} maistra/vendor >/dev/null 2>&1
# END Python workarounds

# Fix path to the vendor deps
sed -i "s|=/work/|=$(pwd)/|" maistra/bazelrc-vendor
sed -i "s|/work/|$(pwd)/|" maistra/vendor/proxy_wasm_cpp_sdk/toolchain/cc_toolchain_config.bzl

# MultiArch
ARCH=$(uname -p)
if [ "${ARCH}" = "ppc64le" ]; then
  ARCH="ppc"
fi

# TODO: Fix this in maistra/proxy update vendor script
find maistra/vendor \( -name '*.h' -o -name '*.cpp' -o -name '*.cc' \) -executable -exec chmod -x '{}' \;

export BUILD_SCM_REVISION="%{git_commit}" BUILD_SCM_STATUS="MAISTRA %{version}-%{release}"
export BAZEL_OUTPUT=$(pwd)/BAZEL_OUTPUT
mkdir -p ${BAZEL_OUTPUT}

export DEBUG_PREFIX=$(pwd)/bazel-istio-proxy-%{version}

COMMON_FLAGS="\
  --incompatible_linkopts_to_linklibs \
  --config=release-symbol \
  --config=${ARCH} \
  --local_ram_resources=12288 \
  --local_cpu_resources=6 \
  --jobs=3 \
  --force_pic=true \
  --host_javabase=@local_jdk//:jdk \
  --copt -fdebug-prefix-map=.=${DEBUG_PREFIX} \
  --copt -fdebug-prefix-map=/proc/self/cwd=${DEBUG_PREFIX} \
"

function bazel_build() {
  bazel --output_base=${BAZEL_OUTPUT} build \
    ${COMMON_FLAGS} \
    "${@}"
}

# Build WASM
%ifarch %{wasmbuildarches}
CC=clang CXX=clang++ bazel_build //extensions:stats.wasm
CC=clang CXX=clang++ bazel_build //extensions:metadata_exchange.wasm
CC=clang CXX=clang++ bazel_build //extensions:attributegen.wasm
CC=cc CXX=g++ bazel_build @envoy//test/tools/wee8_compile:wee8_compile_tool

CC=clang CXX=clang++ bazel-bin/external/envoy/test/tools/wee8_compile/wee8_compile_tool bazel-bin/extensions/stats.wasm bazel-bin/extensions/stats.compiled.wasm
CC=clang CXX=clang++ bazel-bin/external/envoy/test/tools/wee8_compile/wee8_compile_tool bazel-bin/extensions/metadata_exchange.wasm bazel-bin/extensions/metadata_exchange.compiled.wasm
CC=clang CXX=clang++ bazel-bin/external/envoy/test/tools/wee8_compile/wee8_compile_tool bazel-bin/extensions/attributegen.wasm bazel-bin/extensions/attributegen.compiled.wasm

echo "WASM extensions built succesfully. Now building envoy binary."
%endif

# Build Envoy
CC=cc CXX=g++ bazel_build //src/envoy:envoy

echo "Build succeeded. Binary generated:"
bazel-bin/src/envoy/envoy --version

%if 0%{?with_tests}
# Run tests here instead of in a "check" section to avoid rebuilding everything

CC=cc CXX=g++ bazel --output_base=${BAZEL_OUTPUT} test \
  ${COMMON_FLAGS} \
  --build_tests_only \
  --test_env=ENVOY_IP_TEST_VERSIONS=v4only \
  //src/... //test/...

# Go tests
export GOPROXY=off
export ENVOY_PATH=bazel-bin/src/envoy/envoy
export GO111MODULE=on

go test ./test/...

%ifarch %{wasmbuildarches}
WASM=true go test ./test/envoye2e/stats_plugin/...
%endif

%endif

chmod -R ug+w ${BAZEL_OUTPUT}

%install
rm -rf ${RPM_BUILD_ROOT}

mkdir -p ${RPM_BUILD_ROOT}%{_bindir}
cp bazel-bin/src/envoy/envoy ${RPM_BUILD_ROOT}%{_bindir}/

%ifarch %{wasmbuildarches}
EXTENSIONS_DIR=${RPM_BUILD_ROOT}/etc/istio/extensions
mkdir -p ${EXTENSIONS_DIR}
cp bazel-bin/extensions/stats.wasm ${EXTENSIONS_DIR}/stats-filter.wasm
cp bazel-bin/extensions/stats.compiled.wasm ${EXTENSIONS_DIR}/stats-filter.compiled.wasm
cp bazel-bin/extensions/metadata_exchange.wasm ${EXTENSIONS_DIR}/metadata-exchange-filter.wasm
cp bazel-bin/extensions/metadata_exchange.compiled.wasm ${EXTENSIONS_DIR}/metadata-exchange-filter.compiled.wasm
cp bazel-bin/extensions/attributegen.wasm ${EXTENSIONS_DIR}/attributegen.wasm
cp bazel-bin/extensions/attributegen.compiled.wasm ${EXTENSIONS_DIR}/attributegen.compiled.wasm
%endif

%files
%attr(755, -, -) %{_bindir}/envoy

%ifarch %{wasmbuildarches}
%files wasm
/etc/istio/extensions/
%endif

%changelog
* Tue Nov 2 2021 Jonh Wendell <jwendell@redhat.com> 2.1.0-0
- Initial build for maistra 2.1.0
