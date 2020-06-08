%global debug_package %{nil}

Name:    libwee8
Version: 7.9.317.14
Release: 1%{?dist}
Summary: V8 JavaScript Engine - libwee8.a

License: BSD-3-Clause
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: ninja-build
BuildRequires: python3
BuildRequires: libatomic
BuildRequires: gn

# Taken from https://github.com/Maistra/envoy/blob/maistra-1.1/bazel/repository_locations.bzl#L270
Source0: https://storage.googleapis.com/envoyproxy-wee8/wee8-7.9.317.14.tar.gz
Patch0:  wee8.patch
Patch1:  no-fatal-warnings.patch

%description
V8 JavaScript Engine - Just libwee8.a and wasm.hh files

%prep
%setup -q -n wee8
%patch0 -p2
%patch1 -p1

%build

# BEGIN Python workarounds
mkdir -p "${HOME}/bin" && ln -sf /usr/bin/python3 "${HOME}/bin/python"
export PATH="${HOME}/bin:${PATH}"
# END Python workarounds

export CC=gcc CXX=g++ AR=ar NM=nm

# Release build.
WEE8_BUILD_ARGS+=" is_debug=false"
# Clang or not Clang, that is the question.
WEE8_BUILD_ARGS+=" is_clang=false"
# Hack to disable bleeding-edge compiler flags.
WEE8_BUILD_ARGS+=" use_xcode_clang=true"
# Use local toolchain.
WEE8_BUILD_ARGS+=" custom_toolchain=\"//build/toolchain/linux/unbundle:default\""
# Use local stdlibc++ / libc++.
WEE8_BUILD_ARGS+=" use_custom_libcxx=false"
# Use local sysroot.
WEE8_BUILD_ARGS+=" use_sysroot=false"
# Disable unused GLib2 dependency.
WEE8_BUILD_ARGS+=" use_glib=false"
# Expose debug symbols.
WEE8_BUILD_ARGS+=" v8_expose_symbols=true"
# Build monolithic library.
WEE8_BUILD_ARGS+=" is_component_build=false"
WEE8_BUILD_ARGS+=" v8_enable_i18n_support=false"
WEE8_BUILD_ARGS+=" v8_enable_gdbjit=false"
WEE8_BUILD_ARGS+=" v8_use_external_startup_data=false"
# Disable read-only heap, since it's leaky and HEAPCHECK complains about it.
# TODO(PiotrSikora): remove when fixed upstream.
WEE8_BUILD_ARGS+=" v8_enable_shared_ro_heap=false"

gn gen out/wee8 --args="$WEE8_BUILD_ARGS"
%ninja_build -C out/wee8 wee8

%install
install -Dm 644 out/wee8/obj/libwee8.a %{buildroot}/%{_libdir}/libwee8.a
install -Dm 644 third_party/wasm-api/wasm.hh %{buildroot}/%{_includedir}/wasm-api/wasm.hh

%files
%{_libdir}/libwee8.a
%{_includedir}/wasm-api/wasm.hh
