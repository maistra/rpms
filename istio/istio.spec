# Run unit tests
%global with_tests 0
%global debug_package %{nil}

%global git_commit ad1e7094e816a514e9544445abc7adebb7bc2b15
%global git_shortcommit  %(c=%{git_commit}; echo ${c:0:7})

%global provider        github
%global provider_tld    com
%global project         maistra
%global repo            istio
# https://github.com/openshift-istio/istio
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     istio.io/istio

# Use /usr/local as base dir, once upstream heavily depends on that
%global _prefix /usr/local

Name:           istio
Version:        2.1.0
Release:        0%{?dist}
Summary:        An open platform to connect, manage, and secure microservices
License:        ASL 2.0
URL:            https://%{provider_prefix}

Source0:        https://%{provider_prefix}/archive/%{git_commit}/%{repo}-%{git_commit}.tar.gz

%global goipath github.com/maistra/istio
%gometa

%description
Istio is an open platform that provides a uniform way to connect, manage
and secure microservices. Istio supports managing traffic flows between
microservices, enforcing access policies, and aggregating telemetry data,
all without requiring changes to the microservice code.

########### pilot-discovery ###############
%package pilot-discovery
Summary:  The istio pilot discovery
Requires: istio = %{version}-%{release}

%description pilot-discovery
Istio is an open platform that provides a uniform way to connect, manage
and secure microservices. Istio supports managing traffic flows between
microservices, enforcing access policies, and aggregating telemetry data,
all without requiring changes to the microservice code.

This package contains the pilot-discovery program.

pilot-discovery is the main pilot component and belongs to Control Plane.

########### pilot-agent ###############
%package pilot-agent
Summary:  The istio pilot agent
Requires: istio = %{version}-%{release}

%description pilot-agent
Istio is an open platform that provides a uniform way to connect, manage
and secure microservices. Istio supports managing traffic flows between
microservices, enforcing access policies, and aggregating telemetry data,
all without requiring changes to the microservice code.

This package contains the pilot-agent program.

pilot-agent is agent that talks to Istio pilot. It belongs to Data Plane.
Along with Envoy, makes up the proxy that goes in the sidecar along with applications.

########### cni ###############
%package cni
Summary:  The istio CNI plugin and installer

%description cni
Istio is an open platform that provides a uniform way to connect, manage
and secure microservices. Istio supports managing traffic flows between
microservices, enforcing access policies, and aggregating telemetry data,
all without requiring changes to the microservice code.

This package contains the CNI plugin and installer.

cni is the Container Network Interface Plugin that runs on OpenShift
nodes and configures the iptables rules for each application pod that is
part of the service mesh.

%prep
rm -rf %{name}-%{version} && mkdir -p %{name}-%{version}
tar zxf %{SOURCE0} -C %{name}-%{version} --strip=1

%setup -D -T

%build

export GOPROXY=off
export CGO_ENABLED=0
export LDFLAGS="\
-B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \n') \
-X istio.io/pkg/version.buildVersion=MAISTRA_%{version}-%{release} \
-X istio.io/pkg/version.buildGitRevision=%{git_commit} \
-X istio.io/pkg/version.buildTag=%{version} \
-X istio.io/pkg/version.buildStatus=Clean \
-extldflags '-static %__global_ldflags'"

mkdir OUT
# FIXME: Replace with "%%gobuild" macro once a recent enough version lands (probably rhel9)
go build -mod=vendor -ldflags "${LDFLAGS:-}" -tags="rpm_crashtraceback" -a -v -x \
   -o OUT ./pilot/cmd/pilot-discovery ./pilot/cmd/pilot-agent ./mec/cmd/mec \
          ./cni/cmd/istio-cni ./cni/cmd/install-cni ./tools/istio-iptables

%install
rm -rf $RPM_BUILD_ROOT && mkdir -p $RPM_BUILD_ROOT%{_bindir}
binaries=(pilot-discovery pilot-agent mec install-cni istio-cni istio-iptables)
for i in "${binaries[@]}"; do
    strip OUT/$i
    cp -pav OUT/$i $RPM_BUILD_ROOT%{_bindir}/
done

# add artifacts
mkdir -p $RPM_BUILD_ROOT/var/lib/istio/envoy
cp tools/packaging/common/envoy_bootstrap.json $RPM_BUILD_ROOT/var/lib/istio/envoy/envoy_bootstrap_tmpl.json

mkdir -p $RPM_BUILD_ROOT/etc/istio/proxy
chmod g+w $RPM_BUILD_ROOT/etc/istio/proxy

mkdir -p $RPM_BUILD_ROOT/opt/cni/bin
mv $RPM_BUILD_ROOT%{_bindir}/istio-cni $RPM_BUILD_ROOT/opt/cni/bin
mv $RPM_BUILD_ROOT%{_bindir}/istio-iptables $RPM_BUILD_ROOT/opt/cni/bin

%if 0%{?with_tests}

%check
# FIXME: Add tests
%endif

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files
%license LICENSE
%doc     README.md

%files pilot-discovery
%{_bindir}/pilot-discovery
%{_bindir}/mec

%files pilot-agent
%{_bindir}/pilot-agent
/var/lib/istio/envoy

%files cni
%{_bindir}/install-cni
/opt/cni/bin/istio-cni
/opt/cni/bin/istio-iptables

%changelog
* Tue Nov 2 2021 Jonh Wendell <jwendell@redhat.com> - 2.1.0-0
- First 2.1 build
