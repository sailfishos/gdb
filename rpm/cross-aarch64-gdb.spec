%global     ctarch %{crosstarget}__%{_arch}

Name: cross-aarch64-gdb
%define crosstarget aarch64-meego-linux-gnu

%if "%{?crosstarget}" != ""
%define _prefix /opt/cross
%endif

Summary:    A GNU source-level debugger for C, C++, Java and other languages
Version:    16.3.0
Release:    1
License:    GPLv3+
URL:        https://github.com/sailfishos/gdb
Source0:    %{name}-%{version}.tar.bz2
Source1:    gdb-rpmlintrc

# Update gdb-add-index.sh such that, when the GDB environment
# variable is not set, the script is smarter than just looking for
# 'gdb' in the $PATH.
#
# The actual search order is now: /usr/bin/gdb.minimal, gdb (in the
# $PATH), then /usr/libexec/gdb.
#
# For the rationale of looking for gdb.minimal see:
#
#   https://fedoraproject.org/wiki/Changes/Minimal_GDB_in_buildroot
#
#=fedora
Patch002: gdb-add-index.patch

# Not a backport.  Add a new script which hooks into GDB and suggests
# RPMs to install when GDB finds an objfile with no debug info.
Patch003: gdb-rpm-suggestion-script.patch

# Backport "Fix another timeout in gdb.base/bg-execution-repeat.exp"
Patch004: gdb-fix-bg-execution-repeat.patch

# Sailfish OS modifications to rpm suggestion script
Patch005: gdb-rpm-suggestion-script-sailfishos.patch

BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  gettext
BuildRequires:  libstdc++
BuildRequires:  texinfo
BuildRequires:  pkgconfig(expat)
BuildRequires:  pkgconfig(gmp)
BuildRequires:  pkgconfig(mpfr)
BuildRequires:  pkgconfig(ncurses)
BuildRequires:  pkgconfig(python3)
BuildRequires:  pkgconfig(zlib)
Requires:       python3-base
Recommends:     rpm-python

%description
GDB, the GNU debugger, allows you to debug programs written in C, C++,
Java, and other languages, by executing them in a controlled fashion
and printing their data.


%prep
%autosetup -p1 -n %{name}-%{version}/upstream

cat > gdb/version.in << _FOO
Sailfish OS (%{version})
_FOO

