%define		svnrev	r12
%define		rel		1
Summary:	ControlJS is a JavaScript module for making scripts load faster
Name:		js-controljs
Version:	0.1
Release:	0.%{svnrev}.%{rel}
License:	Apache v2.0
Group:		Applications/WWW
Source0:	http://controljs.googlecode.com/svn/trunk/control.js
# Source0-md5:	e331dfc86f22f6ccbaa43c067d35cf0e
URL:		http://stevesouders.com/controljs/
BuildRequires:	rpmbuild(macros) >= 1.553
BuildRequires:	js
BuildRequires:	closure-compiler
Requires:	webserver(access)
Requires:	webserver(alias)
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_sysconfdir	%{_webapps}/%{_webapp}
%define		_appdir		%{_datadir}/%{_webapp}

%description
ControlJS is a JavaScript module for making scripts load faster.

%prep
%setup -qcT
cp -p %{SOURCE0} .

# Apache1/Apache2 config
cat > apache.conf <<'EOF'
Alias /js/controljs/ %{_appdir}/
<Directory %{_appdir}>
	Allow from all
</Directory>
EOF

# Lighttpd config
cat > lighttpd.conf <<'EOF'
alias.url += (
    "/js/controljs/" => "%{_appdir}/",
)
EOF

%build
install -d build
closure-compiler --js control.js --js_output_file build/control.js
js -C -f build/control.js

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_appdir}
cp -p build/* $RPM_BUILD_ROOT%{_appdir}

install -d $RPM_BUILD_ROOT%{_sysconfdir}
cp -p apache.conf $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
cp -p apache.conf $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf
cp -p lighttpd.conf $RPM_BUILD_ROOT%{_sysconfdir}/lighttpd.conf

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%triggerin -- lighttpd
%webapp_register lighttpd %{_webapp}

%triggerun -- lighttpd
%webapp_unregister lighttpd %{_webapp}

%files
%defattr(644,root,root,755)
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lighttpd.conf
%{_appdir}
