%define minetest_version 0.4.15
AutoReqProv: no
%define __find_requires true
%define __find_provides true

Name:		minetest
Version:	%{minetest_version}
Release:	1%{?dist}
Summary:	Multiplayer infinite-world block sandbox with survival mode

Group:		Amusements/Games
License:	GPLv2+
URL:		http://celeron.55.lt/minetest/		

Source0:	https://github.com/minetest/minetest/archive/%{minetest_version}.tar.gz#/minetest-%{minetest_version}.tar.gz
Source1:	%{name}.desktop
Source2:	%{name}.service
Source3:	%{name}.rsyslog
Source4:	%{name}.logrotate
Source5:        json-CMakeLists.txt

BuildRequires:	cmake >= 2.6.0
BuildRequires:  gcc-c++
BuildRequires:  libvorbis-devel
BuildRequires:	irrlicht-devel libvorbis-devel openal-soft-devel 
BuildRequires:	bzip2-devel gettext-devel
#buildRequires: jthread-devel
BuildRequires:  sqlite-devel
BuildRequires:	libpng-devel libjpeg-turbo-devel libXxf86vm mesa-libGL-devel
BuildRequires:	desktop-file-utils
BuildRequires:	systemd-units

Requires:	minetest-server = %{version}-%{release}
Requires:	hicolor-icon-theme

%description 
Game of mining, crafting and building in the infinite world of cubic
blocks with optional hostile creatures. Features both single and the
network multiplayer mode. There are no in-game sounds yet


%package	server
Summary:	Minetest multiplayer server
Group:		Amusements/Games
Requires(pre):		shadow-utils gmp-devel
Requires(post):		systemd-units
Requires(preun):	systemd-units
Requires(postun):	systemd-units

%description	server
Minetest multiplayer server. This package does not require X Window System


%package        server-data
Summary:        Mintest multiplayer server stand-alone data package
Group:          Amusements/Games
Conflicts:      minetest
Requires:	minetest-server = %{version}-%{release}

%description    server-data
Minetest multiplayer server runtime data.  

%prep
%setup -q -n minetest-%{minetest_version}
cp %{SOURCE5} src/jsoncpp/json/CMakeLists.txt

%build
%cmake -DBUILD_CLIENT=true -DBUILD_SERVER=true -DMAKE_BUILD_TYPE=Release -DENABLE_SYSTEM_GMP=true
#-DJTHREAD_INCLUDE_DIR=%{_includedir}/jthread .
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

# Put icon in the new fdo location
mkdir -p $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/scalable/apps
cp -p misc/%{name}.svg $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/scalable/apps

# Add desktop file
desktop-file-install --dir=${RPM_BUILD_ROOT}%{_datadir}/applications %{SOURCE1}

# Systemd unit file
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_unitdir}

# /etc/rsyslog.d/minetest.conf
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/rsyslog.d
cp -p %{SOURCE3} $RPM_BUILD_ROOT/%{_sysconfdir}/rsyslog.d/%{name}.conf

# /etc/logrotate.d/minetest
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d
cp -p %{SOURCE4} $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d/%{name}

# /var/lib/minetest directory for server data files
mkdir -p $RPM_BUILD_ROOT%{_sharedstatedir}/%{name} 

# /etc/minetest.conf
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}
cp -p minetest.conf.example $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf

# Move doc directory back to the sources
mkdir __doc
mv  $RPM_BUILD_ROOT%{_datadir}/doc/%{name}/* __doc
rm -rf $RPM_BUILD_ROOT%{_datadir}/doc/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%pre server
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
    useradd -r -g %{name} -d /var/lib/%{name} -s /sbin/nologin \
    -c "Minetest multiplayer server" %{name}
exit 0

%post server
if [ $1 -eq 1 ] ; then 
    # Initial installation 
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun server
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable %{name}.service > /dev/null 2>&1 || :
    /bin/systemctl stop %{name}.service > /dev/null 2>&1 || :
fi

%postun server
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart %{name}.service >/dev/null 2>&1 || :
fi

%files 
%defattr(-,root,root,-)
%{_bindir}/%{name}
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
%{_datadir}/icons/hicolor/128x128/apps/minetest.png
%{_datadir}/appdata/minetest.appdata.xml
%{_mandir}/man6/minetest.6.gz
%{_mandir}/man6/minetestserver.6.gz


%files server
%{_bindir}/%{name}server
%{_unitdir}/%{name}.service
%config(noreplace) %{_sysconfdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/rsyslog.d/%{name}.conf
%attr(0755,minetest,minetest) %dir %{_sharedstatedir}/%{name}

%files server-data
%defattr(-,minetest,minetest,-)
%{_datadir}/%name

%doc README.txt doc/*.txt

%changelog
* Sun Mar 5 2017 Eric Anderton <eric.t.anderton@gmail.com> - 0.4.15-1
- Forked Russian Fedora spec
- Modified for build on CentOS7 with Fedora Copr
- Changed source location to use publicly available source on github
- Removed localization concessions