# Remove the info and other generated files added by the FSF release
# process. (From Fedora)
rm -f libdecnumber/gstdint.h
rm -f bfd/doc/*.info
rm -f bfd/doc/*.info-*
rm -f gdb/doc/*.info
rm -f gdb/doc/*.info-*

%build
g77="$( which gfortran 2>/dev/null || true )"
test -z "$g77" || ln -s "$g77" ./g77
export CFLAGS="$RPM_OPT_FLAGS"

# We can't use --with-system-readline as we can't update system readline to
# version 6+ because of GPLv3 things.
./configure                                                 \
    --prefix=%{_prefix}                                     \
    --libdir=%{_libdir}                                     \
    --sysconfdir=%{_sysconfdir}                             \
    --mandir=%{_mandir}                                     \
    --infodir=%{_infodir}                                   \
%if "%{?crosstarget}" != ""
    --with-gdb-datadir=%{_datadir}/%{crosstarget}-gdb       \
    --with-pythondir=%{_datadir}/%{crosstarget}-gdb/python  \
    --target=%{crosstarget}                                 \
%else
    --with-gdb-datadir=%{_datadir}/gdb                      \
    --with-pythondir=%{_datadir}/gdb/python                 \
%endif
    --enable-gdb-build-warnings=,-Wno-unused                \
    --disable-werror                                        \
    --with-separate-debug-dir=/usr/lib/debug                \
    --disable-rpath                                         \
    --with-expat                                            \
    --enable-tui                                            \
    --with-python=%{__python3}                              \
    --without-libunwind                                     \
    --enable-64-bit-bfd                                     \
    --enable-static                                         \
    --disable-shared                                        \
    --enable-debug                                          \
    --disable-binutils                                      \
    --disable-ld                                            \
    --disable-gold                                          \
    --disable-gas                                           \
    --disable-sim                                           \
    --disable-gprof                                         \
    --disable-gprofng                                       \
    %{_target_platform}

%make_build
%make_build info


%install
%make_install

find %{buildroot} -name \*.a -delete

rm -r %{buildroot}%{_datadir}/locale/
rm -r %{buildroot}%{_includedir}

%if "%{?crosstarget}" == ""
cp gdb/gcore.in "%{buildroot}%{_bindir}/gcore"
chmod 755 "%{buildroot}%{_bindir}/gcore"
mkdir -p "%{buildroot}%{_docdir}/%{name}-%{version}"
install -m 0644 -t "%{buildroot}%{_docdir}/%{name}-%{version}" README gdb/NEWS
rm "%{buildroot}%{_infodir}"/bfd*
rm -f "%{buildroot}%{_infodir}"/ctf-spec*
rm -f "%{buildroot}%{_infodir}"/sframe-spec*
%else
rm -r "%{buildroot}%{_infodir}/"
rm -r "%{buildroot}%{_mandir}/"
%endif


%if "%{?crosstarget}" == ""
#### NON-CROSS PACS

%package gdbserver
Summary:    A standalone server for GDB (the GNU source-level debugger)
%ifarch %{ix86} x86_64
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig
%endif

%description gdbserver
GDB, the GNU debugger, allows you to debug programs written in C, C++,
Java, and other languages, by executing them in a controlled fashion
and printing their data.

This package provides a program that allows you to run GDB on a different
machine than the one which is running the program being debugged.

%package doc
Summary:   Documentation for %{name}
Requires:  %{name} = %{version}-%{release}
Requires(post): /sbin/install-info
Requires(postun): /sbin/install-info

%description doc
Man and info pages for %{name}.

%ifarch %{ix86} x86_64
%post gdbserver -p /sbin/ldconfig
%postun gdbserver -p /sbin/ldconfig
%endif

%post doc
%install_info --info-dir=%{_infodir} %{_infodir}/annotate.info.gz
%install_info --info-dir=%{_infodir} %{_infodir}/gdb.info.gz
%install_info --info-dir=%{_infodir} %{_infodir}/gdbint.info.gz
%install_info --info-dir=%{_infodir} %{_infodir}/stabs.info.gz

%postun doc
if [ $1 = 0 ]
then
    %install_info_delete --info-dir=%{_infodir} %{_infodir}/annotate.info.gz
    %install_info_delete --info-dir=%{_infodir} %{_infodir}/gdb.info.gz
    %install_info_delete --info-dir=%{_infodir} %{_infodir}/gdbint.info.gz
    %install_info_delete --info-dir=%{_infodir} %{_infodir}/stabs.info.gz
fi


%files
%license COPYING3 COPYING3.LIB
%{_bindir}/gcore
%{_bindir}/gdb
%{_bindir}/gdb-add-index
%{_bindir}/gstack
%{_datadir}/gdb
%if "%{_arch}" == "aarch64"
%{_libdir}/libinproctrace.so
%endif

%files gdbserver
%{_bindir}/gdbserver
%ifarch %{ix86} x86_64
%{_libdir}/libinproctrace.so
%endif

%files doc
%{_mandir}/*/gdb.1*
%{_mandir}/*/gdbserver.1*
%{_mandir}/man1/gcore.1.gz
%{_mandir}/man1/gdb-add-index.1.gz
%{_mandir}/man1/gstack.1.gz
%{_mandir}/man5/gdbinit.5.gz
%{_infodir}/annotate.info.gz
%{_infodir}/gdb.info.gz
%{_infodir}/stabs.info.gz
%{_docdir}/%{name}-%{version}


%else
# crosstarget
#### CROSS PACS

%files
/opt/cross/share/%{crosstarget}-gdb
%if "%{ctarch}" == "aarch64-meego-linux-gnu__aarch64" || "%{ctarch}" == "i486-meego-linux-gnu__i386" || "%{ctarch}" == "armv7hl-meego-linux-gnueabi__arm" || "%{ctarch}" == "x86_64-meego-linux-gnu__x86_64"
/opt/cross/bin/gcore
/opt/cross/bin/gdb
/opt/cross/bin/gdb-add-index
/opt/cross/bin/gdbserver
/opt/cross/bin/gstack
%else
/opt/cross/bin/%{crosstarget}-gdb
/opt/cross/bin/%{crosstarget}-gdb-add-index
/opt/cross/bin/%{crosstarget}-gstack
%endif

%if "%{ctarch}" == "aarch64-meego-linux-gnu__aarch64" || "%{ctarch}" == "i486-meego-linux-gnu__i386" || "%{ctarch}" == "x86_64-meego-linux-gnu__x86_64"
/opt/cross/%{_lib}/libinproctrace.so
%endif

# crosstarget
%endif
