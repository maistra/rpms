%undefine _missing_build_ids_terminate_build

%global git_commit ad791dc47db0851859fedfa219ccbb0a99995417
%global git_shortcommit  %(c=%{git_commit}; echo ${c:0:7})

%global provider        github
%global provider_tld    com
%global project         maistra
%global repo            ior
# https://github.com/maistra/ior
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}

Name:           ior
Version:        0.8.0
Release:        1%{?dist}
Summary:        Istio + OpenShift Routing
License:        ASL 2.0
URL:            https://%{provider_prefix}

Source0:        https://%{provider_prefix}/archive/%{git_commit}/%{repo}-%{git_commit}.tar.gz

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 aarch64 %{arm}}
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  golang >= 1.9

%description
ior integrates Istio Gateways with OpenShift Routes

%prep
rm -rf IOR
mkdir -p IOR/src/%{provider_prefix}
tar zxf %{SOURCE0} -C IOR/src/%{provider_prefix} --strip=1

%build
cd IOR
export GOPATH=$(pwd):%{gopath}

pushd src/%{provider_prefix}
make

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/%{_bindir}
cd IOR/src/%{provider_prefix}

install -p -m 755 cmd/ior %{buildroot}/%{_bindir}

%files
%license IOR/src/%{provider_prefix}/LICENSE
%doc     IOR/src/%{provider_prefix}/README.md

%{_bindir}/ior

%changelog
* Thu Feb 14 2019 Kevin Conner <kconner@redhat.com> - 0.8.0
- First package
* Mon Jan 14 2019 Jonh Wendell <jonh.wendell@redhat.com> - 0.6.0
- First package
