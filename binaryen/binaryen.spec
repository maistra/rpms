Summary:       Compiler and toolchain infrastructure library for WebAssembly
Name:          binaryen
Version:       97.0.0
Release:       1%{?dist}

URL:           https://github.com/WebAssembly/binaryen
Source0        %{url}/archive/refs/tags/version_97.tar.gz
License:       ASL 2.0

# tests fail on big-endian
# https://github.com/WebAssembly/binaryen/issues/2983
ExcludeArch:   ppc64 s390x

BuildRequires: cmake
BuildRequires: python3
BuildRequires: python3-devel
BuildRequires: git
BuildRequires: gcc-c++

# filter out internal shared library
%global __provides_exclude_from ^%{_libdir}/%{name}/.*$
%global __requires_exclude ^libbinaryen\\.so.*$

%description
Binaryen is a compiler and toolchain infrastructure library for WebAssembly,
written in C++. It aims to make compiling to WebAssembly easy, fast, and
effective:

* Easy: Binaryen has a simple C API in a single header, and can also be used
  from JavaScript. It accepts input in WebAssembly-like form but also accepts
  a general control flow graph for compilers that prefer that.

* Fast: Binaryen's internal IR uses compact data structures and is designed for
  completely parallel codegen and optimization, using all available CPU cores.
  Binaryen's IR also compiles down to WebAssembly extremely easily and quickly
  because it is essentially a subset of WebAssembly.

* Effective: Binaryen's optimizer has many passes that can improve code very
  significantly (e.g. local coloring to coalesce local variables; dead code
  elimination; precomputing expressions when possible at compile time; etc.).
  These optimizations aim to make Binaryen powerful enough to be used as a
  compiler backend by itself. One specific area of focus is on
  WebAssembly-specific optimizations (that general-purpose compilers might not
  do), which you can think of as wasm minification , similar to minification for
  JavaScript, CSS, etc., all of which are language-specific (an example of such
  an optimization is block return value generation in SimplifyLocals).

%prep
%setup -q -n binaryen-version_97

%build
# BEGIN Python workarounds
rm -f "${HOME}/bin/python"
mkdir -p "${HOME}/bin" && ln -s /usr/bin/python3 "${HOME}/bin/python"
export PATH="${HOME}/bin:${PATH}"
# END Python workarounds

%cmake . \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DPYTHON_EXECUTABLE=%{__python3} \
    -DCMAKE_INSTALL_LIBDIR=%{_libdir}/%{name} \
    -DCMAKE_INSTALL_RPATH=\\\$ORIGIN/../%{_lib}/%{name} \
    -DENABLE_WERROR=OFF \

%make_build

%install
%make_install

%files
%license LICENSE
%doc README.md
%{_bindir}/wasm-as
%{_bindir}/wasm-ctor-eval
%{_bindir}/wasm-dis
%{_bindir}/wasm-emscripten-finalize
%{_bindir}/wasm-metadce
%{_bindir}/wasm-opt
%{_bindir}/wasm-reduce
%{_bindir}/wasm-shell
%{_bindir}/wasm2js
%{_includedir}/binaryen-c.h
%{_libdir}/%{name}/libbinaryen.so

%changelog
* Tue Nov 2 2021 Jonh Wendell <jwendell@redhat.com> 97.0.0-1
- Initial build for maistra 2.1.0
