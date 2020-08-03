%global grafana_arches %{lua: go_arches = {}
  for arch in rpm.expand("%{go_arches}"):gmatch("%S+") do
    go_arches[arch] = 1
  end
  for arch in rpm.expand("%{nodejs_arches}"):gmatch("%S+") do
    if go_arches[arch] then
      print(arch .. " ")
  end
end}

# Unbundle Grafana vendor sources and instead use BuildRequires
# on platforms that have enough golang devel support.
%if 0%{?rhel} == 0
%global           unbundle_vendor_sources 1
%endif

%if 0%{?rhel}
# emulate macros defined by the go-rpm-macros package
# https://pagure.io/go-rpm-macros/blob/master/f/rpm/macros.d/macros.go-compilers-golang
%define gobuild(o:) go build -buildmode pie -compiler gc -tags="rpm_crashtraceback ${BUILDTAGS:-}" -ldflags "${LDFLAGS:-}%{?currentgoldflags} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n') -extldflags '%__global_ldflags %{?__golang_extldflags}'" -a -v -x %{?**};
%define gotestextldflags %__global_ldflags %{?__golang_extldflags}
%define gotest() GO111MODULE=off go test -buildmode pie -compiler gc -ldflags "${LDFLAGS:-}%{?currentgoldflags} -extldflags '%{gotestextldflags}'" %{?**};
%endif

%global release_number 1

Name:             grafana
Version:          6.7.4
Release:          %{release_number}%{?dist}
Summary:          Metrics dashboard and graph editor
License:          ASL 2.0
URL:              https://grafana.org

# Source0 contains the tagged upstream sources
Source0:          https://github.com/grafana/grafana/archive/v%{version}/%{name}-%{version}.tar.gz

# Source1 contains the front-end javascript modules bundled into a webpack
Source1:          grafana_webpack-%{version}-%{release_number}.tar.gz

# Source2 contains Grafana configuration defaults for distributions
Source2:          distro-defaults.ini

# Source3 is the script to create the webpack from grafana sources
Source3:          make_grafana_webpack.sh

# Source4 is the script to generate the list of Go build dependencies:
Source4:          list_go_buildrequires.sh

# Source5 is the script to generate the list of bundled nodejs packages
Source5:          list_bundled_nodejs_packages.py


# Patches
Patch1:           001-login-oauth-use-oauth2-exchange.patch
Patch2:           002-remove-jaeger-tracing.patch
Patch3:           003-manpages.patch
Patch4:           004-wrappers-grafana-cli.patch
Patch5:           005-pkg-main-fix-import-paths.patch
Patch6:           006-pkg-setting-ini-default-section.patch
Patch7:           007-pkg-prometheus-client-query-range.patch
Patch8:           008-pkg-services-notifications-codes-Unknwon.patch
Patch9:           009-pkg-fix-xorm-import.patch

# Intersection of go_arches and nodejs_arches
ExclusiveArch:    %{grafana_arches}

# https://bugzilla.redhat.com/show_bug.cgi?id=1752991
# unfortunately the golang_arches macro of go-srpm-macros doesn't reflect that change yet
ExcludeArch:      i686

# omit golang debugsource, see BZ995136 and related
%global           dwz_low_mem_die_limit 0
%global           _debugsource_template %{nil}

%global           GRAFANA_USER %{name}
%global           GRAFANA_GROUP %{name}
%global           GRAFANA_HOME %{_datadir}/%{name}

# grafana-server service daemon uses systemd
%{?systemd_requires}
Requires(pre):    shadow-utils

BuildRequires:    git, systemd, golang, go-srpm-macros

%if 0%{?fedora} || 0%{?rhel} > 7
Recommends: grafana-cloudwatch = %{version}-%{release}
Recommends: grafana-elasticsearch = %{version}-%{release}
Recommends: grafana-azure-monitor = %{version}-%{release}
Recommends: grafana-graphite = %{version}-%{release}
Recommends: grafana-influxdb = %{version}-%{release}
Recommends: grafana-loki = %{version}-%{release}
Recommends: grafana-mssql = %{version}-%{release}
Recommends: grafana-mysql = %{version}-%{release}
Recommends: grafana-opentsdb = %{version}-%{release}
Recommends: grafana-postgres = %{version}-%{release}
Recommends: grafana-prometheus = %{version}-%{release}
Recommends: grafana-stackdriver = %{version}-%{release}
Recommends: grafana-pcp >= 2
%endif

