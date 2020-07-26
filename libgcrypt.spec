%global gcrylibdir %{_libdir}
%global gcrysoname libgcrypt.so.20
%global hmackey orboDeJITITejsirpADONivirpUkvarP

Name:          libgcrypt
Version:       1.8.6
Release:       1
Summary:       A general-purpose cryptography library
License:       LGPLv2+
URL:           https://www.gnupg.org/
Source0:       https://www.gnupg.org/ftp/gcrypt/libgcrypt/libgcrypt-%{version}.tar.bz2
Source7:       random.conf

Patch2:        libgcrypt-1.8.5-use-fipscheck.patch
Patch5:        libgcrypt-1.8.4-fips-keygen.patch
Patch6:        libgcrypt-1.8.4-tests-fipsmode.patch
Patch7:        libgcrypt-1.7.3-fips-cavs.patch
Patch11:       libgcrypt-1.8.4-use-poll.patch
Patch13:       libgcrypt-1.6.1-mpicoder-gccopt.patch
Patch14:       libgcrypt-1.7.3-ecc-test-fix.patch
Patch18:       libgcrypt-1.8.3-fips-ctor.patch
Patch22:       libgcrypt-1.7.3-fips-reqs.patch
#Patch24:       libgcrypt-1.8.5-getrandom.patch
#Patch25:       libgcrypt-1.8.3-cmac-selftest.patch
#Patch26:       libgcrypt-1.8.3-fips-enttest.patch
#Patch27:       libgcrypt-1.8.3-md-fips-enforce.patch
#Patch28:       libgcrypt-1.8.5-intel-cet.patch
#Patch29:       libgcrypt-1.8.5-fips-module.patch
#Patch30:       libgcrypt-1.8.5-aes-perf.patch

Patch6004:     CVE-2019-12904-1.patch
Patch6005:     CVE-2019-12904-2.patch
Patch6006:     CVE-2019-12904-3.patch

BuildRequires: gcc texinfo git autoconf automake libtool
BuildRequires: gawk libgpg-error-devel >= 1.11 pkgconfig

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
%autosetup -n %{name}-%{version} -p1 -S git

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
