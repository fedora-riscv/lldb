#%%global rc_ver 6
%global baserelease 3
%global lldb_srcdir %{name}-%{version}%{?rc_ver:rc%{rc_ver}}.src

Name:		lldb
Version:	10.0.0
Release:	%{baserelease}%{?rc_ver:.rc%{rc_ver}}%{?dist}
Summary:	Next generation high-performance debugger

License:	NCSA
URL:		http://lldb.llvm.org/
%if 0%{?rc_ver:1}
Source0:	https://prereleases.llvm.org/%{version}/rc%{rc_ver}/%{lldb_srcdir}.tar.xz
Source1:	https://prereleases.llvm.org/%{version}/rc%{rc_ver}/%{lldb_srcdir}.tar.xz.sig
%else
Source0:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/%{lldb_srcdir}.tar.xz
Source3:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/%{lldb_srcdir}.tar.xz.sig
%endif
Source2:	https://prereleases.llvm.org/%{version}/hans-gpg-key.asc

BuildRequires:	cmake
BuildRequires:	llvm-devel = %{version}
BuildRequires:	llvm-test = %{version}
BuildRequires:	clang-devel = %{version}
BuildRequires:	ncurses-devel
BuildRequires:	swig
BuildRequires:	llvm-static = %{version}
BuildRequires:	libffi-devel
BuildRequires:	zlib-devel
BuildRequires:	libxml2-devel
BuildRequires:	libedit-devel
BuildRequires:	python3-lit

Requires:	python3-lldb

%description
LLDB is a next generation, high-performance debugger. It is built as a set
of reusable components which highly leverage existing libraries in the
larger LLVM Project, such as the Clang expression parser and LLVM
disassembler.

%package devel
Summary:	Development header files for LLDB
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description devel
The package contains header files for the LLDB debugger.

%package -n python3-lldb
%{?python_provide:%python_provide python3-lldb}
Summary:	Python module for LLDB
BuildRequires:	python3-devel
Requires:	python3-six

%description -n python3-lldb
The package contains the LLDB Python module.

%prep
%autosetup -n %{lldb_srcdir} -p2

%build

mkdir -p _build
cd _build

# Python version detection is broken
LDFLAGS="%{__global_ldflags} -lpthread -ldl"

CFLAGS="%{optflags} -Wno-error=format-security"
CXXFLAGS="%{optflags} -Wno-error=format-security"

%cmake .. \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DCMAKE_SKIP_RPATH:BOOL=ON \
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
	-DLLVM_CONFIG:FILEPATH=/usr/bin/llvm-config-%{__isa_bits} \
	\
	-DLLDB_DISABLE_CURSES:BOOL=OFF \
	-DLLDB_DISABLE_LIBEDIT:BOOL=OFF \
	-DLLDB_DISABLE_PYTHON:BOOL=OFF \
%if 0%{?__isa_bits} == 64
	-DLLVM_LIBDIR_SUFFIX=64 \
%else
	-DLLVM_LIBDIR_SUFFIX= \
%endif
	\
	-DPYTHON_EXECUTABLE:STRING=%{__python3} \
	-DPYTHON_VERSION_MAJOR:STRING=$(%{__python3} -c "import sys; print(sys.version_info.major)") \
	-DPYTHON_VERSION_MINOR:STRING=$(%{__python3} -c "import sys; print(sys.version_info.minor)") \
	-DLLVM_EXTERNAL_LIT=%{_bindir}/lit \
	-DCLANG_LINK_CLANG_DYLIB=ON \
	-DLLVM_LIT_ARGS="-sv \
	--path %{_libdir}/llvm" \

make %{?_smp_mflags}

%install
cd _build
make install DESTDIR=%{buildroot}