%if 0%{?unbundle_vendor_sources}
# golang build deps. These allow us to unbundle vendor golang source.
# Note: generated with the list_go_buildrequires.sh script (see README.md)
BuildRequires: golang(github.com/apache/arrow/go/arrow)
BuildRequires: golang(github.com/apache/arrow/go/arrow/array)
BuildRequires: golang(github.com/apache/arrow/go/arrow/ipc)
BuildRequires: golang(github.com/apache/arrow/go/arrow/memory)
BuildRequires: golang(github.com/aws/aws-sdk-go/aws)
BuildRequires: golang(github.com/aws/aws-sdk-go/aws/awsutil)
BuildRequires: golang(github.com/aws/aws-sdk-go/aws/credentials)
BuildRequires: golang(github.com/aws/aws-sdk-go/aws/credentials/ec2rolecreds)
BuildRequires: golang(github.com/aws/aws-sdk-go/aws/credentials/endpointcreds)
BuildRequires: golang(github.com/aws/aws-sdk-go/aws/defaults)
BuildRequires: golang(github.com/aws/aws-sdk-go/aws/ec2metadata)
BuildRequires: golang(github.com/aws/aws-sdk-go/aws/request)
BuildRequires: golang(github.com/aws/aws-sdk-go/aws/session)
BuildRequires: golang(github.com/aws/aws-sdk-go/service/cloudwatch)
BuildRequires: golang(github.com/aws/aws-sdk-go/service/ec2)
BuildRequires: golang(github.com/aws/aws-sdk-go/service/ec2/ec2iface)
BuildRequires: golang(github.com/aws/aws-sdk-go/service/resourcegroupstaggingapi)
BuildRequires: golang(github.com/aws/aws-sdk-go/service/resourcegroupstaggingapi/resourcegroupstaggingapiiface)
BuildRequires: golang(github.com/aws/aws-sdk-go/service/s3/s3manager)
BuildRequires: golang(github.com/aws/aws-sdk-go/service/sts)
BuildRequires: golang(github.com/benbjohnson/clock)
BuildRequires: golang(github.com/bradfitz/gomemcache/memcache)
BuildRequires: golang(github.com/BurntSushi/toml)
BuildRequires: golang(github.com/cheekybits/genny/generic)
BuildRequires: golang(github.com/crewjam/saml)
BuildRequires: golang(github.com/davecgh/go-spew/spew)
BuildRequires: golang(github.com/denisenkom/go-mssqldb)
BuildRequires: golang(github.com/facebookgo/inject)
BuildRequires: golang(github.com/fatih/color)
BuildRequires: golang(github.com/gobwas/glob)
BuildRequires: golang(github.com/golang/protobuf/proto)
BuildRequires: golang(github.com/go-macaron/binding)
BuildRequires: golang(github.com/go-macaron/gzip)
BuildRequires: golang(github.com/go-macaron/session)
BuildRequires: golang(github.com/google/go-cmp/cmp)
BuildRequires: golang(github.com/google/go-cmp/cmp/cmpopts)
BuildRequires: golang(github.com/gorilla/websocket)
BuildRequires: golang(github.com/gosimple/slug)
BuildRequires: golang(github.com/go-sql-driver/mysql)
BuildRequires: golang(github.com/go-stack/stack)
BuildRequires: golang(github.com/go-xorm/core)
BuildRequires: golang(github.com/hashicorp/go-hclog)
BuildRequires: golang(github.com/hashicorp/go-plugin)
BuildRequires: golang(github.com/hashicorp/go-version)
BuildRequires: golang(github.com/inconshreveable/log15)
BuildRequires: golang(github.com/jmespath/go-jmespath)
BuildRequires: golang(github.com/jung-kurt/gofpdf)
BuildRequires: golang(github.com/lib/pq)
BuildRequires: golang(github.com/linkedin/goavro)
BuildRequires: golang(github.com/mattetti/filebuffer)
BuildRequires: golang(github.com/mattn/go-isatty)
BuildRequires: golang(github.com/mattn/go-sqlite3)
BuildRequires: golang(github.com/opentracing/opentracing-go)
BuildRequires: golang(github.com/opentracing/opentracing-go/ext)
BuildRequires: golang(github.com/opentracing/opentracing-go/log)
BuildRequires: golang(github.com/patrickmn/go-cache)
BuildRequires: golang(github.com/pkg/errors)
BuildRequires: golang(github.com/prometheus/client_golang/api)
BuildRequires: golang(github.com/prometheus/client_golang/api/prometheus/v1)
BuildRequires: golang(github.com/prometheus/client_golang/prometheus)
BuildRequires: golang(github.com/prometheus/client_golang/prometheus/promhttp)
BuildRequires: golang(github.com/prometheus/client_model/go)
BuildRequires: golang(github.com/prometheus/common/expfmt)
BuildRequires: golang(github.com/prometheus/common/model)
BuildRequires: golang(github.com/robfig/cron)
BuildRequires: golang(github.com/smartystreets/goconvey/convey)
BuildRequires: golang(github.com/stretchr/testify/require)
BuildRequires: golang(github.com/teris-io/shortid)
BuildRequires: golang(github.com/ua-parser/uap-go/uaparser)
BuildRequires: golang(github.com/uber/jaeger-client-go/config)
BuildRequires: golang(github.com/uber/jaeger-client-go/zipkin)
BuildRequires: golang(github.com/Unknwon/com)
BuildRequires: golang(github.com/urfave/cli/v2)
BuildRequires: golang(github.com/VividCortex/mysqlerr)
BuildRequires: golang(github.com/yudai/gojsondiff)
BuildRequires: golang(github.com/yudai/gojsondiff/formatter)
BuildRequires: golang(golang.org/x/crypto/pbkdf2)
BuildRequires: golang(golang.org/x/net/context)
BuildRequires: golang(golang.org/x/net/context/ctxhttp)
BuildRequires: golang(golang.org/x/oauth2)
BuildRequires: golang(golang.org/x/oauth2/google)
BuildRequires: golang(golang.org/x/oauth2/jwt)
BuildRequires: golang(golang.org/x/sync/errgroup)
BuildRequires: golang(golang.org/x/xerrors)
BuildRequires: golang(google.golang.org/grpc)
BuildRequires: golang(google.golang.org/grpc/codes)
BuildRequires: golang(google.golang.org/grpc/metadata)
BuildRequires: golang(google.golang.org/grpc/status)
BuildRequires: golang(gopkg.in/ini.v1)
BuildRequires: golang(gopkg.in/ldap.v3)
BuildRequires: golang(gopkg.in/macaron.v1)
BuildRequires: golang(gopkg.in/mail.v2)
BuildRequires: golang(gopkg.in/redis.v5)
BuildRequires: golang(gopkg.in/robfig/cron.v3)
BuildRequires: golang(gopkg.in/square/go-jose.v2)
BuildRequires: golang(gopkg.in/square/go-jose.v2/jwt)
BuildRequires: golang(gopkg.in/yaml.v2)
BuildRequires: golang(xorm.io/xorm)
%endif

