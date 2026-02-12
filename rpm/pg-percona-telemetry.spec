%define pg_name @BUILD_FLAVOR@%{nil}
%{percona_pg_version_from_name}

%global sname percona-pg-telemetry
%global pgrel %{pg_version}
%global pginstdir /usr/pgsql-%{pg_version}/

Summary:        Statistics collector for PostgreSQL
Name:           %{sname}%{pgrel}
Version:        1.2.0
Release:        1%{?dist}
License:        PostgreSQL
Source0:        %{sname}-%{version}.tar.gz
URL:            https://github.com/percona/percona_pg_telemetry

%if "%{pg_name}" == ""
ExclusiveArch:  do_not_build
Name:           %{sname}
%endif

BuildRequires: %{pg_name}-devel
BuildRequires: clang
BuildRequires: llvm

Requires:       percona-telemetry-agent
Provides:       %{sname}%{pgrel}
Conflicts:      %{sname}%{pgrel}
Obsoletes:      %{sname}%{pgrel} <= %{version}-%{release}
Epoch:          1
Packager:       Percona Development Team <https://jira.percona.com>
Vendor:         Percona, Inc

%description
The percona_pg_telemetry is an extension for Percona telemetry data collection for PostgreSQL.

%prep
%setup -q -n %{sname}-%{version}


%build
sed -i 's:PG_CONFIG = pg_config:PG_CONFIG = /usr/pgsql-%{pgrel}/bin/pg_config:' Makefile
%{__make} USE_PGXS=1 %{?_smp_mflags}


%install
%{__rm} -rf %{buildroot}
%{__make} USE_PGXS=1 %{?_smp_mflags} install DESTDIR=%{buildroot}
%{__install} -d %{buildroot}%{pginstdir}/share/extension
%{__install} -m 755 README.md %{buildroot}%{pginstdir}/share/extension/README-percona_pg_telemetry


%clean
%{__rm} -rf %{buildroot}

%pre -n %{sname}%{pgrel}
if [ $1 == 1 ]; then
  if ! getent passwd postgres > /dev/null 2>&1; then
    groupadd -g 26 -o -r postgres >/dev/null 2>&1 || :
    /usr/sbin/useradd -M -g postgres -o -r -d /var/lib/pgsql -s /bin/bash \
        -c "PostgreSQL Server" -u 26 postgres >/dev/null 2>&1 || :
  fi
fi

%post -n %{sname}%{pgrel}
usermod -a -G percona-telemetry postgres
install -d -m 2775 -o postgres -g percona-telemetry /usr/local/percona/telemetry/pg

%postun -n %{sname}%{pgrel}
rm -rf /usr/local/percona/telemetry/pg

%files
%defattr(755,root,root,755)
%doc %{pginstdir}/share/extension/README-percona_pg_telemetry
%{pginstdir}/lib/percona_pg_telemetry.so
%{pginstdir}/share/extension/percona_pg_telemetry--*.sql
%{pginstdir}/share/extension/percona_pg_telemetry.control
%{pginstdir}/lib/bitcode/percona_pg_telemetry*.bc
%{pginstdir}/lib/bitcode/percona_pg_telemetry/*.bc


%changelog
* Fri Apr 26 2024 Surabhi Bhat <surabhi.bhat@percona.com> - 1.0.0-1
- Initial build
