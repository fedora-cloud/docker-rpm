%global with_devel 1
%global with_unit_test 1

# modifying the dockerinit binary breaks the SHA1 sum check by docker
%global __os_install_post %{_rpmconfigdir}/brp-compress

# docker builds in a checksum of dockerinit into docker,
# so stripping the binaries breaks docker
%global debug_package %{nil}
%global provider github
%global provider_tld com
%global project docker
%global repo %{project}

%global import_path %{provider}.%{provider_tld}/%{project}/%{repo}

# docker stuff (prefix with d_)
%global d_commit cb216bee4d723fe967345a2b11a02cd7d7d2fdd5
%global d_shortcommit %(c=%{d_commit}; echo ${c:0:7})
%global d_dist %(echo %{?dist} | sed 's/./-/')

# d-s-s stuff (prefix with dss_)
%global dss_libdir %{_prefix}/lib/%{repo}-storage-setup
%global dss_commit 6898d433f7c7666475656ab89565ec02d08c4c55
%global dss_shortcommit %(c=%{dss_commit}; echo ${c:0:7})

%global utils_commit dab51acd1b1a77f7cb01a1b7e2129ec85c846b71

# docker-selinux conditional
%if 0%{?fedora} >= 22 || 0%{?centos} >= 7 || 0%{?rhel} >= 7
%global with_selinux 1
%endif

%if 0%{?with_selinux}
# docker-selinux stuff (prefix with ds_ for version/release etc.)
# Some bits borrowed from the openstack-selinux package
%global ds_commit 2ed73eb5066f2a4e0e7fa84c260816d754433bc6
%global ds_shortcommit %(c=%{ds_commit}; echo ${c:0:7})
%global selinuxtype targeted
%global moduletype services
%global modulenames %{repo}

# Usage: _format var format
# Expand 'modulenames' into various formats as needed
# Format must contain '$x' somewhere to do anything useful
%global _format() export %1=""; for x in %{modulenames}; do %1+=%2; %1+=" "; done;

# Relabel files
%global relabel_files() %{_sbindir}/restorecon -R %{_bindir}/%{repo} %{_localstatedir}/run/%{repo}.sock %{_localstatedir}/run/%{repo}.pid %{_sysconfdir}/%{repo} %{_localstatedir}/log/%{repo} %{_localstatedir}/log/lxc %{_localstatedir}/lock/lxc %{_unitdir}/%{repo}.service %{_sysconfdir}/%{repo} &> /dev/null || :

# Version of SELinux we were using
%if 0%{?fedora} >= 22
%global selinux_policyver 3.13.1-119
%else
%global selinux_policyver 3.13.1-23
%endif
%endif # with_selinux

Name: %{repo}
Version: 1.8.2
Release: 6.git%{d_shortcommit}%{?dist}
Summary: Automates deployment of containerized applications
License: ASL 2.0
URL: http://www.%{repo}.com
ExclusiveArch: %{arm} %{ix86} x86_64
# Branch used: https://github.com/rhatdan/docker/commits/fedora-1.7
Source0: https://github.com/rhatdan/%{repo}/archive/%{d_commit}/%{repo}-%{d_shortcommit}.tar.gz
Source1: %{repo}.service
Source2: %{repo}.sysconfig
Source3: %{repo}-storage.sysconfig
Source4: %{repo}-logrotate.sh
Source5: README.%{repo}-logrotate
Source6: %{repo}-network.sysconfig

