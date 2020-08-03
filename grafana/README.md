# grafana
The grafana package

## Upgrade instructions
(replace X.Y.Z with the new Grafana version)

* update `Version` and `%changelog` in the specfile
* download source tarball and create webpack: `./make_grafana_webpack.sh X.Y.Z`
* update golang buildrequires: `./list_go_buildrequires.sh grafana-X.Y.Z` and replace the old golang `BuildRequires:` with the new ones
* update nodejs provides: `./list_bundled_nodejs_packages.py grafana-X.Y.Z` and replace the old nodejs `Provides:` with the new ones
* check if the default configuration has changed: `diff grafana-X.Y.Z/conf/defaults.ini distro-defaults.ini` and update `distro-defaults.ini` if necessary
* install all new golang build dependencies: `sudo dnf builddep grafana.spec` and create packages for missing dependencies
* run local build: `rpkg local`, and if any patches fail, update them accordingly
* run rpm linter: `rpkg lint`
* run local builds with different OS versions: `./run_container_build.sh version` (place not yet published dependencies in the `deps/` directory)
* run a scratch build: `fedpkg scratch-build --srpm`
