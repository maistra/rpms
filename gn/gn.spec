%global debug_package %{nil}

%global git_commit b175fa5d

Name:    gn
Version: 1772
Release: 1%{?dist}.%{git_commit}
Summary: A meta build system

License: BSD-3-Clause
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: ninja-build
BuildRequires: python3

Source0: https://gn.googlesource.com/gn/+archive/%{git_commit}.tar.gz

%description
GN is a meta-build system that generates build files for Ninja.

%prep
%setup -q -c -n gn

%build

export CC=gcc CXX=g++ CXXFLAGS="$CXXFLAGS -Wno-deprecated-copy"

python3 build/gen.py --no-last-commit-position --no-static-libstdc++

# last_commit_position.h generation wants Git, so write it manually.
cat > out/last_commit_position.h <<EOF
#ifndef OUT_LAST_COMMIT_POSITION_H_
#define OUT_LAST_COMMIT_POSITION_H_

#define LAST_COMMIT_POSITION_NUM %{version}
#define LAST_COMMIT_POSITION "%{version} (%{git_commit})"

#endif  // OUT_LAST_COMMIT_POSITION_H_
EOF

%ninja_build -C out

%install
install -Dm 755 out/gn %{buildroot}/%{_bindir}/gn

%files
%{_bindir}/gn
