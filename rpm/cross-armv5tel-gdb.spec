%define     _unpackaged_files_terminate_build 0

Name: cross-armv5tel-gdb
%define crosstarget armv5tel-meego-linux-gnueabi

%if "%{?crosstarget}" != ""
%define _prefix /opt/cross
%endif

Summary:    A GNU source-level debugger for C, C++, Java and other languages
Version:    8.2.1
Release:    1
Group:      Development/Debuggers
License:    GPLv3+
URL:        http://gnu.org/software/gdb/
Source0:    %{name}-%{version}.tar.bz2
Source1:    gdb-rpmlintrc
Source2:    precheckin.sh

# New locating of the matching binaries from the pure core file (build-id).
Patch1: gdb-6.6-buildid-locate.patch
# Fix loading of core files without build-ids but with build-ids in executables.
Patch2: gdb-6.6-buildid-locate-solib-missing-ids.patch
Patch3: gdb-6.6-buildid-locate-rpm.patch
# Workaround librpm BZ 643031 due to its unexpected exit() calls (BZ 642879).
Patch4: gdb-6.6-buildid-locate-rpm-librpm-workaround.patch
Patch5: gdb-6.6-buildid-locate-rpm-suse.patch

BuildRequires:  pkgconfig(ncurses)
BuildRequires:  texinfo
BuildRequires:  gettext
BuildRequires:  flex
BuildRequires:  bison
BuildRequires:  expat-devel
BuildRequires:  python-devel
BuildRequires:  libstdc++
BuildRequires:  zlib-devel

%description
GDB, the GNU debugger, allows you to debug programs written in C, C++,
Java, and other languages, by executing them in a controlled fashion
and printing their data.

%if "%{?crosstarget}" == ""
%package gdbserver
Summary:    A standalone server for GDB (the GNU source-level debugger)
Group:      Development/Debuggers
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description gdbserver
GDB, the GNU debugger, allows you to debug programs written in C, C++,
Java, and other languages, by executing them in a controlled fashion
and printing their data.

This package provides a program that allows you to run GDB on a different machine than the one which is running the program being debugged.

%endif

%package doc
Summary:   Documentation for %{name}
Group:     Documentation
Requires:  %{name} = %{version}-%{release}
Requires(post): /sbin/install-info
Requires(postun): /sbin/install-info

%description doc
Man and info pages for %{name}.

%prep
%setup -q -n %{name}-%{version}/upstream
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

cat > gdb/version.in << _FOO
Mer (%{version})
_FOO

%build

g77="`which gfortran 2>/dev/null || true`"
test -z "$g77" || ln -s "$g77" ./g77
export CFLAGS="$RPM_OPT_FLAGS"
./configure                                                 \
    --prefix=%{_prefix}                                     \
    --libdir=%{_libdir}                                     \
    --sysconfdir=%{_sysconfdir}                             \
    --mandir=%{_mandir}                                     \
    --infodir=%{_infodir}                                   \
%if "%{?crosstarget}" != ""
    --with-gdb-datadir=%{_datadir}/%{crosstarget}-gdb       \
    --with-pythondir=%{_datadir}/%{crosstarget}-gdb/python  \
%else
    --with-gdb-datadir=%{_datadir}/gdb                      \
    --with-pythondir=%{_datadir}/gdb/python                 \
%endif
    --enable-gdb-build-warnings=,-Wno-unused                \
    --disable-werror                                        \
    --with-separate-debug-dir=/usr/lib/debug                \
%if "%{?crosstarget}" != ""
    --target=%{crosstarget} \
%endif
    --disable-sim                                           \
    --disable-rpath                                         \
    --with-expat                                            \
    --enable-tui                                            \
    --with-python                                           \
    --without-libunwind                                     \
    --enable-64-bit-bfd                                     \
    --enable-static --disable-shared --enable-debug         \
%{_target_platform}

# We can't use --with-system-readline as we can't update system readline to
# version 6+ because of GPLv3 things.

make %{?_smp_mflags}

make %{?_smp_mflags} info

%clean
rm -rf %{buildroot}

%install
%make_install

# install the gcore script in /usr/bin
%if "%{?crosstarget}" == ""
cp gdb/gcore.in %{buildroot}%{_bindir}/gcore
chmod 755 %{buildroot}%{_bindir}/gcore

mkdir -p %{buildroot}%{_docdir}/%{name}-%{version}
install -m0644 -t %{buildroot}%{_docdir}/%{name}-%{version} README gdb/NEWS

rm %{buildroot}%{_infodir}/bfd*
rm %{buildroot}%{_bindir}/addr2line
rm %{buildroot}%{_bindir}/ar
rm %{buildroot}%{_bindir}/as
rm %{buildroot}%{_bindir}/c++filt
rm %{buildroot}%{_bindir}/elfedit
rm %{buildroot}%{_bindir}/gdb-add-index
rm %{buildroot}%{_bindir}/gprof
rm %{buildroot}%{_bindir}/ld
rm %{buildroot}%{_bindir}/ld.bfd
rm %{buildroot}%{_bindir}/nm
rm %{buildroot}%{_bindir}/objcopy
rm %{buildroot}%{_bindir}/objdump
rm %{buildroot}%{_bindir}/ranlib
rm %{buildroot}%{_bindir}/readelf
rm %{buildroot}%{_bindir}/size
rm %{buildroot}%{_bindir}/strings
rm %{buildroot}%{_bindir}/strip
rm %{buildroot}/usr/%{_target_platform}/bin/ar
rm %{buildroot}/usr/%{_target_platform}/bin/as
rm %{buildroot}/usr/%{_target_platform}/bin/ld
rm %{buildroot}/usr/%{_target_platform}/bin/ld.bfd
rm %{buildroot}/usr/%{_target_platform}/bin/nm
rm %{buildroot}/usr/%{_target_platform}/bin/objcopy
rm %{buildroot}/usr/%{_target_platform}/bin/objdump
rm %{buildroot}/usr/%{_target_platform}/bin/ranlib
rm %{buildroot}/usr/%{_target_platform}/bin/readelf
rm %{buildroot}/usr/%{_target_platform}/bin/strip
rm -r %{buildroot}/usr/%{_target_platform}/lib/ldscripts/

%else
rm -r %{buildroot}%{_infodir}/
rm -r %{buildroot}%{_mandir}/

%endif

rm -r %{buildroot}%{_datadir}/locale/
rm -r %{buildroot}%{_includedir}

%if "%{?crosstarget}" == ""

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

%endif

%if "%{?crosstarget}" == ""

%post gdbserver -p /sbin/ldconfig

%postun gdbserver -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%license COPYING COPYING.LIB
%{_bindir}/gcore
%{_bindir}/gdb
%{_datadir}/gdb

%files gdbserver
%defattr(-,root,root,-)
%{_bindir}/gdbserver
%ifarch %{ix86} x86_64
%{_libdir}/libinproctrace.so

%endif

%files doc
%defattr(-,root,root,-)
%{_mandir}/*/gdb.1*
%{_mandir}/*/gdbserver.1*
%{_mandir}/man1/gcore.1.gz
%{_mandir}/man1/gdb-add-index.1.gz
%{_mandir}/man5/gdbinit.5.gz
%{_infodir}/annotate.info.gz
%{_infodir}/gdb.info.gz
%{_infodir}/stabs.info.gz
%{_docdir}/%{name}-%{version}

%else

%files
%defattr(-,root,root,-)
/opt/cross

%endif
