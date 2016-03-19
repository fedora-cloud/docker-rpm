%if 0%{?fedora}
%global with_devel 1
%global with_unit_test 1
%else
%global with_devel 0
%global with_unit_test 0
%endif

# modifying the dockerinit binary breaks the SHA1 sum check by docker
%global __os_install_post %{_rpmconfigdir}/brp-compress

# docker builds in a checksum of dockerinit into docker,
# so stripping the binaries breaks docker
%global debug_package %{nil}
%global provider github
%global provider_tld com
%global project docker
%global repo %{project}

%global import_path %{provider}.%{provider_tld}/%{project}/%{name}

# docker
%global git0 https://github.com/projectatomic/%{repo}
%global commit0 0f5ac89062e1f80bd87e7db9a94859adf7a188a7
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

# d-s-s
%global git1 https://github.com/projectatomic/%{repo}-storage-setup/
%global commit1 1c2b95b33b917adb9b681a953f2c6b6b2befae6d
%global shortcommit1 %(c=%{commit1}; echo ${c:0:7})
%global dss_libdir %{_exec_prefix}/lib/%{repo}-storage-setup

# docker-selinux
%global git2 https://github.com/projectatomic/%{repo}-selinux
%global commit2 afc876c0e8828cc0b73cf76bbf550e30b5e627aa
%global shortcommit2 %(c=%{commit2}; echo ${c:0:7})

# docker-utils
%global git3 https://github.com/vbatts/%{repo}-utils
%global commit3 dab51acd1b1a77f7cb01a1b7e2129ec85c846b71
%global shortcommit3 %(c=%{commit3}; echo ${c:0:7})

# docker-novolume-plugin
%global git4 https://github.com/projectatomic/%{repo}-novolume-plugin
%global commit4 77a55c1e22563a4b87d426bb89e7c9144c966742
%global shortcommit4 %(c=%{commit4}; echo ${c:0:7})

# v1.10-migrator
%global git5 https://github.com/%{repo}/v1.10-migrator
%global commit5 994c35cbf7ae094d4cb1230b85631ecedd77b0d8
%global shortcommit5 %(c=%{commit5}; echo ${c:0:7})

# forward-journald
%global git6 https://github.com/projectatomic/forward-journald
%global commit6 3b80098e33db819718544a02ad2f3f3289c23f99
%global shortcommit6 %(c=%{commit6}; echo ${c:0:7})

# docker-selinux stuff (prefix with ds_ for version/release etc.)
# Some bits borrowed from the openstack-selinux package
%global selinuxtype targeted
%global moduletype services
%global modulenames %{name}

# Usage: _format var format
# Expand 'modulenames' into various formats as needed
# Format must contain '$x' somewhere to do anything useful
%global _format() export %1=""; for x in %{modulenames}; do %1+=%2; %1+=" "; done;

# Relabel files
%global relabel_files() %{_sbindir}/restorecon -R %{_bindir}/%{name} %{_localstatedir}/run/%{name}.sock %{_localstatedir}/run/%{name}.pid %{_sysconfdir}/%{name} %{_localstatedir}/log/%{name} %{_localstatedir}/log/lxc %{_localstatedir}/lock/lxc %{_unitdir}/%{name}.service %{_sysconfdir}/%{name} &> /dev/null || :

# Version of SELinux we were using
%if 0%{?centos}
%global selinux_policyver 3.13.1-60
%else
%global selinux_policyver 3.13.1-155
%endif

Name: %{repo}
Epoch: 1
Version: 1.10.2
Release: 9.git%{shortcommit0}%{?dist}
Summary: Automates deployment of containerized applications
License: ASL 2.0
URL: https://%{provider}.%{provider_tld}/projectatomic/%{name}
ExclusiveArch: %{go_arches}

Source0: %{git0}/archive/%{commit0}/%{repo}-%{shortcommit0}.tar.gz
Source1: %{git1}/archive/%{commit1}/%{repo}-storage-setup-%{shortcommit1}.tar.gz
Source2: %{git2}/archive/%{commit2}/%{repo}-selinux-%{shortcommit2}.tar.gz
Source3: %{git3}/archive/%{commit3}/%{repo}-utils-%{shortcommit3}.tar.gz
Source4: %{git4}/archive/%{commit4}/%{repo}-novolume-plugin-%{shortcommit4}.tar.gz
Source5: %{repo}.service
Source6: %{repo}.sysconfig
Source7: %{repo}-storage.sysconfig
Source8: %{repo}-logrotate.sh
Source9: README.%{repo}-logrotate
Source10: %{repo}-network.sysconfig
Source11: %{git5}/archive/%{commit5}/v1.10-migrator-%{shortcommit5}.tar.gz
Source12: %{git6}/archive/%{commit6}/forward-journald-%{shortcommit6}.tar.gz

BuildRequires: git
BuildRequires: glibc-static
BuildRequires: go-md2man
BuildRequires: godep
BuildRequires: device-mapper-devel
BuildRequires: libseccomp-static >= 2.2.1
BuildRequires: pkgconfig(audit)
BuildRequires: btrfs-progs-devel
BuildRequires: sqlite-devel
BuildRequires: pkgconfig(systemd)
BuildRequires: %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}
%if 0%{?fedora} >= 21
# Resolves: rhbz#1165615
Requires: device-mapper-libs >= 1.02.90-1
%endif

# RE: rhbz#1195804 - ensure min NVR for selinux-policy
%if 0%{?centos}
Requires: selinux-policy >= %{selinux_policyver}
%else
Requires: selinux-policy >= 3.13.1-114
%endif
Requires: %{name}-selinux >= %{epoch}:%{version}-%{release}

# Resolves: rhbz#1045220
Requires: xz
Provides: lxc-%{name} = %{epoch}:%{version}-%{release}

# needs tar to be able to run containers
Requires: tar

# permitted by https://fedorahosted.org/fpc/ticket/341#comment:7
# In F22, the whole package should be renamed to be just "docker" and
# this changed to "Provides: docker-io".
%if 0%{?fedora} >= 22
Provides: %{name}-io = %{epoch}:%{version}-%{release}
Obsoletes: %{name}-io <= 1.5.0-19
%endif

# include d-s-s into main docker package and obsolete existing d-s-s rpm
# also update BRs and Rs
Requires: lvm2
Requires: xfsprogs
Obsoletes: %{name}-storage-setup <= 0.5-3

Requires: libseccomp >= 2.2.1
Requires: %{repo}-forward-journald = %{epoch}:%{version}-%{release}

%description
Docker is an open-source engine that automates the deployment of any
application as a lightweight, portable, self-sufficient container that will
run virtually anywhere.

Docker containers can encapsulate any payload, and will run consistently on
and between virtually any server. The same container that a developer builds
and tests on a laptop will run at scale, in production*, on VMs, bare-metal
servers, OpenStack clusters, public instances, or combinations of the above.

