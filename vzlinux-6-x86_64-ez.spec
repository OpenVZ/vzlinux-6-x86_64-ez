# template name attributes
%define templatename vzlinux
%define templatever 6
%define templatearch x86_64

# Human-readable attributes
%define fullname VzLinux %templatever
%define fulltemplatearch (for AMD64/Intel EM64T)

# template dirs
%define templatedir /vz/template/%templatename/%templatever/%templatearch/config
%define ostemplatedir %templatedir/os/default

# vzpkgenv related
%define pkgman 47x64
%define package_manager rpm%pkgman
%define package_manager_pkg vzpkgenv%pkgman >= 7.0.0

# Files lists
%define files_lst() \
find %1 -type d -printf '%%%dir %%%attr(%m,root,root) %p\\n' | sed "s,%buildroot,,g" >> %2\
find %1 -type f -printf '%%%config %%%attr(%m,root,root) %p\\n' | sed "s,%buildroot,,g" >> %2\
%nil

# Sources list
%define sources_lst() \
%((cd %_sourcedir;\
s=1;\
for tmpl in %1; do\
sources=$tmpl"_*";\
for file in $sources; do\
echo Source$s: $file;\
s=$((s+1))\
done;\
done))\
%nil

# Obsoletes list
%define obsoletes_lst() \
%((for tmpl in %1; do\
[ $tmpl = os ] && continue;\
echo "Obsoletes: $tmpl-%templatename-%templatever-%templatearch-ez < 7.0.0";\
echo "Provides: $tmpl-%templatename-%templatever-%templatearch-ez = %version-%release";\
done))\
%nil

# Templates list - packages file should be always present in any template!
%define templates_list() %((cd %_sourcedir; for f in *_packages; do echo -n "${f%_*} "; done))

Summary: %fullname %fulltemplatearch Template set
Name: %templatename-%templatever-%templatearch-ez
Group: Virtuozzo/Templates
License: GPL
Version: 7.0.0
Release: 3%{?dist}
BuildRoot: %_tmppath/%name-root
BuildArch: noarch
Requires: %package_manager_pkg

# template source files
%sources_lst %templates_list

# obsoletes
%obsoletes_lst %templates_list

%description
%fullname %fulltemplatearch packaged as a Virtuozzo Template set.

%install
installfile() {
	local sourcename=%_sourcedir/${1}_$4
	local mode=$2
	local dir=$3
	local name=$4

	[ ! -f $sourcename ] && return

	install -m $mode $sourcename $dir/$name
}

rm -f files.lst
for tmpl in %templates_list; do
	[ $tmpl = "os" ] && dir=%buildroot/%ostemplatedir || \
		dir=%buildroot/%templatedir/app/$tmpl/default

	mkdir -p $dir

	if [ $tmpl = "os" ]; then
		# Os template only files

		# Text
		echo "%fullname %fulltemplatearch Virtuozzo Template" > $dir/description
		echo "%fullname %fulltemplatearch Virtuozzo Template" > $dir/summary

		# Package manager
		echo "%package_manager" > $dir/package_manager

		# Disable upgrade
		touch $dir/upgradable_versions

		# Pkgman environment
		installfile $tmpl 0644 $dir environment

		# vzctl-related
		installfile $tmpl 0644 $dir distribution

		# Kernel virtualization
		installfile $tmpl 0644 $dir osrelease

		# Os template cache scripts
		installfile $tmpl 0755 $dir pre-cache
		installfile $tmpl 0755 $dir post-cache
		installfile $tmpl 0755 $dir ct2vm
		installfile $tmpl 0755 $dir mid-pre-install
		installfile $tmpl 0755 $dir mid-post-install
		installfile $tmpl 0755 $dir pre-upgrade
		installfile $tmpl 0755 $dir post-upgrade
	else
		# App templates only files

		# Text
		echo "$tmpl for %fullname %fulltemplatearch Virtuozzo Template" > $dir/description
		echo "$tmpl for %fullname %fulltemplatearch Virtuozzo Template" > $dir/summary
	fi

	# Common things

	# Installation sources
	installfile $tmpl 0644 $dir mirrorlist
	installfile $tmpl 0644 $dir repositories

	# Packages
	installfile $tmpl 0644 $dir packages

	# Scripts
	installfile $tmpl 0755 $dir pre-install
	installfile $tmpl 0755 $dir pre-install-hn
	installfile $tmpl 0755 $dir post-install
	installfile $tmpl 0755 $dir post-install-hn

	# Versioning
	echo "%release" > $dir/release
	echo "%version" > $dir/version
	%files_lst $dir files.lst
done

%files -f files.lst

%changelog
* Tue Apr 26 2016 Denis Silakov <dsilakov@virtuozzo.com> 7.0.0-3
- Drop aux mirrors - all necessary packages are in vzlinux repos now

* Thu Apr 21 2016 Denis Silakov <dsilakov@virtuozzo.com> 7.0.0-1
- Initial release