%if 0%{?with_selinux}
Source7: https://github.com/fedora-cloud/%{repo}-selinux/archive/%{ds_commit}/%{repo}-selinux-%{ds_shortcommit}.tar.gz
%endif # with_selinux
# Source8 is the source tarball for docker-storage-setup
Source8: https://github.com/projectatomic/%{repo}-storage-setup/archive/%{dss_commit}/%{repo}-storage-setup-%{dss_shortcommit}.tar.gz
# Source9 is the source tarball for docker-utils
Source9: https://github.com/vbatts/%{repo}-utils/archive/%{utils_commit}.tar.gz
Patch0: dev-setup.patch
Patch1: dev-dont-modify.patch
BuildRequires: git
BuildRequires: glibc-static
BuildRequires: golang >= 1.4.2
BuildRequires: go-md2man
BuildRequires: device-mapper-devel
BuildRequires: btrfs-progs-devel
BuildRequires: sqlite-devel
BuildRequires: pkgconfig(systemd)
%if 0%{?fedora} >= 21
# Resolves: rhbz#1165615
Requires: device-mapper-libs >= 1.02.90-1
%endif

# RE: rhbz#1195804 - ensure min NVR for selinux-policy
%if 0%{?with_selinux}
Requires: selinux-policy >= %{selinux_policyver}
Requires(pre): %{repo}-selinux >= %{version}-%{release}
%endif # with_selinux

# Resolves: rhbz#1045220
Requires: xz
Provides: lxc-%{repo} = %{version}-%{release}

# Match with upstream name
Provides: %{repo}-engine = %{version}-%{release}

# needs tar to be able to run containers
Requires: tar

# permitted by https://fedorahosted.org/fpc/ticket/341#comment:7
# In F22, the whole package should be renamed to be just "docker" and
# this changed to "Provides: docker-io".
%if 0%{?fedora} >= 22
Provides: %{repo}-io = %{version}-%{release}
Obsoletes: %{repo}-io < %{version}-21
%endif

# include d-s-s into main docker package and obsolete existing d-s-s rpm
# also update BRs and Rs
Requires: lvm2
Requires: xfsprogs
Obsoletes: %{repo}-storage-setup <= 0.5-3

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
Provides: golang(%{import_path}/contrib/docker-device-tool) = %{version}-%{release}
Provides: golang(%{import_path}/contrib/httpserver) = %{version}-%{release}
Provides: golang(%{import_path}/contrib/host-integration) = %{version}-%{release}
Provides: golang(%{import_path}/docker) = %{version}-%{release}
Provides: golang(%{import_path}/dockerinit) = %{version}-%{release}
Provides: golang(%{import_path}/api) = %{version}-%{release}
Provides: golang(%{import_path}/api/server) = %{version}-%{release}
Provides: golang(%{import_path}/api/client) = %{version}-%{release}
Provides: golang(%{import_path}/api/types) = %{version}-%{release}
Provides: golang(%{import_path}/links) = %{version}-%{release}
Provides: golang(%{import_path}/utils) = %{version}-%{release}
Provides: golang(%{import_path}/daemon) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/graphdriver) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/graphdriver/graphtest) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/graphdriver/btrfs) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/graphdriver/devmapper) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/graphdriver/aufs) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/graphdriver/overlay) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/graphdriver/vfs) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/logger) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/logger/syslog) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/logger/jsonfilelog) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/networkdriver) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/networkdriver/ipallocator) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/networkdriver/portmapper) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/networkdriver/bridge) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/networkdriver/portallocator) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/execdriver) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/execdriver/lxc) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/execdriver/execdrivers) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/execdriver/native) = %{version}-%{release}
Provides: golang(%{import_path}/daemon/execdriver/native/template) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/ioutils) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/fileutils) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/version) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/signal) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/units) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/pools) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/tarsum) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/tailfile) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/pubsub) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/progressreader) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/stdcopy) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/broadcastwriter) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/parsers) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/parsers/kernel) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/parsers/filters) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/parsers/operatingsystem) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/proxy) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/ulimit) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/system) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/jsonlog) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/mflag) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/mflag/example) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/timeoutconn) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/graphdb) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/timeutils) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/term) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/term/winconsole) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/networkfs/resolvconf) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/networkfs/etchosts) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/listenbuffer) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/httputils) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/iptables) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/directory) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/archive) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/namesgenerator) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/systemd) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/common) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/mount) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/testutils) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/promise) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/truncindex) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/sysinfo) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/homedir) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/reexec) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/symlink) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/chrootarchive) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/devicemapper) = %{version}-%{release}
Provides: golang(%{import_path}/pkg/urlutil) = %{version}-%{release}
Provides: golang(%{import_path}/engine) = %{version}-%{release}
Provides: golang(%{import_path}/nat) = %{version}-%{release}
Provides: golang(%{import_path}/volumes) = %{version}-%{release}
Provides: golang(%{import_path}/registry) = %{version}-%{release}
Provides: golang(%{import_path}/registry/v2) = %{version}-%{release}
Provides: golang(%{import_path}/integration) = %{version}-%{release}
Provides: golang(%{import_path}/trust) = %{version}-%{release}
Provides: golang(%{import_path}/runconfig) = %{version}-%{release}
Provides: golang(%{import_path}/graph) = %{version}-%{release}
Provides: golang(%{import_path}/builder) = %{version}-%{release}
Provides: golang(%{import_path}/builder/parser) = %{version}-%{release}
Provides: golang(%{import_path}/builder/parser/dumper) = %{version}-%{release}
Provides: golang(%{import_path}/builder/command) = %{version}-%{release}
Provides: golang(%{import_path}/builtins) = %{version}-%{release}
Provides: golang(%{import_path}/integration-cli) = %{version}-%{release}
Provides: golang(%{import_path}/image) = %{version}-%{release}
Provides: golang(%{import_path}/events) = %{version}-%{release}
Provides: golang(%{import_path}/opts) = %{version}-%{release}

