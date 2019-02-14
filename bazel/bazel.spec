# they warn against doing this ... :-\
%define _disable_source_fetch 0
# make sure that internet access is enabled during the build

Name:           bazel
Version:        0.22.0
Release:        1%{?dist}
Summary:        Correct, reproducible, and fast builds for everyone.
License:        Apache License 2.0
URL:            http://bazel.io/
Source0:        https://github.com/bazelbuild/bazel/releases/download/%{version}/bazel-%{version}-dist.zip

ExclusiveArch:  x86_64

BuildRequires:  unzip 
BuildRequires:  java-1.8.0-openjdk-devel
BuildRequires:  zlib-devel
BuildRequires:  pkgconfig(bash-completion)
BuildRequires:  python
BuildRequires:  gcc-c++
Requires:       java-1.8.0-openjdk-devel

%define debug_package %{nil}
%define __os_install_post %{nil}

%description
Correct, reproducible, and fast builds for everyone.

%prep
%setup -q -c -n %{name}-%{version}-dist

%build

which g++
g++ --version

CC=gcc
CXX=g++
env EXTRA_BAZEL_ARGS="--host_javabase=@local_jdk//:jdk" ./compile.sh
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
* Wed Feb 13 2019 Kevin Conner <kconner@redhat.com> 0.22.0-1
- Release 0.20.1-1
* Tue Jan 15 2019 Kevin Conner <kconner@redhat.com> 0.20.0-1
- Release 0.20.1-1
* Wed Aug 1  2018 Dmitri Dolguikh <ddolguik@redhat.com> 0.15.2-1
- Release 0.15.2-1
* Wed Mar 14 2018 William DeCoste <wdecoste@redhat.com> 0.11.1-1
- Initial from vbatts copr

