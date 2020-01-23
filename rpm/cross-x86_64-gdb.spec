%global     __python %{__python3}

%global     ctarch %{crosstarget}__%{_arch}

Name: cross-x86_64-gdb
%define crosstarget x86_64-meego-linux-gnu

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
Patch6: system-gdbinit-missing-parentheses.patch

BuildRequires:  pkgconfig(ncurses)
BuildRequires:  texinfo
BuildRequires:  gettext
BuildRequires:  flex
BuildRequires:  bison
BuildRequires:  expat-devel
BuildRequires:  python3-devel
BuildRequires:  libstdc++
BuildRequires:  zlib-devel
Requires:       python3-base

%description
GDB, the GNU debugger, allows you to debug programs written in C, C++,
Java, and other languages, by executing them in a controlled fashion
and printing their data.


%prep
%setup -q -n %{name}-%{version}/upstream
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1

cat > gdb/version.in << _FOO
Mer (%{version})
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
    --with-python=%{__python}                               \
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
    %{_target_platform}

make %{?_smp_mflags}
make %{?_smp_mflags} info

%clean
rm -rf %{buildroot}

%install
%make_install

rm -r %{buildroot}%{_datadir}/locale/
rm -r %{buildroot}%{_includedir}

%if "%{?crosstarget}" == ""
cp gdb/gcore.in "%{buildroot}%{_bindir}/gcore"
chmod 755 "%{buildroot}%{_bindir}/gcore"
mkdir -p "%{buildroot}%{_docdir}/%{name}-%{version}"
install -m 0644 -t "%{buildroot}%{_docdir}/%{name}-%{version}" README gdb/NEWS
rm "%{buildroot}%{_infodir}"/bfd*
%else
rm -r "%{buildroot}%{_infodir}/"
rm -r "%{buildroot}%{_mandir}/"
%endif


%if "%{?crosstarget}" == ""
#### NON-CROSS PACS

%files
%defattr(-,root,root,-)
%license COPYING COPYING.LIB
%{_bindir}/gcore
%{_bindir}/gdb
%{_bindir}/gdb-add-index
%{_datadir}/gdb
%if "%{_arch}" == "aarch64"
/usr/lib/libinproctrace.so
%endif


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

%ifarch %{ix86} x86_64
%post gdbserver -p /sbin/ldconfig
%postun gdbserver -p /sbin/ldconfig
%endif

%files gdbserver
%defattr(-,root,root,-)
%{_bindir}/gdbserver
%ifarch %{ix86} x86_64
%{_libdir}/libinproctrace.so
%endif


%package doc
Summary:   Documentation for %{name}
Group:     Documentation
Requires:  %{name} = %{version}-%{release}
Requires(post): /sbin/install-info
Requires(postun): /sbin/install-info

%description doc
Man and info pages for %{name}.

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


%else # crosstarget
#### CROSS PACS

%files
%defattr(-,root,root,-)
/opt/cross/share/%{crosstarget}-gdb
%if "%{ctarch}" == "aarch64-meego-linux-gnu__aarch64" || "%{ctarch}" == "i486-meego-linux-gnu__i386" || "%{ctarch}" == "armv7hl-meego-linux-gnueabi__arm"
/opt/cross/bin/gcore
/opt/cross/bin/gdb
/opt/cross/bin/gdb-add-index
/opt/cross/bin/gdbserver
%else
/opt/cross/bin/%{crosstarget}-gdb
/opt/cross/bin/%{crosstarget}-gdb-add-index
%endif

%if "%{ctarch}" == "aarch64-meego-linux-gnu__aarch64" || "%{ctarch}" == "i486-meego-linux-gnu__i386"
/opt/cross/lib/libinproctrace.so
%endif

%endif # crosstarget