%description devel
%{summary}

This package provides the source libraries for Docker.
%endif # with_devel

%package utils
Summary: External utilities for the %{repo} experience

%description utils
%{summary}

%if 0%{?with_unit_test}
%package unit-test
Summary: %{summary} - for running unit tests

%description unit-test
%{summary} - for running unit tests
%endif # with_unit_test

%package fish-completion
Summary: fish completion files for Docker
Requires: %{repo} = %{version}-%{release}
Requires: fish
Provides: %{repo}-io-fish-completion = %{version}-%{release}

%description fish-completion
This package installs %{summary}.

%package logrotate
Summary: cron job to run logrotate on Docker containers
Requires: %{repo} = %{version}-%{release}
Provides: %{repo}-io-logrotate = %{version}-%{release}

%description logrotate
This package installs %{summary}. logrotate is assumed to be installed on
containers for this to work, failures are silently ignored.

%if 0%{?with_selinux}
%package selinux
Summary: SELinux policies for Docker
BuildRequires: selinux-policy
BuildRequires: selinux-policy-devel
Requires(post): selinux-policy-base >= %{selinux_policyver}
Requires(post): selinux-policy-targeted >= %{selinux_policyver}
Requires(post): policycoreutils
Requires(post): policycoreutils-python
Requires(post): libselinux-utils
Provides: %{repo}-io-selinux

%description selinux
SELinux policy modules for use with Docker.
%endif # with_selinux

%package vim
Summary: vim syntax highlighting files for Docker
Requires: %{repo} = %{version}-%{release}
Requires: vim
Provides: %{repo}-io-vim = %{version}-%{release}

%description vim
This package installs %{summary}.

%package zsh-completion
Summary: zsh completion files for Docker
Requires: %{repo} = %{version}-%{release}
Requires: zsh
Provides: %{repo}-io-zsh-completion = %{version}-%{release}

%description zsh-completion
This package installs %{summary}.

%prep
%setup -q -n %{repo}-%{d_commit}
%patch0 -p1
pushd vendor/src/github.com/opencontainers/runc
%patch1 -p1
popd
cp %{SOURCE5} .
sed -i 's/$/%{d_dist}/' VERSION

# untar d-s-s
tar zxf %{SOURCE8}

# untar %{repo}-utils
tar zxf %{SOURCE9}

