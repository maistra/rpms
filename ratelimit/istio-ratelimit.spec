# Run unit tests
%global with_tests 1
%global debug_package %{nil}

%global git_commit d8fc6a62f40b7ca2b22d1562fd528959e27e9a56
%global git_shortcommit  %(c=%{git_commit}; echo ${c:0:7})

%global provider        github
%global provider_tld    com
%global project         maistra
%global repo            ratelimit
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}

Name:           istio-ratelimit
Version:        2.1.0
Release:        0%{?dist}
Summary:        gRPC service designed to enable generic rate limit scenarios from different types of applications
License:        ASL 2.0
URL:            https://%{provider_prefix}

Source0:        https://%{provider_prefix}/archive/%{git_commit}/%{repo}-%{git_commit}.tar.gz

%global goipath github.com/maistra/istio
%gometa

%description
Go/gRPC service designed to enable generic rate limit scenarios from different types of applications.

%prep
rm -rf %{name}-%{version} && mkdir -p %{name}-%{version}
tar zxf %{SOURCE0} -C %{name}-%{version} --strip=1

%setup -D -T

%build

export GOPROXY=off
export CGO_ENABLED=0
export LDFLAGS="\
-B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \n') \
-extldflags '-static %__global_ldflags'"

mkdir OUT
# FIXME: Replace with "%%gobuild" macro once a recent enough version lands (probably rhel9)
go build -mod=vendor -ldflags "${LDFLAGS:-}" -tags="rpm_crashtraceback" -a -v -x \
   -o OUT/ratelimit ./src/service_cmd

%install
rm -rf $RPM_BUILD_ROOT && mkdir -p $RPM_BUILD_ROOT%{_bindir}
strip OUT/ratelimit
cp -pav OUT/ratelimit $RPM_BUILD_ROOT%{_bindir}/

%if 0%{?with_tests}

%check
TESTFLAGS="-race"
ARCH=$(uname -p)

if [ "${ARCH}" = "s390x" ]; then
  # go test: -race is only supported on linux/amd64, linux/ppc64le, linux/arm64, freebsd/amd64, netbsd/amd64, darwin/amd64 and windows/amd64
  TESTFLAGS=""
fi

%endif

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files
%license LICENSE
%doc     README.md
%{_bindir}/ratelimit

%changelog
* Wed Nov 3 2021 Jonh Wendell <jwendell@redhat.com> - 2.1.0-0
- Initial build for maistra 2.1.0
