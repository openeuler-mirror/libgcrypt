%global gcrylibdir %{_libdir}
%global gcrysoname libgcrypt.so.20
%global hmackey orboDeJITITejsirpADONivirpUkvarP

Name:          libgcrypt
Version:       1.9.4
Release:       2
Summary:       A general-purpose cryptography library
License:       LGPLv2+
URL:           https://www.gnupg.org/
Source0:       https://www.gnupg.org/ftp/gcrypt/libgcrypt/libgcrypt-%{version}.tar.bz2
Source7:       random.conf

Patch0:        backport-libgcrypt-1.8.5-use-fipscheck.patch
Patch1:        backport-libgcrypt-1.8.4-fips-keygen.patch
Patch2:        backport-libgcrypt-1.8.4-tests-fipsmode.patch
Patch3:        backport-libgcrypt-1.7.3-fips-cavs.patch
Patch4:        backport-libgcrypt-1.8.4-use-poll.patch
Patch5:        backport-libgcrypt-1.6.1-mpicoder-gccopt.patch
Patch6:        backport-libgcrypt-1.7.3-ecc-test-fix.patch
Patch7:        backport-libgcrypt-1.8.3-fips-ctor.patch
Patch8:        backport-libgcrypt-1.8.5-getrandom.patch
Patch9:        backport-libgcrypt-1.8.3-fips-enttest.patch
Patch10:       backport-libgcrypt-1.8.3-md-fips-enforce.patch
Patch11:       backport-libgcrypt-1.8.5-intel-cet.patch
Patch12:       backport-libgcrypt-1.8.5-fips-module.patch
Patch13:       fix-clang.patch
BuildRequires: gcc texinfo autoconf automake libtool
BuildRequires: gawk libgpg-error-devel >= 1.11 pkgconfig

Provides:      %{name}-sm3 = %{version}-%{release}

%description
Libgcrypt is a general purpose cryptographic library originally based on code from GnuPG.

%package       devel
Summary:       Development files for the %{name} package
License:       LGPLv2+ and GPLv2+
Requires:      libgpg-error-devel %{name} = %{version}-%{release} pkgconfig

%description devel
Libgcrypt is a general purpose crypto library based on the code used
in GNU Privacy Guard.  This package contains files needed to develop
applications using libgcrypt.

%package_help

%prep
%autosetup -n %{name}-%{version} -p1

%build
%define _lto_cflags %{nil}
autoreconf -f

%configure  --disable-static --enable-noexecstack --enable-hmac-binary-check \
     --enable-pubkey-ciphers='dsa elgamal rsa ecc' --disable-O-flag-munging

sed -i -e '/^sys_lib_dlsearch_path_spec/s,/lib /usr/lib,/usr/lib /lib64 /usr/lib64 /lib,g' libtool
%make_build

%check
src/hmac256 %{hmackey} src/.libs/%{gcrysoname} | cut -f1 -d ' ' >src/.libs/.%{gcrysoname}.hmac

make check

%define __spec_install_post \
    %{?__debug_package:%{__debug_install_post}} \
    %{__arch_install_post} \
    %{__os_install_post} \
    src/hmac256 %{hmackey} $RPM_BUILD_ROOT%{gcrylibdir}/%{gcrysoname} | cut -f1 -d ' ' >$RPM_BUILD_ROOT%{gcrylibdir}/.%{gcrysoname}.hmac \
%{nil}

%install
%make_install

sed -i -e 's,^libdir="/usr/lib.*"$,libdir="/usr/lib",g' $RPM_BUILD_ROOT/%{_bindir}/libgcrypt-config
sed -i -e 's,^my_host=".*"$,my_host="none",g' $RPM_BUILD_ROOT/%{_bindir}/libgcrypt-config
%delete_la

/sbin/ldconfig -n $RPM_BUILD_ROOT/%{_libdir}