%if 0%{?with_selinux}
# unpack %{repo}-selinux
tar zxf %{SOURCE7}
%endif # with_selinux

%build
# set up temporary build gopath, and put our directory there
mkdir _build
pushd _build
mkdir -p src/%{provider}.%{provider_tld}/{%{repo},vbatts}
ln -s $(dirs +1 -l) src/%{import_path}
ln -s $(dirs +1 -l)/%{repo}-utils-%{utils_commit} src/%{provider}.%{provider_tld}/vbatts/%{repo}-utils
popd

export DOCKER_GITCOMMIT="%{d_shortcommit}/%{version}"
export DOCKER_BUILDTAGS="selinux btrfs_noversion"
export GOPATH=$(pwd)/_build:$(pwd)/vendor:%{gopath}

DEBUG=1 hack/make.sh dynbinary
man/md2man-all.sh
cp contrib/syntax/vim/LICENSE LICENSE-vim-syntax
cp contrib/syntax/vim/README.md README-vim-syntax.md

pushd $(pwd)/_build/src
go build github.com/vbatts/%{repo}-utils/cmd/%{repo}-fetch
go build github.com/vbatts/%{repo}-utils/cmd/%{repo}tarsum
popd

%if 0%{?with_selinux}
# build %{repo}-selinux
pushd %{repo}-selinux-%{ds_commit}
make SHARE="%{_datadir}" TARGETS="%{modulenames}"
popd
%endif # with_selinux

%install
# install binary
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_libexecdir}/%{repo}

# install utils
install -p -m 755 _build/src/%{repo}-fetch %{buildroot}%{_bindir}
install -p -m 755 _build/src/%{repo}tarsum %{buildroot}%{_bindir}

# Grab the first thing from -dev
for x in bundles/latest; do \
  install -p -m 755 $x/dynbinary/%{repo}-%{version}%{d_dist} %{buildroot}%{_bindir}/%{repo}
  install -p -m 755 $x/dynbinary/%{repo}init-%{version}%{d_dist} %{buildroot}%{_libexecdir}/%{repo}/%{repo}init
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
install -p -m 755 %{SOURCE4} %{buildroot}%{_sysconfdir}/cron.daily/%{repo}-logrotate

# install vim syntax highlighting
install -d %{buildroot}%{_datadir}/vim/vimfiles/{doc,ftdetect,syntax}
install -p -m 644 contrib/syntax/vim/doc/%{repo}file.txt %{buildroot}%{_datadir}/vim/vimfiles/doc
install -p -m 644 contrib/syntax/vim/ftdetect/%{repo}file.vim %{buildroot}%{_datadir}/vim/vimfiles/ftdetect
install -p -m 644 contrib/syntax/vim/syntax/%{repo}file.vim %{buildroot}%{_datadir}/vim/vimfiles/syntax

# install zsh completion
install -d %{buildroot}%{_datadir}/zsh/site-functions
install -p -m 644 contrib/completion/zsh/_%{repo} %{buildroot}%{_datadir}/zsh/site-functions

# install udev rules
install -d %{buildroot}%{_sysconfdir}/udev/rules.d
install -p contrib/udev/80-%{repo}.rules %{buildroot}%{_sysconfdir}/udev/rules.d

# install storage dir
install -d %{buildroot}%{_sharedstatedir}/%{repo}

# install systemd/init scripts
install -d %{buildroot}%{_unitdir}
install -p -m 644 %{SOURCE1} %{buildroot}%{_unitdir}

# for additional args
install -d %{buildroot}%{_sysconfdir}/sysconfig/
install -p -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/%{repo}
install -p -m 644 %{SOURCE6} %{buildroot}%{_sysconfdir}/sysconfig/%{repo}-network
install -p -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/%{repo}-storage

%if 0%{?with_selinux}
# install SELinux interfaces
%_format INTERFACES $x.if
install -d %{buildroot}%{_datadir}/selinux/devel/include/%{moduletype}
install -p -m 644 %{repo}-selinux-%{ds_commit}/$INTERFACES %{buildroot}%{_datadir}/selinux/devel/include/%{moduletype}