%if 0%{?with_devel}
%package devel
%ifarch %{golang_arches}
BuildRequires: golang >= 1.2.1-3
%else
BuildRequires: gcc-go >= %{gccgo_min_vers}
%endif
Provides: %{repo}-io-devel = %{epoch}:%{version}-%{release}
Provides: %{repo}-pkg-devel = %{epoch}:%{version}-%{release}
Provides: %{repo}-io-pkg-devel = %{epoch}:%{version}-%{release}
Summary:  A golang registry for global request variables (source libraries)
Provides: golang(%{import_path}) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/builder) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/builder/parser) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/builder/parser/dumper) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/builder/command) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/nat) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/utils) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/integration-cli) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/trust) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/events) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/volumes) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/dockerinit) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/engine) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/registry) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/registry/v2) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/api) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/api/client) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/api/stats) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/api/server) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/opts) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/builtins) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/runconfig) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/docker) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/contrib/docker-device-tool) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/contrib/host-integration) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/daemon) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/daemon/graphdriver) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/daemon/graphdriver/devmapper) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/daemon/graphdriver/aufs) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/daemon/graphdriver/overlay) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/daemon/graphdriver/vfs) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/daemon/graphdriver/btrfs) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/daemon/graphdriver/graphtest) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/daemon/networkdriver) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/daemon/networkdriver/ipallocator) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/daemon/networkdriver/portmapper) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/daemon/networkdriver/bridge) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/daemon/networkdriver/portallocator) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/daemon/execdriver) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/daemon/execdriver/execdrivers) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/daemon/execdriver/lxc) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/daemon/execdriver/native) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/daemon/execdriver/native/template) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/devicemapper) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/units) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/chrootarchive) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/mount) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/systemd) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/parsers) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/parsers/kernel) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/parsers/operatingsystem) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/parsers/filters) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/broadcastwriter) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/stdcopy) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/proxy) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/promise) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/pools) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/system) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/fileutils) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/mflag) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/mflag/example) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/timeutils) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/ioutils) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/pubsub) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/signal) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/listenbuffer) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/version) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/httputils) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/urlutil) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/sysinfo) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/archive) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/iptables) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/tailfile) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/graphdb) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/tarsum) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/namesgenerator) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/jsonlog) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/testutils) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/truncindex) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/homedir) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/symlink) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/networkfs/resolvconf) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/networkfs/etchosts) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/term) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/pkg/reexec) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/integration) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/links) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/image) = %{epoch}:%{version}-%{release}
Provides: golang(%{import_path}/graph) = %{epoch}:%{version}-%{release}

%description devel
%{summary}

This package provides the source libraries for Docker.
%endif

%package utils
Summary: External utilities for the %{name} experience

%description utils
%{summary}

%if 0%{?with_unit_test}
%package unit-test
Summary: %{summary} - for running unit tests

%description unit-test
%{summary} - for running unit tests
%endif

%package fish-completion
Summary: fish completion files for Docker
Requires: %{name} = %{epoch}:%{version}-%{release}
Requires: fish
Provides: %{name}-io-fish-completion = %{epoch}:%{version}-%{release}

%description fish-completion
This package installs %{summary}.

%package logrotate
Summary: cron job to run logrotate on Docker containers
Requires: %{name} = %{epoch}:%{version}-%{release}
Provides: %{name}-io-logrotate = %{epoch}:%{version}-%{release}

%description logrotate
This package installs %{summary}. logrotate is assumed to be installed on
containers for this to work, failures are silently ignored.

%package novolume-plugin
URL: %{git4}
License: MIT
Summary: Block container starts with local volumes defined
Requires: %{repo} = %{epoch}:%{version}-%{release}

%description novolume-plugin
When a volume in provisioned via the `VOLUME` instruction in a Dockerfile or
via `docker run -v volumename`, host's storage space is used. This could lead to
an unexpected out of space issue which could bring down everything.
There are situations where this is not an accepted behavior. PAAS, for
instance, can't allow their users to run their own images without the risk of
filling the entire storage space on a server. One solution to this is to deny users
from running images with volumes. This way the only storage a user gets can be limited
and PAAS can assign quota to it.

This plugin solves this issue by disallowing starting a container with
local volumes defined. In particular, the plugin will block `docker run` with:

- `--volumes-from`
- images that have `VOLUME`(s) defined
- volumes early provisioned with `docker volume` command

The only thing allowed will be just bind mounts.

%package selinux
Summary: SELinux policies for Docker
BuildRequires: selinux-policy
BuildRequires: selinux-policy-devel
Requires(post): selinux-policy-base >= %{selinux_policyver}
Requires(post): policycoreutils
%if 0%{?centos}
Requires(post): policycoreutils-python
%else
Requires(post): policycoreutils-python-utils
%endif
Requires(post): libselinux-utils
Provides: %{name}-io-selinux = %{epoch}:%{version}-%{release}

%description selinux
SELinux policy modules for use with Docker.

%package vim
Summary: vim syntax highlighting files for Docker
Requires: %{name} = %{epoch}:%{version}-%{release}
Requires: vim
Provides: %{name}-io-vim = %{epoch}:%{version}-%{release}

%description vim
This package installs %{summary}.

%package zsh-completion
Summary: zsh completion files for Docker
Requires: %{name} = %{epoch}:%{version}-%{release}
Requires: zsh
Provides: %{name}-io-zsh-completion = %{epoch}:%{version}-%{release}

%description zsh-completion
This package installs %{summary}.

%package v1.10-migrator
Summary: Calculates SHA256 checksums for docker layer content
License: ASL 2.0 and CC-BY-SA

%description v1.10-migrator
Starting from v1.10 docker uses content addressable IDs for the images and
layers instead of using generated ones. This tool calculates SHA256 checksums
for docker layer content, so that they don't need to be recalculated when the
daemon starts for the first time.

The migration usually runs on daemon startup but it can be quite slow(usually
100-200MB/s) and daemon will not be able to accept requests during
that time. You can run this tool instead while the old daemon is still
running and skip checksum calculation on startup.

%package forward-journald
Summary: Forward stdin to journald
License: ASL 2.0
BuildRequires: golang(github.com/coreos/go-systemd/journal)

%description forward-journald
Forward stdin to journald

The main driver for this program is < go 1.6rc2 has a issue where 10
SIGPIPE's on stdout or stderr cause go to generate a non-trappable SIGPIPE
killing the process. This happens when journald is restarted while docker is
running under systemd.

%prep
%setup -q -n %{repo}-%{commit0}

# here keep the new line above otherwise autosetup fails when applying patch
cp %{SOURCE9} .

# untar d-s-s
tar zxf %{SOURCE1}

# unpack %%{repo}-selinux
tar zxf %{SOURCE2}

# untar docker-utils
tar zxf %{SOURCE3}

# untar docker-novolume-plugin
tar zxf %{SOURCE4}

# untar v1.10-migrator
tar zxf %{SOURCE11}

# untar forward-journald
tar zxf %{SOURCE12}

%build
# set up temporary build gopath, and put our directory there
mkdir _build
pushd _build
mkdir -p src/%{provider}.%{provider_tld}/{%{repo},projectatomic,vbatts}
ln -s $(dirs +1 -l) src/%{import_path}
ln -s $(dirs +1 -l)/%{repo}-utils-%{commit3} src/%{provider}.%{provider_tld}/vbatts/%{repo}-utils
ln -s $(dirs +1 -l)/%{repo}-novolume-plugin-%{commit4} src/%{provider}.%{provider_tld}/projectatomic/%{repo}-novolume-plugin
ln -s $(dirs +1 -l)/forward-journald-%{commit6} src/%{provider}.%{provider_tld}/projectatomic/forward-journald
popd

export DOCKER_GITCOMMIT="%{shortcommit0}/%{version}"
export DOCKER_BUILDTAGS="selinux seccomp"
export GOPATH=$(pwd)/_build:$(pwd)/vendor:%{gopath}:$(pwd)/%{repo}-novolume-plugin-%{commit4}/Godeps/_workspace:$(pwd)/forward-journald-%{commit6}/vendor

DEBUG=1 bash -x hack/make.sh dynbinary
man/md2man-all.sh
cp contrib/syntax/vim/LICENSE LICENSE-vim-syntax
cp contrib/syntax/vim/README.md README-vim-syntax.md
cp %{repo}-novolume-plugin-%{commit4}/LICENSE LICENSE-novolume-plugin
cp %{repo}-novolume-plugin-%{commit4}/README.md README-novolume-plugin.md
go-md2man -in %{repo}-novolume-plugin-%{commit4}/man/docker-novolume-plugin.8.md -out docker-novolume-plugin.8

pushd $(pwd)/_build/src
go build -ldflags "-B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \n')" github.com/vbatts/%{repo}-utils/cmd/%{repo}-fetch
go build -ldflags "-B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \n')" github.com/vbatts/%{repo}-utils/cmd/%{repo}tarsum
go build -ldflags "-B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \n')" github.com/projectatomic/%{repo}-novolume-plugin
go build -ldflags "-B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \n')" github.com/projectatomic/forward-journald
popd

