# Issues for this repository are disabled

Issues for this repository are tracked in Red Hat Jira. Please head to <https://issues.redhat.com/browse/MAISTRA> in order to browse or open an issue.

# SPEC files for creation of Istio RPMs

## Versions

### Master
`master` branch of this repository tracks the master branch of Istio. Currently this is unused. 

### Releases
Branches named `maistra-X.X.X` track Maistra releases.

A repository for CentOS builds is available at [Fedora COPR](https://copr.fedorainfracloud.org/coprs/g/maistra/istio/).


### Building 
The following instructions apply to all RPMs in this repository. 

### Generating a Source RPM
* Change directory to the directory for the RPM to build. 
* Update the metadata for the RPM see [Fields to update](#fields-to-update) for more details. These 
should be updated to match the GitHub commit ID of the commit to use for the RPM. Some repositories 
have one commit andothers have multiple commits depending on how many GitHub repositories the build 
references. 
* Execute ./update.sh. This will generate a .tar.gz file containing the sources to use for the build
as well as update the sources file. These changes and the changes to the .spec file should be
submitted in a pull request. 
* Generate the source rpm via: `fedpkg --release el8 srpm`

### Local Builds
The RPM can be compiled locally using the following command: `fedpkg --release el8 local`

### Online Builds
The RPM can be compiled on COPR using the following command: `copr build @coprgroup/coprrepo istio-1.0.0-2.el8.src.rpm`


#### Fields to update
##### Istio 
###### Buildinfo
- [ ] buildVersion
- [ ] buildGitRevision
###### istio.spec
- [ ] git_commit -- this should match the GitHub commit ID in the [Istio](https://github.com/maistra/istio) repo to use for this RPM.
- [ ] version -- this is the semantic version for the RPM.
- [ ] release -- this should be incremented on every build, starting at 1 for a new release. 
- [ ] changelog -- two new lines should be added for every build explaining the changes in the build.
###### istiorc
- [ ] TAG -- this should match the release-build. For the second build of 1.0.0, this would be 1.0.0-2.

##### IOR 
###### ior.spec
- [ ] git_commit -- this should match the GitHub commit ID in the [IOR](https://github.com/maistra/ior) repo to use for this RPM. 
- [ ] version -- this is the semantic version for the RPM.
- [ ] release -- this should be incremented on every build, starting at 1 for a new release. 
- [ ] changelog -- two new lines should be added for every build explaining the changes in the build.


##### Istio-operator 
###### istio-operator.spec
- [ ] git_commit -- this should match the GitHub commit ID in the [Istio operator](https://github.com/maistra/istio-operator) repo to use for this RPM. 
- [ ] version -- this is the semantic version for the RPM.
- [ ] release -- this should be incremented on every build, starting at 1 for a new release. 
- [ ] changelog -- two new lines should be added for every build explaining the changes in the build.

##### Grafana
###### grafana.spec
- [ ] version -- this is the Grafana version for the RPM (downloaded from https://github.com/grafana/grafana).
- [ ] release -- this should be incremented on every build, starting at 1 for a new release. 
- [ ] changelog -- two new lines should be added for every build explaining the changes in the build.

##### Prometheus-promu
###### promu.spec
- [ ] version -- this is the Promu version for the RPM (downloaded from https://github.com/prometheus/promu).
- [ ] release -- this should be incremented on every build, starting at 1 for a new release. 
- [ ] changelog -- two new lines should be added for every build explaining the changes in the build.

##### Prometheus
###### prometheus.spec
- [ ] git_commit -- this should match the GitHub commit ID in the [Prometheus](https://github.com/maistra/prometheus) repo to use for this RPM. 
- [ ] version -- this is the Promu version for the RPM (downloaded from https://github.com/prometheus/promu).
- [ ] release -- this should be incremented on every build, starting at 1 for a new release. 
- [ ] changelog -- two new lines should be added for every build explaining the changes in the build.
