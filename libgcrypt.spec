%define gcrylibdir %{_libdir}
Name:          libgcrypt
Version:       1.8.3
Release:       5
Summary:       A general-purpose cryptography library
License:       LGPLv2+
URL:           https://www.gnupg.org/
Source0:       https://www.gnupg.org/ftp/gcrypt/libgcrypt/libgcrypt-%{version}.tar.gz
Source2:       wk@g10code.com
Source3:       hobble-libgcrypt
Source4:       ecc-curves.c
Source5:       curves.c
Source6:       t-mpi-point.c
Source7:       random.conf

Patch2:        libgcrypt-1.6.2-use-fipscheck.patch
Patch5:        libgcrypt-1.8.0-tests.patch
Patch7:        libgcrypt-1.7.3-fips-cavs.patch
Patch11:       libgcrypt-1.8.0-use-poll.patch
Patch13:       libgcrypt-1.6.1-mpicoder-gccopt.patch
Patch14:       libgcrypt-1.7.3-ecc-test-fix.patch
Patch18:       libgcrypt-1.8.3-fips-ctor.patch
Patch22:       libgcrypt-1.7.3-fips-reqs.patch
Patch24:       libgcrypt-1.8.3-getrandom.patch

Patch6000:     sexp-Fix-uninitialized-use-of-a-var-in-the-error-cas.patch
Patch6001:     ecc-Fix-possible-memory-leakage-in-parameter-check-o.patch
Patch6002:     ecc-Fix-memory-leak-in-the-error-case-of-ecc_encrypt.patch
Patch6003:     Fix-memory-leak-in-secmem-in-out-of-core-conditions.patch

Patch6004:     CVE-2019-12904-1.patch
Patch6005:     CVE-2019-12904-2.patch
Patch6006:     CVE-2019-12904-3.patch
Patch6007:     CVE-2019-13627-1.patch
Patch6008:     CVE-2019-13627-2.patch

BuildRequires: gcc fipscheck texinfo git
BuildRequires: gawk libgpg-error-devel >= 1.11 pkgconfig

%description
Libgcrypt is a general purpose cryptographic library originally based on code from GnuPG.

%package       devel
Summary:       Development files for the %{name} package
License:       LGPLv2+ and GPLv2+
Requires(pre): /sbin/install-info
Requires(post): /sbin/install-info
Requires:      libgpg-error-devel %{name} = %{version}-%{release}

%description devel
Libgcrypt is a general purpose crypto library based on the code used
in GNU Privacy Guard.  This package contains files needed to develop
applications using libgcrypt.

%package_help

%prep
%autosetup -n %{name}-%{version} -p1 -S git
chmod +x %{SOURCE3}
%{SOURCE3}
cp %{SOURCE4} cipher/
cp %{SOURCE5} %{SOURCE6} tests/

%build
%configure  --enable-noexecstack --enable-hmac-binary-check \
     --enable-pubkey-ciphers='dsa elgamal rsa ecc' --disable-O-flag-munging

sed -i -e '/^sys_lib_dlsearch_path_spec/s,/lib /usr/lib,/usr/lib /lib64 /usr/lib64 /lib,g' libtool
%make_build

%check
fipshmac src/.libs/libgcrypt.so.??
%define __spec_install_post \
    %{?__debug_package:%{__debug_install_post}} \
    %{__arch_install_post} \
    %{__os_install_post} \
    fipshmac $RPM_BUILD_ROOT%{gcrylibdir}/*.so.?? \
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

%post devel
[ -f %{_infodir}/gcrypt.info.gz ] && \
    /sbin/install-info %{_infodir}/gcrypt.info.gz %{_infodir}/dir
exit 0

%preun devel
if [ $1 = 0 -a -f %{_infodir}/gcrypt.info.gz ]; then
    /sbin/install-info --delete %{_infodir}/gcrypt.info.gz %{_infodir}/dir
fi
exit 0

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
%{_datadir}/aclocal/*

%files help
%defattr(-,root,root)
%{_mandir}/man1/*
%{_infodir}/gcrypt.info*

%changelog
* Sat Dec 21 2019 openEuler Buildteam <buildteam@openeuler.org> - 1.8.3-5
- Type:cves
- ID:NA
- SUG:restart
- DESC:fix CVEs

* Thu Sep 05 2019 openEuler Buildteam <buildteam@openeuler.org> - 1.8.3-4
- Package init
