Name: cross-armv6l-gdb
%define crosstarget armv6l-meego-linux-gnueabi

# >> macros
%define gdb_src gdb-%{version}/gdb
%define gdb_build build-%{_target_platform}
%if "%{?crosstarget}" != ""
%define _prefix /opt/cross
%endif

# << macros

Summary:    A GNU source-level debugger for C, C++, Java and other languages
Version:    7.5.1
Release:    1
Group:      Development/Debuggers
License:    GPLv3+
URL:        http://gnu.org/software/gdb/
Source0:    ftp://ftp.gnu.org/gnu/gdb/gdb-%{version}.tar.bz2
Source1:    gdb-rpmlintrc
Source2:    precheckin.sh

Patch0: gdb-archer.patch
# New locating of the matching binaries from the pure core file (build-id).
#=push
Patch1: gdb-6.6-buildid-locate.patch
# Fix loading of core files without build-ids but with build-ids in executables.
#=push
Patch2: gdb-6.6-buildid-locate-solib-missing-ids.patch
#=push
Patch3: gdb-6.6-buildid-locate-rpm.patch
# Workaround librpm BZ 643031 due to its unexpected exit() calls (BZ 642879).
#=push
Patch4: gdb-6.6-buildid-locate-rpm-librpm-workaround.patch
#
Patch5: gdb-6.6-buildid-locate-rpm-suse.patch


Requires(post): /sbin/install-info
Requires(postun): /sbin/install-info
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
Requires:   %{name} = %{version}-%{release}
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description gdbserver
GDB, the GNU debugger, allows you to debug programs written in C, C++,
Java, and other languages, by executing them in a controlled fashion
and printing their data.

This package provides a program that allows you to run GDB on a different machine than the one which is running the program being debugged.

%endif

%prep
%setup -q -n gdb-%{version}/gdb
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
# >> setu1
# Files have `# <number> <file>' statements breaking VPATH / find-debuginfo.sh .
rm -f gdb/ada-exp.c gdb/ada-lex.c gdb/c-exp.c gdb/cp-name-parser.c gdb/f-exp.c
rm -f gdb/jv-exp.c gdb/m2-exp.c gdb/objc-exp.c gdb/p-exp.c

cat > gdb/version.in << _FOO
Mer (%{version})
_FOO

# Remove the info and other generated files added by the FSF release
# process.
rm -f libdecnumber/gstdint.h
rm -f bfd/doc/*.info
rm -f bfd/doc/*.info-*
rm -f gdb/doc/*.info
rm -f gdb/doc/*.info-*
# << setup

%build
# >> build pre
rm -fr %{gdb_build}
mkdir %{gdb_build}
cd %{gdb_build}
g77="`which gfortran 2>/dev/null || true`"
test -z "$g77" || ln -s "$g77" ./g77
export CFLAGS="$RPM_OPT_FLAGS"
../configure                                    \
--prefix=%{_prefix}                             \
--libdir=%{_libdir}                             \
--sysconfdir=%{_sysconfdir}                     \
--mandir=%{_mandir}                             \
--infodir=%{_infodir}                           \
%if "%{?crosstarget}" != ""
--with-gdb-datadir=%{_datadir}/%{crosstarget}-gdb              \
--with-pythondir=%{_datadir}/%{crosstarget}-gdb/python         \
%else
--with-gdb-datadir=%{_datadir}/gdb              \
--with-pythondir=%{_datadir}/gdb/python         \
%endif
--enable-gdb-build-warnings=,-Wno-unused        \
--disable-werror                                \
--with-separate-debug-dir=/usr/lib/debug        \
%if "%{?crosstarget}" != ""
--target=%{crosstarget} \
%endif
--disable-sim                                  \
--disable-rpath                                 \
--with-expat                                    \
--enable-tui                                    \
--with-python                                   \
--without-libunwind                             \
--enable-64-bit-bfd                             \
--enable-static --disable-shared --enable-debug \
%{_target_platform}

# We can't use --with-system-readline as we can't update system readline to
# version 6+ because of GPLv3 things.
# << build pre


make %{?jobs:-j%jobs}

# >> build post
make %{?_smp_mflags} info

# Copy the <sourcetree>/gdb/NEWS file to the directory above it.
cp $RPM_BUILD_DIR/%{gdb_src}/gdb/NEWS $RPM_BUILD_DIR/%{gdb_src}
# << build post

%install
rm -rf %{buildroot}
# >> install pre
# Initially we're in the %{gdb_src} directory.
cd %{gdb_build}
# << install pre
%make_install

# >> install post
# install the gcore script in /usr/bin
%if "%{?crosstarget}" == ""
cp $RPM_BUILD_DIR/%{gdb_src}/gdb/gdb_gcore.sh $RPM_BUILD_ROOT%{_bindir}/gcore
chmod 755 $RPM_BUILD_ROOT%{_bindir}/gcore
%else
rm -rf $RPM_BUILD_ROOT%{_infodir}/
rm -rf $RPM_BUILD_ROOT%{_mandir}/
%endif


rm -rf $RPM_BUILD_ROOT%{_datadir}/locale/
rm -f $RPM_BUILD_ROOT%{_infodir}/bfd*
rm -f $RPM_BUILD_ROOT%{_infodir}/standard*
rm -f $RPM_BUILD_ROOT%{_infodir}/mmalloc*
rm -f $RPM_BUILD_ROOT%{_infodir}/configure*
rm -rf $RPM_BUILD_ROOT%{_includedir}
rm -rf $RPM_BUILD_ROOT/%{_libdir}/lib{bfd*,opcodes*,iberty*,mmalloc*}
rm -f $RPM_BUILD_ROOT%{_infodir}/dir
# << install post


%check
# >> check
# Initially we're in the %{gdb_src} directory.
cd %{gdb_build}
# << check

%if "%{?crosstarget}" == ""
%post
%install_info --info-dir=%_infodir %{_infodir}/annotate.info.gz
%install_info --info-dir=%_infodir %{_infodir}/gdb.info.gz
%install_info --info-dir=%_infodir %{_infodir}/gdbint.info.gz
%install_info --info-dir=%_infodir %{_infodir}/stabs.info.gz

%postun
if [ $1 = 0 ] ;then
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
# >> files
%doc COPYING COPYING.LIB README NEWS
%{_bindir}/gcore
%{_bindir}/gdb
%{_mandir}/*/gdb.1*
%{_datadir}/gdb
%{_infodir}/annotate.info.gz
%{_infodir}/gdb.info.gz
%{_infodir}/gdbint.info.gz
%{_infodir}/stabs.info.gz
# << files

%files gdbserver
%defattr(-,root,root,-)
# >> files gdbserver
%{_bindir}/gdbserver
%{_mandir}/*/gdbserver.1*
%ifarch %{ix86} x86_64
%{_libdir}/libinproctrace.so
%endif
# << files gdbserver
%else
%files
%defattr(-,root,root,-)
/opt/cross
%endif