# install policy modules
%_format MODULES $x.pp.bz2
install -d %{buildroot}%{_datadir}/selinux/packages
install -m 0644 %{repo}-selinux-%{ds_commit}/$MODULES %{buildroot}%{_datadir}/selinux/packages
%endif # with_selinux

%if 0%{?with_unit_test}
install -d -m 0755 %{buildroot}%{_sharedstatedir}/docker-unit-test/
cp -pav VERSION Dockerfile %{buildroot}%{_sharedstatedir}/docker-unit-test/.
for d in */ ; do
  cp -rpav $d %{buildroot}%{_sharedstatedir}/docker-unit-test/
done
# remove docker.initd as it requires /sbin/runtime no packages in Fedora
rm -rf %{buildroot}%{_sharedstatedir}/docker-unit-test/contrib/init/openrc/docker.initd
%endif # with_unit_test

%if 0%{?with_devel}
# sources
install -d -p %{buildroot}%{gopath}/src/%{import_path}
rm -rf pkg/symlink/testdata

# remove dirs that won't be installed in devel
rm -rf vendor docs _build bundles contrib/init hack project

# install sources to devel
for dir in */ ; do
    cp -rpav $dir %{buildroot}/%{gopath}/src/%{import_path}/
done
%endif # with_devel

# remove %{repo}-selinux rpm spec file
rm -rf %{repo}-selinux-%{ds_commit}/%{repo}-selinux.spec

# install %{repo} config directory
install -dp %{buildroot}%{_sysconfdir}/%{repo}

# install d-s-s
pushd %{repo}-storage-setup-%{dss_commit}
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

%check
[ ! -w /run/%{repo}.sock ] || {
    mkdir test_dir
    pushd test_dir
    git clone https://github.com/lsm5/docker.git -b fedora-1.8
    pushd %{repo}
    make test
    popd
    popd
}

%pre
getent passwd %{repo}root > /dev/null || %{_sbindir}/useradd -r \
           -d %{_sharedstatedir}/%{repo} -s /sbin/nologin \
           -c "Docker User" %{repo}root
exit 0

%post
%systemd_post %{repo}

%if 0%{?with_selinux}
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
	retorecon -R %{_sharedstatedir}/%{repo}
    fi
fi
%endif # with_selinux

%preun
%systemd_preun %{repo}

%postun
%systemd_postun_with_restart %{repo}

%if 0%{?with_selinux}
%postun selinux
if [ $1 -eq 0 ]; then
%{_sbindir}/semodule -n -r %{modulenames} &> /dev/null || :
if %{_sbindir}/selinuxenabled ; then
%{_sbindir}/load_policy
%relabel_files
fi
fi
%endif # with_selinux

%files
%doc AUTHORS CHANGELOG.md CONTRIBUTING.md LICENSE MAINTAINERS NOTICE README.md 
%doc LICENSE-vim-syntax README-vim-syntax.md
%config(noreplace) %{_sysconfdir}/sysconfig/%{repo}
%config(noreplace) %{_sysconfdir}/sysconfig/%{repo}-network
%config(noreplace) %{_sysconfdir}/sysconfig/%{repo}-storage
%{_mandir}/man1/%{repo}*.1.gz
%{_mandir}/man5/Dockerfile.5.gz
%{_bindir}/%{repo}
%{_libexecdir}/%{repo}
%{_unitdir}/%{repo}.service
%{_datadir}/bash-completion/completions/%{repo}
%dir %{_sharedstatedir}/%{repo}
%{_sysconfdir}/udev/rules.d/80-%{repo}.rules
%{_sysconfdir}/%{repo}
# d-s-s specific
%config(noreplace) %{_sysconfdir}/sysconfig/%{repo}-storage-setup
%{_unitdir}/%{repo}-storage-setup.service
%{_bindir}/%{repo}-storage-setup
%{dss_libdir}/%{repo}-storage-setup
%{dss_libdir}/libdss.sh