%if "%{gcrylibdir}" != "%{_libdir}"
mkdir -p $RPM_BUILD_ROOT%{gcrylibdir}
for shlib in $RPM_BUILD_ROOT%{_libdir}/*.so* ; do
	if test -L "$shlib" ; then
		rm "$shlib"
	else
		mv "$shlib" $RPM_BUILD_ROOT%{gcrylibdir}/
	fi
done

/sbin/ldconfig -n $RPM_BUILD_ROOT/%{_lib}/
%endif

pushd $RPM_BUILD_ROOT/%{gcrylibdir}
for shlib in lib*.so.?? ; do
	target=$RPM_BUILD_ROOT/%{_libdir}/`echo "$shlib" | sed -e 's,\.so.*,,g'`.so
%if "%{gcrylibdir}" != "%{_libdir}"
	shlib=%{gcrylibdir}/$shlib
%endif
	ln -sf $shlib $target
done
popd

mkdir -p -m 755 $RPM_BUILD_ROOT/etc/gcrypt
install -m644 %{SOURCE7} $RPM_BUILD_ROOT/etc/gcrypt/random.conf

%ldconfig_scriptlets

%files
%defattr(-,root,root)
%doc AUTHORS NEWS THANKS
%license COPYING.LIB COPYING
%dir /etc/gcrypt
%config(noreplace) /etc/gcrypt/random.conf
%{gcrylibdir}/*.so.*
%{gcrylibdir}/.*.so.*.hmac
%exclude %{_infodir}/dir

%files devel
%defattr(-,root,root)
%{_bindir}/*
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/libgcrypt.pc
%{_datadir}/aclocal/*

%files help
%defattr(-,root,root)
%{_mandir}/man1/*
%{_infodir}/gcrypt.info*

%changelog
* Mon May 22 2023 Xiang Zhang <zhangxiang@iscas.ac.cn> - 1.9.4-2
- Fix clang build error

* Thu Dec 30 2021 zoulin <zoulin13@huawei.com> - 1.9.4-1
- Type:requirements
- ID:NA
- SUG:NA
- DESC:Update version to 1.9.4

* Wed Oct 27 2021 zhujianwei001 <zhujianwei7@huawei.com> - 1.8.7-5
- Type:requirements
- ID:NA
- SUG:NA
- DESC:add support sm3

* Fri Sep 24 2021 zoulin <zoulin13@huawei.com> - 1.8.7-4
- Type:cves
- ID:NA
- SUG:NA
- DESC:Fix CVE-2021-33560 CVE-2021-40528

* Fri Jul 30 2021 chenyanpanHW <chenyanpan@huawei.com> - 1.8.7-3
- DESC: delete -S git from autosetup, and delete BuildRequires git

* Mon Jun 21 2021 gaihuiying1 <gaihuiying1@huawei.com> - 1.8.7-2
- Type:cves
- ID:NA
- SUG:NA
- DESC:Fix CVE-2021-33560

* Fri Jan 29 2021 xihaochen <xihaochen@huawei.com> - 1.8.7-1
- Type:requirements
- Id:NA
- SUG:NA
- DESC:update libgcrypt to 1.8.7

* Sat Sep 19 2020 xiaqirong <xiaqirong1@huawei.com> - 1.8.6-3
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:Fix warnings instroduced by aes-perf patch

* Sun Aug 30 2020 openEuler Buildteam <buildteam@openeuler.org> - 1.8.6-2
- Type:bugfix
- ID:NA
- SUG:restart
- DESC:delete # of patch in spec

* Sun Jul 26 2020 openEuler Buildteam <buildteam@openeuler.org> - 1.8.6-1
- update to 1.8.6 from upstream

* Sat Dec 21 2019 openEuler Buildteam <buildteam@openeuler.org> - 1.8.5-1
- update to 1.8.5 from upstream

* Sat Dec 21 2019 openEuler Buildteam <buildteam@openeuler.org> - 1.8.3-5
- Type:cves
- ID:NA
- SUG:restart
- DESC:fix CVEs

* Thu Sep 05 2019 openEuler Buildteam <buildteam@openeuler.org> - 1.8.3-4
- Package init
