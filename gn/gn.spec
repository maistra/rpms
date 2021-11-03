# The git sha below is obtained by extracting the wee8 tarball used by envoy 1.8
# https://github.com/istio/envoy/blob/81b7bb3eb044842e6caaf02a46d01a50a83743f4/bazel/repository_locations.bzl#L696
# Then inspecting the `gn_version` variable in the DEPS file from the extracted tarball
%global git_commit e002e68a48d1c82648eadde2f6aafa20d08c36f2

# The version below is obtained by running `python3 build/gen.py` in the source dir
# and inspecting the file `out/last_commit_position.h`.
Name:    gn
Version: 1831
Release: 1%{?dist}
Summary: A meta build system

License: BSD-3-Clause
BuildRequires: clang
BuildRequires: ninja-build
BuildRequires: python3

Source0: https://gn.googlesource.com/gn/+archive/%{git_commit}.tar.gz

%description
GN is a meta-build system that generates build files for Ninja.

%prep
%setup -q -c

python3 build/gen.py --no-last-commit-position --no-static-libstdc++ --debug

# last_commit_position.h generation wants Git, so write it manually.
cat > out/last_commit_position.h <<EOF
#ifndef OUT_LAST_COMMIT_POSITION_H_
#define OUT_LAST_COMMIT_POSITION_H_

#define LAST_COMMIT_POSITION_NUM %{version}
#define LAST_COMMIT_POSITION "%{version} (%{git_commit})"

#endif  // OUT_LAST_COMMIT_POSITION_H_
EOF

%build

ninja -C out

%install
install -Dm 755 out/gn %{buildroot}/%{_bindir}/gn

%files
%{_bindir}/gn

%changelog
* Tue Nov 2 2021 Jonh Wendell <jwendell@redhat.com> - 1831-1
- Initial build for maistra 2.1.0