# build %%{repo}-selinux
pushd %{repo}-selinux-%{commit2}
make SHARE="%{_datadir}" TARGETS="%{modulenames}"
popd

# build v1.10-migrator
pushd v1.10-migrator-%{commit5}
make v1.10-migrator-local
popd

%install
# install binary
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_libexecdir}/%{repo}

# install utils and forward-journald
install -p -m 755 _build/src/%{repo}-fetch %{buildroot}%{_bindir}
install -p -m 755 _build/src/%{repo}tarsum %{buildroot}%{_bindir}
install -p -m 700 _build/src/forward-journald %{buildroot}%{_bindir}

for x in bundles/latest; do
    if ! test -d $x/dynbinary; then
    continue
    fi
    rm $x/dynbinary/*.md5 $x/dynbinary/*.sha256
    install -p -m 755 $x/dynbinary/%{repo}-%{version}* %{buildroot}%{_bindir}/%{repo}
    install -p -m 755 $x/dynbinary/%{repo}init-%{version}* %{buildroot}%{_libexecdir}/%{repo}/%{repo}init
    break
done

# install manpages
install -d %{buildroot}%{_mandir}/man1
install -p -m 644 man/man1/%{repo}*.1 %{buildroot}%{_mandir}/man1
install -d %{buildroot}%{_mandir}/man5
install -p -m 644 man/man5/Dockerfile.5 %{buildroot}%{_mandir}/man5

# install bash completion
install -dp %{buildroot}%{_datadir}/bash-completion/completions
install -p -m 644 contrib/completion/bash/%{repo} %{buildroot}%{_datadir}/bash-completion/completions

# install fish completion
# create, install and own /usr/share/fish/vendor_completions.d until
# upstream fish provides it
install -dp %{buildroot}%{_datadir}/fish/vendor_completions.d
install -p -m 644 contrib/completion/fish/%{repo}.fish %{buildroot}%{_datadir}/fish/vendor_completions.d

# install container logrotate cron script
install -dp %{buildroot}%{_sysconfdir}/cron.daily/
install -p -m 755 %{SOURCE8} %{buildroot}%{_sysconfdir}/cron.daily/%{repo}-logrotate

# install vim syntax highlighting
install -d %{buildroot}%{_datadir}/vim/vimfiles/{doc,ftdetect,syntax}
install -p -m 644 contrib/syntax/vim/doc/%{repo}file.txt %{buildroot}%{_datadir}/vim/vimfiles/doc
install -p -m 644 contrib/syntax/vim/ftdetect/%{repo}file.vim %{buildroot}%{_datadir}/vim/vimfiles/ftdetect
install -p -m 644 contrib/syntax/vim/syntax/%{repo}file.vim %{buildroot}%{_datadir}/vim/vimfiles/syntax

# install zsh completion
install -d %{buildroot}%{_datadir}/zsh/site-functions
install -p -m 644 contrib/completion/zsh/_%{repo} %{buildroot}%{_datadir}/zsh/site-functions

# install udev rules
install -d %{buildroot}%{_udevrulesdir}
install -p contrib/udev/80-%{repo}.rules %{buildroot}%{_udevrulesdir}

# install storage dir
install -d %{buildroot}%{_sharedstatedir}/%{repo}

# install secret patch directory
install -d %{buildroot}%{_datadir}/rhel/secrets

# install systemd/init scripts
install -d %{buildroot}%{_unitdir}
install -p -m 644 %{SOURCE5} %{buildroot}%{_unitdir}

# install novolume-plugin executable, unitfile, socket and man
install -d %{buildroot}/usr/lib/docker
install -p -m 755 _build/src/%{repo}-novolume-plugin %{buildroot}/usr/lib/docker
install -p -m 644 %{repo}-novolume-plugin-%{commit4}/systemd/%{repo}-novolume-plugin.service %{buildroot}%{_unitdir}
install -p -m 644 %{repo}-novolume-plugin-%{commit4}/systemd/%{repo}-novolume-plugin.socket %{buildroot}%{_unitdir}
install -d %{buildroot}%{_mandir}/man8
install -p -m 644 %{repo}-novolume-plugin.8 %{buildroot}%{_mandir}/man8

# for additional args
install -d %{buildroot}%{_sysconfdir}/sysconfig/
install -p -m 644 %{SOURCE6} %{buildroot}%{_sysconfdir}/sysconfig/%{repo}
install -p -m 644 %{SOURCE10} %{buildroot}%{_sysconfdir}/sysconfig/%{repo}-network
install -p -m 644 %{SOURCE7} %{buildroot}%{_sysconfdir}/sysconfig/%{repo}-storage

# install policy modules
%_format MODULES $x.pp.bz2
install -d %{buildroot}%{_datadir}/selinux/packages
install -m 0644 %{name}-selinux-%{commit2}/$MODULES %{buildroot}%{_datadir}/selinux/packages

%if 0%{?with_unit_test}
install -d -m 0755 %{buildroot}%{_sharedstatedir}/docker-unit-test/
cp -pav VERSION Dockerfile %{buildroot}%{_sharedstatedir}/docker-unit-test/.
for d in */ ; do
  cp -rpav $d %{buildroot}%{_sharedstatedir}/docker-unit-test/
done
# remove docker.initd as it requires /sbin/runtime no packages in Fedora
rm -rf %{buildroot}%{_sharedstatedir}/docker-unit-test/contrib/init/openrc/docker.initd
%endif

%if 0%{?with_devel}
# sources
install -d -p %{buildroot}%{gopath}/src/%{import_path}
rm -rf pkg/symlink/testdata

# remove dirs that won't be installed in devel
rm -rf vendor docs man _build bundles contrib/init hack project

# install sources to devel
for dir in */ ; do
    cp -rpav $dir %{buildroot}/%{gopath}/src/%{import_path}/
done
%endif

# remove %%{name}-selinux rpm spec file
rm -rf %{name}-selinux-%{commit2}/%{name}-selinux.spec

# install %%{name} config directory
install -dp %{buildroot}%{_sysconfdir}/%{name}

# install d-s-s
pushd %{repo}-storage-setup-%{commit1}
install -d %{buildroot}%{_bindir}
install -p -m 755 %{repo}-storage-setup.sh %{buildroot}%{_bindir}/%{repo}-storage-setup
install -d %{buildroot}%{_unitdir}
install -p -m 644 %{repo}-storage-setup.service %{buildroot}%{_unitdir}
install -d %{buildroot}%{dss_libdir}
install -p -m 644 %{repo}-storage-setup.conf %{buildroot}%{dss_libdir}/%{repo}-storage-setup
install -p -m 755 libdss.sh %{buildroot}%{dss_libdir}
install -d %{buildroot}%{_mandir}/man1
install -p -m 644 %{repo}-storage-setup.1 %{buildroot}%{_mandir}/man1
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -p -m 644 %{repo}-storage-setup-override.conf %{buildroot}%{_sysconfdir}/sysconfig/%{repo}-storage-setup
popd

# install v1.10-migrator
install -d %{buildroot}%{_bindir}
install -p -m 700 v1.10-migrator-%{commit5}/v1.10-migrator-local %{buildroot}%{_bindir}
cp v1.10-migrator-%{commit5}/CONTRIBUTING.md CONTRIBUTING-v1.10-migrator.md
cp v1.10-migrator-%{commit5}/README.md README-v1.10-migrator.md
cp v1.10-migrator-%{commit5}/LICENSE.code LICENSE-v1.10-migrator.code
cp v1.10-migrator-%{commit5}/LICENSE.docs LICENSE-v1.10-migrator.docs

%check
[ ! -w /run/%{name}.sock ] || {
    mkdir test_dir
    pushd test_dir
    git clone https://github.com/projectatomic/docker.git -b fedora-1.10.2
    pushd %{repo}
    make test
    popd
    popd
}

%post
%systemd_post %{repo}