# Declare all nodejs modules bundled in the webpack - this is for security
# purposes so if nodejs-foo ever needs an update, affected packages can be
# easily identified.
# Note: generated with the list_bundled_nodejs_packages.sh script (see README.md)
Provides: bundled(nodejs-@braintree/sanitize-url) = 4.0.0
Provides: bundled(nodejs-@grafana/slate-react) = 0.22.9-grafana
Provides: bundled(nodejs-@reduxjs/toolkit) = 1.2.1
Provides: bundled(nodejs-@torkelo/react-select) = 3.0.8
Provides: bundled(nodejs-@types/md5) = 2.1.33
Provides: bundled(nodejs-@types/react-loadable) = 5.5.2
Provides: bundled(nodejs-@types/react-virtualized-auto-sizer) = 1.0.0
Provides: bundled(nodejs-@types/uuid) = 3.4.7
Provides: bundled(nodejs-abortcontroller-polyfill) = 1.4.0
Provides: bundled(nodejs-angular) = 1.6.9
Provides: bundled(nodejs-angular-bindonce) = 0.3.1
Provides: bundled(nodejs-angular-native-dragdrop) = 1.2.2
Provides: bundled(nodejs-angular-route) = 1.6.6
Provides: bundled(nodejs-angular-sanitize) = 1.6.6
Provides: bundled(nodejs-baron) = 3.0.3
Provides: bundled(nodejs-brace) = 0.10.0
Provides: bundled(nodejs-calculate-size) = 1.1.1
Provides: bundled(nodejs-classnames) = 2.2.6
Provides: bundled(nodejs-clipboard) = 2.0.4
Provides: bundled(nodejs-core-js) = 1.2.7
Provides: bundled(nodejs-d3) = 5.15.0
Provides: bundled(nodejs-d3-scale-chromatic) = 1.5.0
Provides: bundled(nodejs-emotion) = 10.0.27
Provides: bundled(nodejs-eventemitter3) = 2.0.3
Provides: bundled(nodejs-fast-text-encoding) = 1.0.0
Provides: bundled(nodejs-file-saver) = 1.3.8
Provides: bundled(nodejs-hoist-non-react-statics) = 3.3.0
Provides: bundled(nodejs-immutable) = 3.8.2
Provides: bundled(nodejs-is-hotkey) = 0.1.4
Provides: bundled(nodejs-jquery) = 3.4.1
Provides: bundled(nodejs-lodash) = 3.10.1
Provides: bundled(nodejs-lru-cache) = 4.1.5
Provides: bundled(nodejs-marked) = 0.3.19
Provides: bundled(nodejs-md5) = 2.2.1
Provides: bundled(nodejs-memoize-one) = 4.1.0
Provides: bundled(nodejs-moment) = 2.24.0
Provides: bundled(nodejs-mousetrap) = 1.6.3
Provides: bundled(nodejs-mousetrap-global-bind) = 1.1.0
Provides: bundled(nodejs-nodemon) = 1.18.10
Provides: bundled(nodejs-papaparse) = 4.6.3
Provides: bundled(nodejs-prismjs) = 1.16.0
Provides: bundled(nodejs-prop-types) = 15.7.2
Provides: bundled(nodejs-rc-cascader) = 0.17.5
Provides: bundled(nodejs-re-resizable) = 6.2.0
Provides: bundled(nodejs-react) = 16.10.2
Provides: bundled(nodejs-react-dom) = 16.10.2
Provides: bundled(nodejs-react-grid-layout) = 0.17.1
Provides: bundled(nodejs-react-highlight-words) = 0.11.0
Provides: bundled(nodejs-react-loadable) = 5.5.0
Provides: bundled(nodejs-react-popper) = 1.3.3
Provides: bundled(nodejs-react-redux) = 7.1.1
Provides: bundled(nodejs-react-sizeme) = 2.5.2
Provides: bundled(nodejs-react-split-pane) = 0.1.89
Provides: bundled(nodejs-react-transition-group) = 2.6.1
Provides: bundled(nodejs-react-use) = 12.8.0
Provides: bundled(nodejs-react-virtualized-auto-sizer) = 1.0.2
Provides: bundled(nodejs-react-window) = 1.7.1
Provides: bundled(nodejs-redux) = 3.7.2
Provides: bundled(nodejs-redux-logger) = 3.0.6
Provides: bundled(nodejs-redux-thunk) = 2.3.0
Provides: bundled(nodejs-regenerator-runtime) = 0.11.1
Provides: bundled(nodejs-reselect) = 4.0.0
Provides: bundled(nodejs-rst2html) = 1.0.4
Provides: bundled(nodejs-rxjs) = 5.5.12
Provides: bundled(nodejs-search-query-parser) = 1.5.2
Provides: bundled(nodejs-slate) = 0.47.8
Provides: bundled(nodejs-slate-plain-serializer) = 0.7.10
Provides: bundled(nodejs-tether) = 1.4.5
Provides: bundled(nodejs-tether-drop) = 1.5.0
Provides: bundled(nodejs-tinycolor2) = 1.4.1
Provides: bundled(nodejs-tti-polyfill) = 0.2.2
Provides: bundled(nodejs-uuid) = 3.3.3
Provides: bundled(nodejs-whatwg-fetch) = 3.0.0
Provides: bundled(nodejs-xss) = 1.0.3


