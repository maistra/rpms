Name:           bazel
Version:        2.2.0
Release:        1%{?dist}
Summary:        Correct, reproducible, and fast builds for everyone.
License:        Apache License 2.0
URL:            https://www.bazel.build/
Source0:        https://github.com/bazelbuild/bazel/releases/download/%{version}/bazel-%{version}-dist.zip


BuildRequires:  unzip 
BuildRequires:  java-11-openjdk-devel
BuildRequires:  zlib-devel
BuildRequires:  pkgconfig(bash-completion)
BuildRequires:  python3
BuildRequires:  gcc-c++
Requires:       java-11-openjdk-devel

%define debug_package %{nil}
%define __os_install_post %{nil}

%description
Correct, reproducible, and fast builds for everyone.

%prep
%setup -q -c -n %{name}-%{version}-dist

%build
# BEGIN Python workarounds
mkdir -p "${HOME}/bin" && ln -s /usr/bin/python3 "${HOME}/bin/python"
export PATH="${HOME}/bin:${PATH}"
# END Python workarounds

export CC=gcc CXX=g++
export EXTRA_BAZEL_ARGS="--host_javabase=@local_jdk//:jdk --host_force_python=PY3"

./compile.sh
./output/bazel shutdown

%install
mkdir -p %{buildroot}/%{_bindir}
cp output/bazel %{buildroot}/%{_bindir}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%attr(0755,root,root) %{_bindir}/bazel


%changelog
* Wed Jun 10 2020 Jonh Wendell <jwendell@redhat.com> - 2.2.0-1
- Bump to 2.2.0