%post selinux
# Install all modules in a single transaction
if [ $1 -eq 1 ]; then
    %{_sbindir}/setsebool -P -N virt_use_nfs=1 virt_sandbox_use_all_caps=1
fi
%_format MODULES %{_datadir}/selinux/packages/$x.pp.bz2
%{_sbindir}/semodule -n -s %{selinuxtype} -i $MODULES
if %{_sbindir}/selinuxenabled ; then
    %{_sbindir}/load_policy
    %relabel_files
    if [ $1 -eq 1 ]; then
    restorecon -R %{_sharedstatedir}/%{repo} &> /dev/null || :
    fi
fi

%preun
%systemd_preun %{repo}

%postun
%systemd_postun_with_restart %{repo}

%postun selinux
if [ $1 -eq 0 ]; then
%{_sbindir}/semodule -n -r %{modulenames} &> /dev/null || :
if %{_sbindir}/selinuxenabled ; then
%{_sbindir}/load_policy
%relabel_files
fi
fi

%triggerpost -n %{repo}-v1.10-migrator -- %{repo} < %{version}
%{_bindir}/v1.10-migrator-local 2>/dev/null
exit 0

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files
%license LICENSE LICENSE-novolume-plugin LICENSE-vim-syntax
%doc AUTHORS CHANGELOG.md CONTRIBUTING.md MAINTAINERS NOTICE README.md 
%doc README-novolume-plugin.md README-vim-syntax.md
%config(noreplace) %{_sysconfdir}/sysconfig/%{repo}
%config(noreplace) %{_sysconfdir}/sysconfig/%{repo}-network
%config(noreplace) %{_sysconfdir}/sysconfig/%{repo}-storage
%{_mandir}/man1/%{repo}*.1.gz
%{_mandir}/man5/Dockerfile.5.gz
%{_bindir}/%{repo}
%{_libexecdir}/%{repo}
%{_unitdir}/%{repo}.service
%{_unitdir}/%{repo}-novolume-plugin.socket
%{_datadir}/bash-completion/completions/%{repo}
%dir %{_datadir}/rhel/secrets
%dir %{_sharedstatedir}/%{repo}
%{_udevrulesdir}/80-%{repo}.rules
%{_sysconfdir}/%{repo}
# d-s-s specific
%config(noreplace) %{_sysconfdir}/sysconfig/%{repo}-storage-setup
%{_unitdir}/%{repo}-storage-setup.service
%{_bindir}/%{repo}-storage-setup
%dir %{dss_libdir}
%{dss_libdir}/*

%if 0%{?with_devel}
%files devel
%license LICENSE
%doc AUTHORS CHANGELOG.md CONTRIBUTING.md MAINTAINERS NOTICE README.md 
%dir %{gopath}/src/%{provider}.%{provider_tld}/%{project}
%{gopath}/src/%{import_path}
%endif

%if 0%{?with_unit_test}
%files unit-test
%{_sharedstatedir}/docker-unit-test/
%endif

%files fish-completion
%dir %{_datadir}/fish/vendor_completions.d/
%{_datadir}/fish/vendor_completions.d/%{name}.fish

%files logrotate
%doc README.%{name}-logrotate
%{_sysconfdir}/cron.daily/%{name}-logrotate

%files novolume-plugin
%license LICENSE-novolume-plugin
%doc README-novolume-plugin.md
/usr/lib/docker/%{repo}-novolume-plugin
%{_unitdir}/%{repo}-novolume-plugin.service
%{_unitdir}/%{repo}-novolume-plugin.socket
%{_mandir}/man8/%{repo}-novolume-plugin.8.gz

%files selinux
%doc %{repo}-selinux-%{commit2}/README.md
%{_datadir}/selinux/*

%files vim
%{_datadir}/vim/vimfiles/doc/%{repo}file.txt
%{_datadir}/vim/vimfiles/ftdetect/%{repo}file.vim
%{_datadir}/vim/vimfiles/syntax/%{repo}file.vim

%files zsh-completion
%{_datadir}/zsh/site-functions/_%{repo}

%files utils
%{_bindir}/%{repo}-fetch
%{_bindir}/%{repo}tarsum

%files v1.10-migrator
%license LICENSE-v1.10-migrator.{code,docs}
%doc CONTRIBUTING-v1.10-migrator.md README-v1.10-migrator.md
%{_bindir}/v1.10-migrator-local

%files forward-journald
%license forward-journald-%{commit6}/LICENSE
%doc forward-journald-%{commit6}/README.md
%{_bindir}/forward-journald

%changelog
* Sat Mar 19 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.2-9.git0f5ac89
- update docker-novolume-plugin to v1.0.8

* Wed Mar 16 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.2-8.git0f5ac89
- docker package runtime depends on docker-forward-journald

* Wed Mar 16 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.2-7.git0f5ac89
- Resolves: rhbz#1318361 - include docker-forward-journald subpackage
- bump release tag, -6 already built

* Fri Mar 04 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.10.2-6.git0f5ac89
- include docker-forward-journald subpackage commit#3b80098

* Fri Feb 26 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.2-5.git0f5ac89
- rebuilt to remove dockerroot user creation

* Wed Feb 24 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.2-4.git0f5ac89
- rebuilt to include dss_libdir directory

* Mon Feb 22 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.2-3.git0f5ac89
- built docker @projectatomic/fedora-1.10.2 commit#0f5ac89
- built d-s-s commit#1c2b95b
- built docker-selinux commit#b8aae8f
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#e478a5c
- built docker-v1.10-migrator commit#994c35

* Mon Feb 22 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.2-2.git86e59a5
- rebuilt to include /usr/share/rhel/secrets for the secret patch we're carrying

* Mon Feb 22 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.2-1.git86e59a5
- built docker @projectatomic/fedora-1.10.2 commit#86e59a5
- built d-s-s commit#1c2b95b
- built docker-selinux commit#b8aae8f
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#e478a5c
- built docker-v1.10-migrator commit#994c35

* Thu Feb 18 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.1-6.git6c71d8f
- rebuilt with seccomp enabled

* Tue Feb 16 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.1-5.git6c71d8f
- built docker @projectatomic/fedora-1.10.1 commit#6c71d8f
- built d-s-s commit#1c2b95b
- built docker-selinux commit#b8aae8f
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#e478a5c
- built docker-v1.10-migrator commit#994c35

* Tue Feb 16 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.1-4.git6c71d8f
- built docker @projectatomic/fedora-1.10.1 commit#6c71d8f
- built d-s-s commit#1c2b95b
- built docker-selinux commit#b8aae8f
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#2103b9e
- built docker-v1.10-migrator commit#994c35

* Fri Feb 12 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.1-3.git49805e4
- rebuilt, no change

* Fri Feb 12 2016 Antonio Murdaca <runcom@fedoraproject.org> - 1:1.10.1-2.git49805e4
- built docker @projectatomic/fedora-1.10.1 commit#49805e4
- built d-s-s commit#1c2b95b
- built docker-selinux commit#b8aae8f
- built docker-utils commit#dab51ac
- built docker-novolume-plugin commit#d1a7f4a
- built docker-v1.10-migrator commit#994c35

* Mon Jan 25 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.9.1-6.git6ec29ef
- Resolves: rhbz#1301198 - do not add distro tag to docker version
- built docker @projectatomic/fedora-1.9 commit#001db93
- built docker-selinux commit#e2e1f22
- built d-s-s commit#1c2b95b
- built docker-utils commit#dab51ac

* Wed Jan 20 2016 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.9.1-5.git6ec29ef
- built docker @projectatomic/fedora-1.9 commit#2f940c1
- built docker-selinux commit#e2e1f22
- built d-s-s commit#1c2b95b
- built docker-utils commit#dab51ac

* Wed Dec 09 2015 Michal Minar <miminar@redhat.com> 1:1.9.1-4.git6ec29ef
- Made it compilable on i686.

* Wed Dec 02 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.9.1-3.git6ec29ef
- built docker @projectatomic/fedora-1.9 commit#6ec29ef
- built docker-selinux commit#441f312
- built d-s-s commit#0814c26
- built docker-utils commit#dab51ac

* Fri Nov 20 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.9.1-2.git78bc3ea
- built docker @projectatomic/fedora-1.9 commit#78bc3ea
- built docker-selinux commit#dbfad05
- built d-s-s commit#0814c26
- built docker-utils commit#dab51ac

* Fri Nov 13 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.8.2-14.git8f9eabc
- built docker @rhatdan/fedora-1.8 commit#8f9eabc
- built docker-selinux commit#dbfad05
- built d-s-s commit#e9722cc
- built docker-utils commit#dab51ac

* Thu Nov 12 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.8.2-13.git28c300f
- built docker @rhatdan/fedora-1.8 commit#28c300f
- built docker-selinux commit#dbfad05
- built d-s-s commit#e9722cc
- built docker-utils commit#dab51ac
- Resolves: rhbz#1273893
- From: Dan Walsh <dwalsh@redhat.com>

* Thu Nov 12 2015 Jakub Čajka <jcajka@fedoraproject.org> - 1:1.8.2-12.git28c300f
- clean up macros overrides

* Thu Nov 05 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.8.2-11.git28c300f
- Dependency changes
- For docker: Requires: docker-selinux
- For docker-selinux: Requires(post): docker
- From: Dusty Mabe <dustymabe@redhat.com>

* Tue Nov 03 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.8.2-10.git28c300f
- Resolves: rhbz#1270521
- built docker @rhatdan/fedora-1.8 commit#28c300f
- built docker-selinux commit#dbfad05
- built d-s-s commit#e9722cc
- built docker-utils commit#dab51ac

* Wed Oct 21 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.8.2-9.gitbdb52b6
- built docker @rhatdan/fedora-1.8 commit#bdb52b6
- built docker-selinux master commit#fe61432
- built d-s-s master commit#01df512
- built docker-utils master commit#dab51ac
- Resolves: rhbz#1273893

* Wed Oct 21 2015 Lokesh Mandvekar <lsm5@fedoraproject.org>
- built docker @rhatdan/fedora-1.8 commit#
- built docker-selinux master commit#fe61432
- built d-s-s master commit#01df512
- built docker-utils master commit#dab51ac

* Mon Oct 12 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.8.2-7.gitcb216be
- built docker @rhatdan/fedora-1.8 commit#cb216be
- built docker-selinux master commit#44abd21
- built d-s-s master commit#6898d43
- built docker-utils master commit#dab51ac

* Mon Oct 12 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.8.2-6.gitcb216be
- built docker @rhatdan/fedora-1.8 commit#cb216be
- built docker-selinux master commit#44abd21
- built d-s-s master commit#6898d43
- built docker-utils master commit#dab51ac

* Mon Sep 21 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.8.2-5.gitcb216be
- built docker-selinux master commit#2ed73eb

* Mon Sep 21 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.8.2-4.gitcb216be
- built docker-selinux master commit#d6560f8

* Wed Sep 16 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.8.2-3.gitcb216be
- built docker @rhatdan/fedora-1.8 commit#cb216be

* Tue Sep 15 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.8.2-2.gitd449443
- built docker @rhatdan/fedora-1.8 commit#d449443
- built d-s-s master commit#6898d43
- built docker-selinux master commit#b5281b7

* Fri Sep 11 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.8.2-1.gitf1db8f2
- built docker @rhatdan/fedora-1.8 commit#f1db8f2
- built d-s-s master commit#6898d43

* Thu Sep 03 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.8.1-3.git32b8b25
- Resolves: rhbz#1259427

* Mon Aug 24 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.8.1-2.git32b8b25
- built docker @rhatdan/ commit#32b8b25
- built d-s-s master commit#d3b9ba7
- built docker-selinux master commit#6267b83
- built docker-utils master commit#dab51ac

* Fri Aug 14 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.8.1-1
- built docker @rhatdan/fedora-1.8 commit#3c1d7c8
- built d-s-s master commit#ac1b30e
- built docker-selinux master commit#16ebd81
- built docker-utils master commit#dab51ac

* Tue Jul 28 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1:1.7.0-22.gitdcff4e1
- release 21 was crap, include epoch for downgrading

* Mon Jul 27 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-21.gitdcff4e1
- docker version downgraded to allow builds for all arches, latest version
doesn't build for non-x86_64
- obsoletes version 1.8.0

* Fri Jul 24 2015 Tomas Radej <tradej@redhat.com> - 1.8.0-6.git5062080
- Updated dep on policycoreutils-python-utils

* Fri Jul 17 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.0-6.git5062080
- package provides: docker-engine

* Thu Jul 02 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.0-6.git5062080
- built docker @lsm5/fedora-1.8 commit#6c23e87
- enable non-x86_64 builds again

* Tue Jun 30 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.0-5.git6d5bfe5
- built docker @lsm5/fedora-1.8 commit#6d5bfe5
- make test-unit and make test-docker-py successful

* Mon Jun 29 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.0-4.git0d8fd7c
- build docker @lsm5/fedora-1.8 commit#0d8fd7c
- disable non-x86_64 for this build
- use same distro as host for running tests
- docker.service Wants docker-storage-setup.service

* Mon Jun 29 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.0-3.gita2f1a81
- built docker @lsm5/fedora commit#a2f1a81

* Sat Jun 27 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.0-2.git1cad29d
- built docker @lsm5/fedora commit#1cad29d

* Fri Jun 26 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.0-1
- New version: 1.8.0, built docker         @lsm5/commit#96ebfd2

* Fri Jun 26 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-21.gitdcff4e1
- build dss master commit#90f4a5f
- build docker-selinux master commit#bebf349
- update manpage build script path

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.0-20.gitdcff4e1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 15 2015 jchaloup <jchaloup@redhat.com> - 1.7.0-19.gitdcff4e1
- Remove docker.initd as it requires /sbin/runtime no packages in Fedora

* Fri Jun 12 2015 jchaloup <jchaloup@redhat.com> - 1.7.0-18.gitdcff4e1
- Add docker-unit-test subpackage for CI testing
- Add with_devel and with_unit_test macros
- Remove devel's runtime deps on golang

* Tue Jun 09 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-17.gitdcff4e1
- Include d-s-s into the main docker package
- Obsolete docker-storage-setup <= 0.5-3

* Mon Jun 08 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-16.gitdcff4e1
- Resolves: rhbz#1229433 - update docker-selinux to commit#99c4c7

* Mon Jun 08 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-15.gitdcff4e1
- disable debuginfo because it breaks docker

* Sun Jun 07 2015 Dennis Gilmore <dennis@ausil.us> - 1.7.0-14.gitdcff4e1
- enable %%{ix86}
- remove vishvananda/netns/netns_linux_amd.go file if %%{ix86} architecture is used

* Fri Jun 05 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-13.gitdcff4e1
- built docker @lsm5/fedora commit#dcff4e1

* Thu Jun 04 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-12.git9910a0c
- built docker @lsm5/fedora commit#9910a0c

* Tue Jun 02 2015 jchaloup <jchaloup@redhat.com> - 1.7.0-11.gita53a6e6
- remove vishvananda/netns/netns_linux_amd.go file if arm architecture is used
- add debug info

* Mon Jun 01 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-10.gita53a6e6
- built docker @lsm5/fedora commit#a53a6e6

* Sat May 30 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-9.git49d9a3f
- built docker @lsm5/fedora commit#49d9a3f

* Fri May 29 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-8.git0d35ceb
- built docker @lsm5/fedora commit#0d35ceb

* Thu May 28 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-7.git6d76e4c
- built docker @rhatdan/fedora-1.7 commit#6d76e4c
- built docker-selinux master commit#e86b2bc

* Fri May 08 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-6.git56481a3
- include distro tag in VERSION

* Thu Apr 30 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-5.git56481a3
- include docker-selinux for centos7 and rhel7

* Thu Apr 30 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-4.git56481a3
- increment release tag to sync with docker-master on centos7

* Thu Apr 30 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-3.git56481a3
- built docker @lsm5/fedora commit#56481a3

* Mon Apr 20 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-2.git50ef691
- built docker @lsm5/fedora commit#50ef691

* Mon Apr 20 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-1
- New version: 1.7.0, built docker         @lsm5/commit#50ef691

* Sat Apr 11 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-33.git1dcc59a
- built docker @lsm5/fedora commit#1dcc59a

* Thu Apr 09 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-32.gitf7125f9
- built docker @lsm5/fedora commit#f7125f9

* Wed Apr 08 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-31.git7091837
- built docker @lsm5/fedora commit#7091837

* Wed Apr 01 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-30.gitece2f2d
- built docker @lsm5/fedora commit#ece2f2d

* Mon Mar 30 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-29.gitc9c16a3
- built docker @lsm5/fedora commit#c9c16a3

* Mon Mar 30 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-28.git39c97c2
- built docker @lsm5/fedora commit#39c97c2

* Sun Mar 29 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-27.git937f8fc
- built docker @lsm5/fedora commit#937f8fc

* Sat Mar 28 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-26.gitbbc21e4
- built docker @lsm5/fedora commit#bbc21e4

* Tue Mar 24 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-25.git5ebfacd
- move selinux post/postun to its own subpackage
- correct docker-selinux min nvr for docker main package

* Tue Mar 24 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-24.git5ebfacd
- docker-selinux shouldn't require docker
- move docker-selinux's post and postun to docker's

* Sun Mar 22 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-23.git5ebfacd
- increment release tag as -22 was already built without conditionals for f23
and docker-selinux
- Source7 only for f23+

* Sun Mar 22 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-22.git5ebfacd
- Rename package to 'docker', metaprovide: docker-io*
- Obsolete docker-io release 21
- no separate version tag for docker-selinux
- docker-selinux only for f23+

* Fri Mar 20 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-21.git5ebfacd
- selinux specific rpm code from Lukas Vrabec <lvrabec@redhat.com>
- use spaces instead of tabs

* Tue Mar 17 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-20.git5ebfacd
- built commit#5ebfacd

* Mon Mar 16 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-19.git5d7adce
- built commit#5d7adce

* Thu Mar 05 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-18.git92e632c
- built commit#92e632c

* Wed Mar 04 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-17.git0f6704f
- built commit#0f6704f

* Tue Mar 03 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-16.git8e107a9
- built commit#8e107a9

* Sun Mar 01 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-15.gita61716e
- built commit#a61716e

* Sat Feb 28 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-14.gitb52a2cf
- built commit#b52a2cf

* Fri Feb 27 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-13.gitf5850e8
- built commit#f5850e8

* Thu Feb 26 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-12.git7e2328b
- built commit#7e2328b

* Wed Feb 25 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-11.git09b785f
- remove add-X-flag.patch
- require selinux-policy >= 3.13.1-114 for fedora >= 23 (RE: rhbz#1195804)

* Mon Feb 23 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-10.git09b785f
- Resolves: rhbz#1195328 - solve build failures by adding -X flag back
also see (https://github.com/docker/docker/issues/9207#issuecomment-75578730)

* Wed Feb 18 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-9.git09b785f
- built commit#09b785f

* Tue Feb 17 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-8.git2243e32
- re-add detailed provides in -devel package
NOTE: (only providing the root path doesn't help in building packages like
kubernetes)

* Tue Feb 17 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-7.git2243e32
- built commit#2243e32

* Tue Feb 17 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-6.git2243e32
- built commit#2243e32

* Sun Feb 15 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-5.git028968f
- built commit#028968f

* Sat Feb 14 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-4.git9456a25
- built commit#9456a25

* Thu Feb 12 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-3.git802802b
- built commit#802802b

* Wed Feb 11 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-2.git54b59c2
- provide golang paths only upto the repo's root dir
- merge pkg-devel into devel

* Wed Feb 11 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-1
- New version: 1.5.0, built commit#54b59c2

* Tue Feb 10 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-27.git76baa35
- daily rebuild - Tue Feb 10 01:19:10 CET 2015

* Mon Feb 09 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-26.gitc03d6f5
- add config variable for insecure registry

* Sat Feb 07 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-25.gitc03d6f5
- daily rebuild - Sat Feb  7 02:53:34 UTC 2015

* Fri Feb 06 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-24.git68b0ed5
- daily rebuild - Fri Feb  6 04:27:54 UTC 2015

* Wed Feb 04 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-23.git7cc9858
- daily rebuild - Wed Feb  4 22:08:05 UTC 2015

* Wed Feb 04 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-22.git165ea5c
- daily rebuild - Wed Feb  4 03:10:41 UTC 2015

* Wed Feb 04 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-21.git165ea5c
- daily rebuild - Wed Feb  4 03:09:20 UTC 2015

* Tue Feb 03 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-20.git662dffe
- Resolves: rhbz#1184266 - enable debugging
- Resolves: rhbz#1190748 - enable core dumps with no size limit

* Tue Feb 03 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-19.git662dffe
- daily rebuild - Tue Feb  3 04:56:36 UTC 2015

* Mon Feb 02 2015 Dennis Gilmore <dennis@ausil.us> 1.4.1-18.git9273040
- enable building on %%{arm}

* Mon Feb 02 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-17.git9273040
- daily rebuild - Mon Feb  2 00:08:17 UTC 2015

* Sun Feb 01 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-16.git01864d3
- daily rebuild - Sun Feb  1 00:00:57 UTC 2015

* Sat Jan 31 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-15.gitd400ac7
- daily rebuild - Sat Jan 31 05:08:46 UTC 2015

* Sat Jan 31 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-14.gitd400ac7
- daily rebuild - Sat Jan 31 05:07:37 UTC 2015

* Thu Jan 29 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-13.gitd400ac7
- daily rebuild - Thu Jan 29 14:13:04 UTC 2015

* Wed Jan 28 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-12.gitde52a19
- daily rebuild - Wed Jan 28 02:17:47 UTC 2015

* Tue Jan 27 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-11.gitacb8e08
- daily rebuild - Tue Jan 27 02:37:34 UTC 2015

* Sun Jan 25 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-10.gitb1f2fde
- daily rebuild - Sun Jan 25 21:44:48 UTC 2015

* Sun Jan 25 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-9
- use vendored sources (not built)

* Fri Jan 23 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-8
- Resolves:rhbz#1185423 - MountFlags=slave in unitfile
- use golang(github.com/coreos/go-systemd/activation)

* Fri Jan 16 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-7
- docker group no longer used or created
- no socket activation
- config file updates to include info about docker_transition_unconfined
boolean

* Fri Jan 16 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-6
- run tests inside a docker repo (doesn't affect koji builds - not built)

* Tue Jan 13 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-5
- Resolves: rhbz#1169593 patch to set DOCKER_CERT_PATH regardless of config file

* Thu Jan 08 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-4
- allow unitfile to use /etc/sysconfig/docker-network
- MountFlags private

* Fri Dec 19 2014 Dan Walsh <dwalsh@redhat.com> - 1.4.1-3
- Add check to run unit tests

* Thu Dec 18 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-2
- update and rename logrotate cron script
- install /etc/sysconfig/docker-network

* Wed Dec 17 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.1-1
- Resolves: rhbz#1175144 - update to upstream v1.4.1
- Resolves: rhbz#1175097, rhbz#1127570 - subpackages
for fish and zsh completion and vim syntax highlighting
- Provide subpackage to run logrotate on running containers as a daily cron
job

* Thu Dec 11 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.0-2
- update metaprovides

* Thu Dec 11 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.4.0-1
- Resolves: rhbz#1173324
- Resolves: rhbz#1172761 - CVE-2014-9356
- Resolves: rhbz#1172782 - CVE-2014-9357
- Resolves: rhbz#1172787 - CVE-2014-9358
- update to upstream v1.4.0
- override DOCKER_CERT_PATH in sysconfig instead of patching the source
- create dockerroot user if doesn't exist prior

* Tue Dec 09 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.2-6.gitbb24f99
- use /etc/docker instead of /.docker
- use upstream master commit bb24f99d741cd8d6a8b882afc929c15c633c39cb
- include DOCKER_TMPDIR variable in /etc/sysconfig/docker

* Mon Dec 08 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.2-5
- Revert to using upstream release 1.3.2

* Tue Dec 02 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.2-4.git353ff40
- Resolves: rhbz#1169151, rhbz#1169334

* Sun Nov 30 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.2-3.git353ff40
- Resolves: rhbz#1169035, rhbz#1169151
- bring back golang deps (except libcontainer)

* Tue Nov 25 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.2-2
- install sources skipped prior

* Tue Nov 25 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.2-1
- Resolves: rhbz#1167642 - Update to upstream v1.3.2
- Resolves: rhbz#1167505, rhbz#1167507 - CVE-2014-6407
- Resolves: rhbz#1167506 - CVE-2014-6408
- use vendor/ dir for golang deps for this NVR (fix deps soon after)

* Wed Nov 19 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.1-3
- Resolves: rhbz#1165615

* Fri Oct 31 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.1-2
- Remove pandoc from build reqs

* Fri Oct 31 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.1-1
- update to v1.3.1

* Mon Oct 20 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.3.0-1
- Resolves: rhbz#1153936 - update to v1.3.0
- don't install zsh files
- iptables=false => ip-masq=false

* Wed Oct 08 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.2.0-5
- Resolves: rhbz#1149882 - systemd unit and socket file updates

* Tue Sep 30 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.2.0-4
- Resolves: rhbz#1139415 - correct path for bash completion
    /usr/share/bash-completion/completions
- versioned provides for docker
- golang versioned requirements for devel and pkg-devel
- remove macros from changelog
- don't own dirs owned by vim, systemd, bash

* Thu Sep 25 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.2.0-3
- Resolves: rhbz#1145660 - support /etc/sysconfig/docker-storage 
  From: Colin Walters <walters@redhat.com>
- patch to ignore selinux if it's disabled
  https://github.com/docker/docker/commit/9e2eb0f1cc3c4ef000e139f1d85a20f0e00971e6
  From: Dan Walsh <dwalsh@redhat.com>

* Sun Aug 24 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.2.0-2
- Provides docker only for f21 and above

* Sat Aug 23 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.2.0-1
- Resolves: rhbz#1132824 - update to v1.2.0

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Aug 01 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.1.2-2
- change conditionals

* Thu Jul 31 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.1.2-1
- Resolves: rhbz#1124036 - update to upstream v1.1.2

* Mon Jul 28 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.0.0-10
- split out the import_path/pkg/... libraries, to avoid cyclic deps with libcontainer

* Thu Jul 24 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.0.0-9
- /etc/sysconfig/docker should be config(noreplace)

* Wed Jul 23 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.0.0-8
- Resolves: rhbz#1119849
- Resolves: rhbz#1119413 - min delta between upstream and packaged unitfiles
- devel package owns directories it creates
- ensure min NVRs used for systemd contain fixes RE: CVE-2014-3499

* Wed Jul 16 2014 Vincent Batts <vbatts@fedoraproject.org> - 1.0.0-7
- clean up gopath
- add Provides for docker libraries
- produce a -devel with docker source libraries
- accomodate golang rpm macros

* Tue Jul 01 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.0.0-6
- Resolves: rhbz#1114810 - CVE-2014-3499 (correct bz#)

* Tue Jul 01 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.0.0-5
- Resolves: rhbz#11114810 - CVE-2014-3499

* Tue Jun 24 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.0.0-4
- Set mode,user,group in docker.socket file

* Sat Jun 14 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.0.0-3
- correct bogus date

* Sat Jun 14 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.0.0-2
- RHBZ#1109533 patch libcontainer for finalize namespace error
- RHBZ#1109039 build with updated golang-github-syndtr-gocapability
- install Dockerfile.5 manpage

* Mon Jun 09 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.0.0-1
- upstream version bump to v1.0.0

* Mon Jun 09 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0.12.0-1
- RHBZ#1105789 Upstream bump to 0.12.0

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.11.1-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Jun 05 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-11
- unitfile should Require socket file (revert change in release 10)

* Fri May 30 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-10
- do not require docker.socket in unitfile

* Thu May 29 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-9
- BZ: change systemd service type to 'notify'

* Thu May 29 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-8
- use systemd socket-activation version

* Thu May 29 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-7
- add "Provides: docker" as per FPC exception (Matthew Miller
        <mattdm@fedoraproject.org>)

* Thu May 29 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-6
- don't use docker.sysconfig meant for sysvinit (just to avoid confusion)

* Thu May 29 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-5
- Bug 1084232 - add /etc/sysconfig/docker for additional args

* Tue May 27 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-4
- patches for BZ 1088125, 1096375

* Fri May 09 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-3
- add selinux buildtag
- enable selinux in unitfile

* Fri May 09 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-2
- get rid of conditionals, separate out spec for each branch

* Thu May 08 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.11.1-1
- Bug 1095616 - upstream bump to 0.11.1
- manpages via pandoc

* Mon Apr 14 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.10.0-2
- regenerate btrfs removal patch
- update commit value

* Mon Apr 14 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.10.0-1
- include manpages from contrib

* Wed Apr 09 2014 Bobby Powers <bobbypowers@gmail.com> - 0.10.0-1
- Upstream version bump

* Thu Mar 27 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.9.1-1
- BZ 1080799 - upstream version bump

* Thu Mar 13 2014 Adam Miller <maxamillion@fedoraproject.org> - 0.9.0-3
- Add lxc requirement for EPEL6 and patch init script to use lxc driver
- Remove tar dep, no longer needed
- Require libcgroup only for EPEL6

* Tue Mar 11 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.9.0-2
- lxc removed (optional)
  http://blog.docker.io/2014/03/docker-0-9-introducing-execution-drivers-and-libcontainer/

* Tue Mar 11 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.9.0-1
- BZ 1074880 - upstream version bump to v0.9.0

* Wed Feb 19 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.8.1-1
- Bug 1066841 - upstream version bump to v0.8.1
- use sysvinit files from upstream contrib
- BR golang >= 1.2-7

* Thu Feb 13 2014 Adam Miller <maxamillion@fedoraproject.org> - 0.8.0-3
- Remove unneeded sysctl settings in initscript
  https://github.com/dotcloud/docker/pull/4125

* Sat Feb 08 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.8.0-2
- ignore btrfs for rhel7 and clones for now
- include vim syntax highlighting from contrib/syntax/vim

* Wed Feb 05 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.8.0-1
- upstream version bump
- don't use btrfs for rhel6 and clones (yet)

* Mon Jan 20 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.6-2
- bridge-utils only for rhel < 7
- discard freespace when image is removed

* Thu Jan 16 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.6-1
- upstream version bump v0.7.6
- built with golang >= 1.2

* Thu Jan 09 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.5-1
- upstream version bump to 0.7.5

* Thu Jan 09 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.4-1
- upstream version bump to 0.7.4 (BZ #1049793)
- udev rules file from upstream contrib
- unit file firewalld not used, description changes

* Mon Jan 06 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.3-3
- udev rules typo fixed (BZ 1048775)

* Sat Jan 04 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.3-2
- missed commit value in release 1, updated now
- upstream release monitoring (BZ 1048441)

* Sat Jan 04 2014 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.3-1
- upstream release bump to v0.7.3

* Thu Dec 19 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.2-2
- require xz to work with ubuntu images (BZ #1045220)

* Wed Dec 18 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.2-1
- upstream release bump to v0.7.2

* Fri Dec 06 2013 Vincent Batts <vbatts@redhat.com> - 0.7.1-1
- upstream release of v0.7.1

* Mon Dec 02 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.0-14
- sysvinit patch corrected (epel only)
- 80-docker.rules unified for udisks1 and udisks2

* Mon Dec 02 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.0-13
- removed firewall-cmd --add-masquerade

* Sat Nov 30 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.0-12
- systemd for fedora >= 18
- firewalld in unit file changed from Requires to Wants
- firewall-cmd --add-masquerade after docker daemon start in unit file
  (Michal Fojtik <mfojtik@redhat.com>), continue if not present (Michael Young
  <m.a.young@durham.ac.uk>)
- 80-docker.rules included for epel too, ENV variables need to be changed for
  udisks1

* Fri Nov 29 2013 Marek Goldmann <mgoldman@redhat.com> - 0.7.0-11
- Redirect docker log to /var/log/docker (epel only)
- Removed the '-b none' parameter from sysconfig, it's unnecessary since
  we create the bridge now automatically (epel only)
- Make sure we have the cgconfig service started before we start docker,
    RHBZ#1034919 (epel only)

* Thu Nov 28 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.0-10
- udev rules added for fedora >= 19 BZ 1034095
- epel testing pending

* Thu Nov 28 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.0-9
- requires and started after firewalld

* Thu Nov 28 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.0-8
- iptables-fix patch corrected

* Thu Nov 28 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.0-7
- use upstream tarball and patch with mgoldman's commit

* Thu Nov 28 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.0-6
- using mgoldman's shortcommit value 0ff9bc1 for package (BZ #1033606)
- https://github.com/dotcloud/docker/pull/2907

* Wed Nov 27 2013 Adam Miller <maxamillion@fedoraproject.org> - 0.7.0-5
- Fix up EL6 preun/postun to not fail on postun scripts

* Wed Nov 27 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7.0-4
- brctl patch for rhel <= 7

* Wed Nov 27 2013 Vincent Batts <vbatts@redhat.com> - 0.7.0-3
- Patch how the bridge network is set up on RHEL (BZ #1035436)

* Wed Nov 27 2013 Vincent Batts <vbatts@redhat.com> - 0.7.0-2
- add libcgroup require (BZ #1034919)

* Tue Nov 26 2013 Marek Goldmann <mgoldman@redhat.com> - 0.7.0-1
- Upstream release 0.7.0
- Using upstream script to build the binary

* Mon Nov 25 2013 Vincent Batts <vbatts@redhat.com> - 0.7-0.20.rc7
- correct the build time defines (bz#1026545). Thanks dan-fedora.

* Fri Nov 22 2013 Adam Miller <maxamillion@fedoraproject.org> - 0.7-0.19.rc7
- Remove xinetd entry, added sysvinit

* Fri Nov 22 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.18.rc7
- rc version bump

* Wed Nov 20 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.17.rc6
- removed ExecStartPost lines from docker.service (BZ #1026045)
- dockerinit listed in files

* Wed Nov 20 2013 Vincent Batts <vbatts@redhat.com> - 0.7-0.16.rc6
- adding back the none bridge patch

* Wed Nov 20 2013 Vincent Batts <vbatts@redhat.com> - 0.7-0.15.rc6
- update docker source to crosbymichael/0.7.0-rc6
- bridge-patch is not needed on this branch

* Tue Nov 19 2013 Vincent Batts <vbatts@redhat.com> - 0.7-0.14.rc5
- update docker source to crosbymichael/0.7-rc5
- update docker source to 457375ea370a2da0df301d35b1aaa8f5964dabfe
- static magic
- place dockerinit in a libexec
- add sqlite dependency

* Sat Nov 02 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.13.dm
- docker.service file sets iptables rules to allow container networking, this
    is a stopgap approach, relevant pull request here:
    https://github.com/dotcloud/docker/pull/2527

* Sat Oct 26 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.12.dm
- dm branch
- dockerinit -> docker-init

* Tue Oct 22 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.11.rc4
- passing version information for docker build BZ #1017186

* Sat Oct 19 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.10.rc4
- rc version bump
- docker-init -> dockerinit
- zsh completion script installed to /usr/share/zsh/site-functions

* Fri Oct 18 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.9.rc3
- lxc-docker version matches package version

* Fri Oct 18 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.8.rc3
- double quotes removed from buildrequires as per existing golang rules

* Fri Oct 11 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.7.rc3
- xinetd file renamed to docker.xinetd for clarity

* Thu Oct 10 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.6.rc3
- patched for el6 to use sphinx-1.0-build

* Wed Oct 09 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.5.rc3
- rc3 version bump
- exclusivearch x86_64

* Wed Oct 09 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.4.rc2
- debuginfo not Go-ready yet, skipped

* Wed Oct 09 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-0.3.rc2
- debuginfo package generated
- buildrequires listed with versions where needed
- conditionals changed to reflect systemd or not
- docker commit value not needed
- versioned provides lxc-docker

* Mon Oct 07 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-2.rc2
- rc branch includes devmapper
- el6 BZ #1015865 fix included

* Sun Oct 06 2013 Lokesh Mandvekar <lsm5@redhat.com> - 0.7-1
- version bump, includes devicemapper
- epel conditionals included
- buildrequires sqlite-devel

* Fri Oct 04 2013 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0.6.3-4.devicemapper
- docker-io service enables IPv4 and IPv6 forwarding
- docker user not needed
- golang not supported on ppc64, docker-io excluded too

* Thu Oct 03 2013 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0.6.3-3.devicemapper
- Docker rebuilt with latest kr/pty, first run issue solved

* Fri Sep 27 2013 Marek Goldmann <mgoldman@redhat.com> - 0.6.3-2.devicemapper
- Remove setfcap from lxc.cap.drop to make setxattr() calls working in the
  containers, RHBZ#1012952

* Thu Sep 26 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.3-1.devicemapper
- version bump
- new version solves docker push issues

* Tue Sep 24 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.2-14.devicemapper
- package requires lxc

* Tue Sep 24 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.2-13.devicemapper
- package requires tar

* Tue Sep 24 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.2-12.devicemapper
- /var/lib/docker installed
- package also provides lxc-docker

* Mon Sep 23 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.2-11.devicemapper
- better looking url

* Mon Sep 23 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.2-10.devicemapper
- release tag changed to denote devicemapper patch

* Mon Sep 23 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.2-9
- device-mapper-devel is a buildrequires for alex's code
- docker.service listed as a separate source file

* Sun Sep 22 2013 Matthew Miller <mattdm@fedoraproject.org> 0.6.2-8
- install bash completion
- use -v for go build to show progress

* Sun Sep 22 2013 Matthew Miller <mattdm@fedoraproject.org> 0.6.2-7
- build and install separate docker-init

* Sun Sep 22 2013 Matthew Miller <mattdm@fedoraproject.org> 0.6.2-4
- update to use new source-only golang lib packages

* Sat Sep 21 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.2-3
- man page generation from docs/.
- systemd service file created
- dotcloud/tar no longer required

* Fri Sep 20 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.2-2
- patched with alex larsson's devmapper code

* Wed Sep 18 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.2-1
- Version bump

* Tue Sep 10 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.1-2
- buildrequires updated
- package renamed to docker-io

* Fri Aug 30 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.6.1-1
- Version bump
- Package name change from lxc-docker to docker
- Makefile patched from 0.5.3

* Wed Aug 28 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.5.3-5
- File permissions settings included

* Wed Aug 28 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.5.3-4
- Credits in changelog modified as per reference's request

* Tue Aug 27 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.5.3-3
- Dependencies listed as rpm packages instead of tars
- Install section added

* Mon Aug 26 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.5.3-2
- Github packaging
- Deps not downloaded at build time courtesy Elan Ruusamäe
- Manpage and other docs installed

* Fri Aug 23 2013 Lokesh Mandvekar <lsm5@redhat.com> 0.5.3-1
- Initial fedora package
- Some credit to Elan Ruusamäe (glen@pld-linux.org)