%description
Grafana is an open source, feature rich metrics dashboard and graph editor for
Graphite, InfluxDB & OpenTSDB.


%package cloudwatch
Requires: %{name} = %{version}-%{release}
Summary: Grafana cloudwatch datasource

%description cloudwatch
The Grafana cloudwatch datasource.

%package elasticsearch
Requires: %{name} = %{version}-%{release}
Summary: Grafana elasticsearch datasource

%description elasticsearch
The Grafana elasticsearch datasource.

%package azure-monitor
Requires: %{name} = %{version}-%{release}
Summary: Grafana azure-monitor datasource

%description azure-monitor
The Grafana azure-monitor datasource.

%package graphite
Requires: %{name} = %{version}-%{release}
Summary: Grafana graphite datasource

%description graphite
The Grafana graphite datasource.

%package influxdb
Requires: %{name} = %{version}-%{release}
Summary: Grafana influxdb datasource

%description influxdb
The Grafana influxdb datasource.

%package loki
Requires: %{name} = %{version}-%{release}
Summary: Grafana loki datasource

%description loki
The Grafana loki datasource.

%package mssql
Requires: %{name} = %{version}-%{release}
Summary: Grafana mssql datasource

%description mssql
The Grafana mssql datasource.

%package mysql
Requires: %{name} = %{version}-%{release}
Summary: Grafana mysql datasource

