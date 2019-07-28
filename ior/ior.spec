%undefine _missing_build_ids_terminate_build

%global git_commit 6fa7084f530548d835688b3bf6b328b0d1869939
%global git_shortcommit  %(c=%{git_commit}; echo ${c:0:7})

%global provider        github
%global provider_tld    com
%global project         maistra
%global repo            ior
%global with_debug 0

# https://github.com/maistra/ior
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}

Name:           ior
Version:        1.0.0
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
make VERSION=%{version} GITREVISION=%{git_shortcommit} GITSTATUS=Clean GITTAG=%{version}-%{release}

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/%{_bindir}
cd IOR/src/%{provider_prefix}

%if 0%{?with_debug}
	install -p -m 755 cmd/ior %{buildroot}/%{_bindir}
%else
	echo "Dumping dynamic symbols"
	nm -D cmd/ior --format=posix --defined-only \
	| awk '{ print $1 }' | sort > dynsyms

	echo "Dumping function symbols"
	nm cmd/ior --format=posix --defined-only \
	| awk '{ if ($2 == "T" || $2 == "t" || $2 == "D") print $1 }' \
	| sort > funcsyms

	echo "Grabbing other function symbols"
	comm -13 dynsyms funcsyms > keep_symbols

	echo "Removing unnecessary debug info"
	COMPRESSED_NAME=ior_debuginfo

	objcopy -S --remove-section .gdb_index --remove-section .comment \
	--keep-symbols=keep_symbols cmd/ior  $COMPRESSED_NAME

	echo "Stripping binary"
	mkdir stripped
	strip -o stripped/ior -s cmd/ior

	echo "Compressing debugdata"
	xz $COMPRESSED_NAME

	echo "Injecting compressed data into .gnu_debugdata"
	objcopy --add-section .gnu_debugdata=$COMPRESSED_NAME.xz stripped/ior

	cp -pav stripped/ior %{buildroot}/%{_bindir}
%endif

%files
%license IOR/src/%{provider_prefix}/LICENSE
%doc     IOR/src/%{provider_prefix}/README.md

%{_bindir}/ior

%changelog
* Wed Jun 12 2019 Brian Avery <bavery@redhat.com> - 0.12.0
- Update to Maistra 0.12

* Fri May 17 2019 Jonh Wendell <jonh.wendell@redhat.com> - 0.11.0
- Update to include version info at build time
* Mon May 13 2019 Brian Avery <bavery@redhat.com> - 0.11.0
- Maistra 0.11 release
* Fri Mar 22 2019 Brian Avery <bavery@redhat.com> - 0.10.0
- Maistra 0.10 release
* Mon Mar 4 2019 Brian Avery <bavery@redhat.com> - 0.9.0
- Maistra 0.9 release
* Thu Feb 14 2019 Kevin Conner <kconner@redhat.com> - 0.8.0
- First package
* Mon Jan 14 2019 Jonh Wendell <jonh.wendell@redhat.com> - 0.6.0
- First package
