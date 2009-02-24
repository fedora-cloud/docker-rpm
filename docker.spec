Name:           docker
Version:        1.5
Release:        4%{?dist}
Summary:        KDE and GNOME2 system tray replacement docking application

Group:          User Interface/X
License:        GPL+
URL:            http://icculus.org/openbox/2/docker/
Source0:        http://icculus.org/openbox/2/docker/docker-1.5.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)


BuildRequires:  glib2-devel
BuildRequires:  libX11-devel

%description
Docker is a docking application (WindowMaker dock app) which acts as a system
tray for KDE and GNOME2. It can be used to replace the panel in either
environment, allowing you to have a system tray without running the KDE/GNOME
panel or environment.

%prep
%setup -q


%build
make %{?_smp_mflags} CFLAGS="${RPM_OPT_FLAGS}" XLIBPATH=%{_libdir}/X11


%install
rm -rf $RPM_BUILD_ROOT
mkdir -p ${RPM_BUILD_ROOT}/%{_bindir}
make install PREFIX=${RPM_BUILD_ROOT}/%{_prefix}


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc README COPYING
%{_bindir}/docker


%changelog
* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 11 2008 Andreas Bierfert <andreas.bierfert[AT]lowlatency.de> - 1.5-3
- Rebuilt for gcc43

* Mon Oct 15 2007 Andreas Bierfert <andreas.bierfert[AT]lowlatency.de>
- 1.5-2
- add new license tag

* Sat Jun 02 2007 Andreas Bierfert <andreas.bierfert[AT]lowlatency.de>
- 1.5-1
- initial version