%description mysql
The Grafana mysql datasource.

%package opentsdb
Requires: %{name} = %{version}-%{release}
Summary: Grafana opentsdb datasource

%description opentsdb
The Grafana opentsdb datasource.

%package postgres
Requires: %{name} = %{version}-%{release}
Summary: Grafana postgres datasource

%description postgres
The Grafana postgres datasource.

%package prometheus
Requires: %{name} = %{version}-%{release}
Summary: Grafana prometheus datasource

%description prometheus
The Grafana prometheus datasource.

%package stackdriver
Requires: %{name} = %{version}-%{release}
Summary: Grafana stackdriver datasource

%description stackdriver
The Grafana stackdriver datasource.


%prep
%setup -q -T -D -b 0
%setup -q -T -D -b 1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch6 -p1

%if 0%{?unbundle_vendor_sources}
%patch5 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%endif

# Set up build subdirs and links
mkdir -p %{_builddir}/src/github.com/grafana
ln -sf %{_builddir}/%{name}-%{version} \
    %{_builddir}/src/github.com/grafana/grafana

# remove some (apparent) development files, for rpmlint
rm -f public/sass/.sass-lint.yml public/test/.jshintrc

%if 0%{?unbundle_vendor_sources}
# Unbundle all grafana vendor sources, as per BuildRequires above.
# Note there are some exceptions.
cp --parents -a \
    vendor/github.com/grafana/grafana-plugin-model \
    vendor/github.com/grafana/grafana-plugin-sdk-go \
    %{_builddir}
rm -r vendor # remove all vendor sources
mv %{_builddir}/vendor vendor # put back what we're keeping
%endif

%build
# Build the server-side binaries
cd %{_builddir}/src/github.com/grafana/grafana
%global archbindir bin/`go env GOOS`-`go env GOARCH`
echo _builddir=%{_builddir} archbindir=%{archbindir} gopath=%{gopath}
[ ! -d %{archbindir} ] && mkdir -p %{archbindir}

# non-modular build
export GOPATH=%{_builddir}:%{gopath}
export GO111MODULE=off; rm -f go.mod

# see grafana-X.X.X/build.go
export LDFLAGS="-X main.version=%{version} -X main.buildstamp=${SOURCE_DATE_EPOCH}"
for cmd in grafana-cli grafana-server; do
    %gobuild -o %{archbindir}/${cmd} ./pkg/cmd/${cmd}
done

%install
# Fix up arch bin directories
[ ! -d bin/x86_64 ] && ln -sf linux-amd64 bin/x86_64
[ ! -d bin/i386 ] && ln -sf linux-386 bin/i386
[ ! -d bin/ppc64le ] && ln -sf linux-ppc64le bin/ppc64le
[ ! -d bin/s390x ] && ln -sf linux-s390x bin/s390x
[ ! -d bin/arm ] && ln -sf linux-arm bin/arm
[ ! -d bin/arm64 ] && ln -sf linux-arm64 bin/aarch64
[ ! -d bin/aarch64 ] && ln -sf linux-aarch64 bin/aarch64

# dirs, shared files, public html, webpack
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_datadir}/%{name}
install -d %{buildroot}%{_libexecdir}/%{name}
cp -a conf public %{buildroot}%{_datadir}/%{name}

# wrappers
install -p -m 755 packaging/wrappers/grafana-cli %{buildroot}%{_sbindir}/%{name}-cli

# binaries
install -p -m 755 %{archbindir}/%{name}-server %{buildroot}%{_sbindir}
install -p -m 755 %{archbindir}/%{name}-cli %{buildroot}%{_libexecdir}/%{name}