# remove static libraries
rm -fv %{buildroot}%{_libdir}/*.a

# python: fix binary libraries location
liblldb=$(basename $(readlink -e %{buildroot}%{_libdir}/liblldb.so))
ln -vsf "../../../${liblldb}" %{buildroot}%{python3_sitearch}/lldb/_lldb.so
%py_byte_compile %{__python3} %{buildroot}%{python3_sitearch}/lldb

# remove bundled six.py
rm -f %{buildroot}%{python3_sitearch}/six.*

%ldconfig_scriptlets

%files
%{_bindir}/lldb*
%{_libdir}/liblldb.so.*
%{_libdir}/liblldbIntelFeatures.so.*

%files devel
%{_includedir}/lldb
%{_libdir}/*.so

%files -n python3-lldb
%{python3_sitearch}/lldb

%changelog
* Tue Jun 02 2020 sguelton@redhat.com - 10.0.0-3
- Instruct cmake not to generate RPATH

* Tue May 26 2020 Miro Hrončok <mhroncok@redhat.com> - 10.0.0-2
- Rebuilt for Python 3.9

* Mon Mar 30 2020 sguelton@redhat.com - 10.0.0-1
- 10.0.0 final

* Wed Mar 25 2020 sguelton@redhat.com - 10.0.0-0.6.rc6
- 10.0.0 rc6

* Fri Mar 20 2020 sguelton@redhat.com - 10.0.0-0.5.rc5
- 10.0.0 rc5

* Sun Mar 15 2020 sguelton@redhat.com - 10.0.0-0.4.rc4
- 10.0.0 rc4

* Thu Mar 05 2020 sguelton@redhat.com - 10.0.0-0.3.rc3
- 10.0.0 rc3

* Fri Feb 14 2020 sguelton@redhat.com - 10.0.0-0.2.rc2
- 10.0.0 rc2

* Fri Jan 31 2020 sguelton@redhat.com - 10.0.0-0.1.rc1
- 10.0.0 rc1

* Wed Jan 29 2020 Tom Stellard <tstellar@redhat.com> - 9.0.1-4
- Link against libclang-cpp.so
- https://fedoraproject.org/wiki/Changes/Stop-Shipping-Individual-Component-Libraries-In-clang-lib-Package

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 9.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Sat Dec 21 2019 Tom Stellard <tstellar@redhat.com> - 9.0.1-2
- 9.0.1 Release

* Thu Sep 19 2019 Tom Stellard <tstellar@redhat.com> - 9.0.0-1
- 9.0.0 Release

* Thu Aug 22 2019 Tom Stellard <tstellar@redhat.com> - 9.0.0-0.1.rc3
- 9.0.0-rc3 Release

* Mon Aug 19 2019 Miro Hrončok <mhroncok@redhat.com> - 8.0.0-2.2
- Rebuilt for Python 3.8

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 8.0.0-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Tue Mar 26 2019 sguelton@redhat.com - 8.0.0-2
- Only depend on Python3

* Wed Mar 20 2019 sguelton@redhat.com - 8.0.0-1
- 8.0.0 final

* Tue Mar 12 2019 sguelton@redhat.com - 8.0.0-0.4.rc4
- 8.0.0 Release candidate 4

* Tue Mar 5 2019 sguelton@redhat.com - 8.0.0-0.3.rc3
- 8.0.0 Release candidate 3

* Fri Feb 22 2019 sguelton@redhat.com - 8.0.0-0.2.rc2
- 8.0.0 Release candidate 2

* Mon Feb 11 2019 sguelton@redhat.com - 8.0.0-0.1.rc1
- 8.0.0 Release candidate 1

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 7.0.1-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Dec 17 2018 sguelton@redhat.com - 7.0.1-1
- 7.0.1 Release

* Tue Dec 04 2018 sguelton@redhat.com - 7.0.0-2
- Ensure rpmlint passes on specfile

* Tue Sep 25 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-1
- 7.0.0 Release

* Fri Sep 21 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.5.rc3
- lldb should depend on python2-lldb

* Mon Sep 17 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.4.rc3
- 7.0.0-rc3 Release

* Wed Sep 12 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.3.rc2
- Enable build on s390x

* Fri Aug 31 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.2.rc2
- 7.0.0-rc2 Release

* Tue Aug 14 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.1.rc1
- 7.0.1-rc1 Release

* Tue Aug 07 2018 Tom Stellard <tstellar@redhat.com> - 6.0.1-3
- Enable ppc64le arch

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 6.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon May 21 2018 Tom Stellard <tstellar@redhat.com> - 6.0.1-1
- 6.0.1 Release

* Mon May 21 2018 Tom Stellard <tstellar@redhat.com> - 6.0.1-0.1.rc1
- 6.0.1-rc1 Release

* Sat May 05 2018 Miro Hrončok <mhroncok@redhat.com> - 6.0.0-4
- Update Python macros to new packaging standards
  (See https://fedoraproject.org/wiki/Changes/Avoid_usr_bin_python_in_RPM_Build)

* Tue Mar 20 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-3
- Rebuild against llvm with the rhbz#1558657 fix

* Wed Mar 14 2018 Tilmann Scheller <tschelle@redhat.com> - 6.0.0-2
- Restore LLDB SB API headers, fixes rhbz#1548758

* Fri Mar 09 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-1
- 6.0.0 Release

* Tue Feb 13 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-0.3.rc2
- 6.0.0-rc2 release

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 6.0.0-0.2.rc1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Jan 25 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-0.1.rc1
- 6.0.1-rc1 Release

* Thu Dec 21 2017 Tom Stellard <tstellar@redhat.com> - 5.0.1-1
- 5.0.1 Release

* Fri Oct 06 2017 Tom Stellard <tstellar@redhat.com> - 5.0.0-1
- 5.0.0 Release

* Sat Aug 19 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 4.0.1-4
- Python 2 binary package renamed to python2-lldb
  See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3

* Mon Jul 31 2017 Jan Kratochvil <jan.kratochvil@redhat.com> - 4.0.1-3
- Backport lldb r303907
  Resolves rhbz #1356140

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jun 26 2017 Tom Stellard <tstellar@redhat.com> - 4.0.1-1
- 4.0.1 Release

* Mon May 15 2017 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_27_Mass_Rebuild

* Fri Mar 24 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-1
- lldb 4.0.0

* Tue Mar 21 2017 Tom Stellard <tstellar@redhat.com> - 3.9.1-4
- Add explicit Requires for llvm-libs and clang-libs

* Fri Mar 17 2017 Tom Stellard <tstellar@redhat.org> - 3.9.1-3
- Adjust python sys.path so lldb can find readline.so

* Tue Mar 14 2017 Tom Stellard <tstellar@redhat.com> - 3.9.1-2
- Fix build with gcc 7

* Thu Mar 02 2017 Dave Airlie <airlied@redhat.com - 3.9.1-1
- lldb 3.9.1

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.9.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Nov 14 2016 Nathaniel McCallum <npmccallum@redhat.com> - 3.9.0-3
- Disable libedit support until upstream fixes it (#1356140)

* Wed Nov  2 2016 Peter Robinson <pbrobinson@fedoraproject.org> 3.9.0-2
- Set upstream supported architectures in an ExclusiveArch

* Wed Oct 26 2016 Dave Airlie <airlied@redhat.com> - 3.9.0-1
- lldb 3.9.0
- fixup some issues with MIUtilParse by removing it
- build with -fno-rtti

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.8.0-2
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Thu Mar 10 2016 Dave Airlie <airlied@redhat.com> 3.8.0-1
- lldb 3.8.0

* Thu Mar 03 2016 Dave Airlie <airlied@redhat.com> 3.8.0-0.3
- lldb 3.8.0 rc3

* Wed Feb 24 2016 Dave Airlie <airlied@redhat.com> - 3.8.0-0.2
- dynamically link to llvm

* Thu Feb 18 2016 Dave Airlie <airlied@redhat.com> - 3.8.0-0.1
- lldb 3.8.0 rc2

* Sun Feb 14 2016 Dave Airlie <airlied@redhat.com> 3.7.1-3
- rebuild lldb against latest llvm

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Oct 06 2015 Jan Vcelak <jvcelak@fedoraproject.org> 3.7.0-100
- initial version using cmake build system