%if 0%{?with_devel}
%files devel
%doc AUTHORS CHANGELOG.md CONTRIBUTING.md LICENSE MAINTAINERS NOTICE README.md 
%dir %{gopath}/src/%{provider}.%{provider_tld}/%{project}
%{gopath}/src/%{import_path}
%endif # with_devel

%if 0%{?with_unit_test}
%files unit-test
%{_sharedstatedir}/docker-unit-test/
%endif # with_unit_test

%files fish-completion
%dir %{_datadir}/fish/vendor_completions.d/
%{_datadir}/fish/vendor_completions.d/%{repo}.fish

%files logrotate
%doc README.%{repo}-logrotate
%{_sysconfdir}/cron.daily/%{repo}-logrotate

%if 0%{?with_selinux}
%files selinux
%doc %{repo}-selinux-%{ds_commit}/README.md
%{_datadir}/selinux/*
%endif # with_selinux

%files vim
%{_datadir}/vim/vimfiles/doc/%{repo}file.txt
%{_datadir}/vim/vimfiles/ftdetect/%{repo}file.vim
%{_datadir}/vim/vimfiles/syntax/%{repo}file.vim

%files zsh-completion
%{_datadir}/zsh/site-functions/_%{repo}

%files utils
%{_bindir}/%{repo}-fetch
%{_bindir}/%{repo}tarsum

%changelog
* Thu Oct 01 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.2-6.gitcb216be
- built docker @rhatdan/fedora-1.8 commit#cb216be
- built docker-selinux master commit#2ed73eb
- built d-s-s master commit#6898d43
- built docker-utils master commit#dab51ac

* Thu Oct 01 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.2-6.gitcb216be
- Resolves: rhbz#1267975

* Thu Oct 01 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.2-5.gitcb216be
- built docker @rhatdan/fedora-1.8 commit#cb216be
- built docker-selinux master commit#2ed73eb
- built d-s-s master commit#6898d43
- built docker-utils master commit#dab51ac

* Mon Sep 21 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.2-4.gitcb216be
- build docker @rhatdan/fedora-1.8 commit#cb216be
- built docker-selinux master commit#d6560f8

* Tue Sep 15 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.2-3.gitd449443
- built docker @rhatdan/fedora-1.8 commit#d449443
- revert to BR: golang >= 1.4.2

* Mon Sep 14 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.2-2.gitf1db8f2
- BR: golang < 1.5 until https://github.com/docker/docker/pull/15703

* Fri Sep 11 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.2-1.gitf1db8f2
- built docker @rhatdan/fedora-1.8 commit#f1d8f2
- built d-s-s master commit#6898d43

* Mon Aug 24 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.1-3.git32b8b25
- built docker @rhatdan/ commit#32b8b25
- built d-s-s master commit#d3b9ba7
- built docker-selinux master commit#6267b83
- built docker-utils master commit#dab51ac

* Fri Aug 14 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.1-2.git3c1d7c8
- built docker @rhatdan/fedora-1.8 commit#3c1d7c8
- built d-s-s master commit#ac1b30e
- built docker-selinux master commit#16ebd81
- built docker-utils master commit#dab51ac

* Thu Aug 13 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.1-1
- built docker @rhatdan/fedora-1.8 commit#9281dc3
- built d-s-s master commit#ac1b30e
- built docker-selinux master commit#16ebd81
- built docker-utils master commit#dab51ac

* Tue Aug 11 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.1-8.gitb6416b7
- revert to what existed in 1.7.1-1 (temp fix for rhbz#1252168)

* Tue Aug 04 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.1-7.gitd5a81b3
- built docker @rhatdan/fedora-1.7 commit#d5a81b3
- built d-s-s master commit#b152398
- built docker-selinux master commit#16ebd81

* Fri Jul 24 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.1-6.git33de319
- Resolves: rhbz#1235076
- built docker @rhatdan/fedora-1.7 commit#33de319
- built d-s-s master commit#b152398
- built docker-selinux master commit#bebf349

* Wed Jul 22 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.1-5.gitc8962ac
- Resolves: rhbz#1244124
- built docker @rhatdan/fedora-1.7 commit#c8962ac

* Wed Jul 22 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.1-4.gitcc60fc3
- revert original d-s-s config location
- d-s-s config in /etc/sysconfig is empty by default

* Wed Jul 22 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.1-3.gitcc60fc3
- move d-s-s sysconfig file to /etc/sysconfig
- correct previous 2 changelog dates

* Wed Jul 22 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.1-2.gitcc60fc3
- built docker @rhatdan/fedora-1.7 commit#cc60fc3
- built d-s-s master commit#7cf73dd
- built docker-selinux master commit#bebf349

* Fri Jul 17 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.1-1.gitb6416b7
- package provides: docker-engine

* Wed Jul 15 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.1-1.gitb6416b7
- built docker @rhatdan/fedora-1.7 commit#b6416b7
- v1.7.1 + RH patches

* Tue Jul 14 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-8.git7461f04
- built docker @rhatdan/fedora-1.7 commit#7461f04
- built docker-selinux master commit#bebf349
- built d-s-s master commit#7cf73dd

* Thu Jul 09 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-7.gita2cd872
- built docker @rhatdan/fedora-1.7 commit#a2cd872

* Thu Jul 02 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-6.git74e7a7a
- build docker @lsm5/fedora-1.7 commit#74e7a7a
- Resolves: upstream gh#13649

* Wed Jul 01 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-5.git04d5c0c
- revert to 1.7.0 from 1.8.0
- built docker @lsm5/fedora-1.7 commit#04d5c0c
- build d-s-s master commit#e9c3a4c

* Mon Jun 29 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.8.0-1.git0d8fd7c
- built @lsm5/fedora-1.8 commit#0d8fd7c
- update docker-selinux and dss to latest master commits
- include with_unit_test and with_devel macros from rawhide spec
- disable non-x86_64 for this build (failures with seccomp patches)

* Tue Jun 09 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-4.gitdcff4e1
- Include d-s-s into the main docker package
- Obsolete docker-storage-setup <= 0.5-3
- Resolves: rhbz#1229828

* Mon Jun 08 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-3.git5b82e1d
- BR golang-1.4.2 or greater
- remove netns_linux_amd.go for x86_64

* Tue Jun 02 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-2.git5b82e1d
- build docker rhatdan/fedora-1.7 commit#5b82e1d
- build docker-selinux commit#99c4c77

* Mon Jun 01 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.7.0-1.gita53a6e6
- built docker @lsm5/fedora commit#a53a6e6
- modify docker-selinux condition

* Tue May 05 2015 Michal Minar <miminar@redhat.com> - 1.6.0-3.git9d26a07
- Resolves: bz#1217987 - fix unqualified push

* Wed Apr 22 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.6.0-2.git9d26a07
- build @rhatdan/fedora-1.6 commit#9d26a07 with registry patch fixes

* Thu Apr 16 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.6.0-1.git0591dce
- build @rhatdan/fedora-1.6 commit#0591dce (1.6.0 + rh patches)

* Thu Apr 16 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.6.0-0.3.rc7
- build @rhatdan/fedora-1.6 commit#bc73604

* Tue Apr 14 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.6.0-0.2.rc6
- build @rhatdan/fedora-1.6 commit#b27feb4
- moved GOTRACEBACK=crash to unitfile

* Mon Apr 06 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.6.0-0.1.rc5
- use 1.6.0-rc5

* Tue Mar 31 2015 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.5.0-26.git8150fb6
- use docker rhatdan/1.6 branch (1.6.0 rc with fedora patches)

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