# man pages
install -d %{buildroot}%{_mandir}/man1
install -p -m 644 docs/man/man1/* %{buildroot}%{_mandir}/man1

# config dirs
install -d %{buildroot}%{_sysconfdir}/%{name}
install -d %{buildroot}%{_sysconfdir}/sysconfig

# config defaults
install -p -m 640 %{SOURCE2} %{buildroot}%{_sysconfdir}/%{name}/grafana.ini
install -p -m 640 conf/ldap.toml %{buildroot}%{_sysconfdir}/%{name}/ldap.toml
install -p -m 644 %{SOURCE2} %{buildroot}%{_datadir}/%{name}/conf/defaults.ini
install -p -m 644 packaging/rpm/sysconfig/grafana-server \
    %{buildroot}%{_sysconfdir}/sysconfig/grafana-server

# config database directory and plugins
install -d -m 750 %{buildroot}%{_sharedstatedir}/%{name}
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{name}/plugins

# log directory
install -d %{buildroot}%{_localstatedir}/log/%{name}

# systemd service files
install -d %{buildroot}%{_unitdir} # only needed for manual rpmbuilds
install -p -m 644 packaging/rpm/systemd/grafana-server.service \
    %{buildroot}%{_unitdir}

# daemon run pid file config for using tmpfs
install -d %{buildroot}%{_tmpfilesdir}
echo "d %{_rundir}/%{name} 0755 %{GRAFANA_USER} %{GRAFANA_GROUP} -" \
    > %{buildroot}%{_tmpfilesdir}/%{name}.conf

%pre
getent group %{GRAFANA_GROUP} >/dev/null || groupadd -r %{GRAFANA_GROUP}
getent passwd %{GRAFANA_USER} >/dev/null || \
    useradd -r -g %{GRAFANA_GROUP} -d %{GRAFANA_HOME} -s /sbin/nologin \
    -c "%{GRAFANA_USER} user account" %{GRAFANA_USER}
exit 0

%preun
%systemd_preun grafana-server.service

%post
%systemd_post grafana-server.service
# create grafana.db with secure permissions on new installations
# otherwise grafana-server is creating grafana.db on first start
# with world-readable permissions, which may leak encrypted datasource
# passwords to all users (if the secret_key in grafana.ini was not changed)

# https://bugzilla.redhat.com/show_bug.cgi?id=1805472
if [ "$1" = 1 ] && [ ! -f %{_sharedstatedir}/%{name}/grafana.db ]; then
    touch %{_sharedstatedir}/%{name}/grafana.db
fi

# apply secure permissions to grafana.db if it exists
# (may not exist on upgrades, because users can choose between sqlite/mysql/postgres)
if [ -f %{_sharedstatedir}/%{name}/grafana.db ]; then
    chown %{GRAFANA_USER}:%{GRAFANA_GROUP} %{_sharedstatedir}/%{name}/grafana.db
    chmod 640 %{_sharedstatedir}/%{name}/grafana.db
fi

# required for upgrades
chmod 640 %{_sysconfdir}/%{name}/grafana.ini
chmod 640 %{_sysconfdir}/%{name}/ldap.toml

%postun
%systemd_postun_with_restart grafana-server.service


%check
cd %{_builddir}/src/github.com/grafana/grafana
export GOPATH=%{_builddir}:%{gopath}
# remove tests currently failing - these two are due to a symlink
# BUILD/src/github.com/grafana/grafana -> BUILD/grafana-6.6.1
rm -f pkg/services/provisioning/dashboards/file_reader_linux_test.go
rm -f pkg/services/provisioning/dashboards/file_reader_test.go
export GO111MODULE=off
%gotest ./pkg/...


%files
# binaries and wrappers
%{_sbindir}/%{name}-server
%{_sbindir}/%{name}-cli
%{_libexecdir}/%{name}

# config files
%dir %{_sysconfdir}/%{name}
%config(noreplace) %attr(640, root, %{GRAFANA_GROUP}) %{_sysconfdir}/%{name}/grafana.ini
%config(noreplace) %attr(640, root, %{GRAFANA_GROUP}) %{_sysconfdir}/%{name}/ldap.toml
%config(noreplace) %{_sysconfdir}/sysconfig/grafana-server

# Grafana configuration to dynamically create /run/grafana/grafana.pid on tmpfs
%{_tmpfilesdir}/%{name}.conf

# config database directory and plugins
%attr(750, %{GRAFANA_USER}, %{GRAFANA_GROUP}) %dir %{_sharedstatedir}/%{name}
%attr(-, %{GRAFANA_USER}, %{GRAFANA_GROUP}) %dir %{_sharedstatedir}/%{name}/plugins

# shared directory and all files therein, except some datasources
%{_datadir}/%{name}

# built-in datasources that are sub-packaged
%global dsdir %{_datadir}/%{name}/public/app/plugins/datasource
%exclude %{dsdir}/cloudwatch 
%exclude %{dsdir}/elasticsearch 
%exclude %{dsdir}/graphite
%exclude %{dsdir}/grafana-azure-monitor-datasource
%exclude %{dsdir}/influxdb
%exclude %{dsdir}/loki
%exclude %{dsdir}/mssql
%exclude %{dsdir}/mysql
%exclude %{dsdir}/opentsdb
%exclude %{dsdir}/postgres
%exclude %{dsdir}/prometheus
%exclude %{dsdir}/stackdriver

%dir %{_datadir}/%{name}/conf
%attr(-, root, %{GRAFANA_GROUP}) %{_datadir}/%{name}/conf/*

# systemd service file
%{_unitdir}/grafana-server.service

# log directory - grafana.log is created by grafana-server, and it does it's own log rotation
%attr(0755, %{GRAFANA_USER}, %{GRAFANA_GROUP}) %dir %{_localstatedir}/log/%{name}

# man pages for grafana binaries
%{_mandir}/man1/%{name}-server.1*
%{_mandir}/man1/%{name}-cli.1*

# other docs and license
%license LICENSE
%doc CHANGELOG.md CODE_OF_CONDUCT.md CONTRIBUTING.md NOTICE.md
%doc PLUGIN_DEV.md README.md ROADMAP.md UPGRADING_DEPENDENCIES.md

#
# datasources split out into subpackages
#
%files cloudwatch
%{_datadir}/%{name}/public/app/plugins/datasource/cloudwatch
%doc %{_datadir}/%{name}/public/app/plugins/datasource/cloudwatch/README.md

%files elasticsearch
%{_datadir}/%{name}/public/app/plugins/datasource/elasticsearch
%doc %{_datadir}/%{name}/public/app/plugins/datasource/elasticsearch/README.md

%files azure-monitor
%{_datadir}/%{name}/public/app/plugins/datasource/grafana-azure-monitor-datasource

%files graphite
%{_datadir}/%{name}/public/app/plugins/datasource/graphite
%doc %{_datadir}/%{name}/public/app/plugins/datasource/graphite/README.md

%files influxdb
%{_datadir}/%{name}/public/app/plugins/datasource/influxdb
%doc %{_datadir}/%{name}/public/app/plugins/datasource/influxdb/README.md

%files loki
%{_datadir}/%{name}/public/app/plugins/datasource/loki
%doc %{_datadir}/%{name}/public/app/plugins/datasource/loki/README.md

%files mssql
%{_datadir}/%{name}/public/app/plugins/datasource/mssql
%doc %{_datadir}/%{name}/public/app/plugins/datasource/mssql/README.md

%files mysql
%{_datadir}/%{name}/public/app/plugins/datasource/mysql
%doc %{_datadir}/%{name}/public/app/plugins/datasource/mysql/README.md

%files opentsdb
%{_datadir}/%{name}/public/app/plugins/datasource/opentsdb
%doc %{_datadir}/%{name}/public/app/plugins/datasource/opentsdb/README.md

%files postgres
%{_datadir}/%{name}/public/app/plugins/datasource/postgres
%doc %{_datadir}/%{name}/public/app/plugins/datasource/postgres/README.md

%files prometheus
%{_datadir}/%{name}/public/app/plugins/datasource/prometheus
%doc %{_datadir}/%{name}/public/app/plugins/datasource/prometheus/README.md

%files stackdriver
%{_datadir}/%{name}/public/app/plugins/datasource/stackdriver
%doc %{_datadir}/%{name}/public/app/plugins/datasource/stackdriver/README.md


%changelog
* Mon Aug 03 2020 Jonh Wendell <jwendell@redhat.com> 6.7.4-1
- Reworked on top of 6.7.x
