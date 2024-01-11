%bcond_without ant_tasks
%bcond_without maven_plugin

Name:           aqute-bnd
Version:        3.5.0
Release:        4%{?dist}
Summary:        BND Tool
# Part of jpm is under BSD, but jpm is not included in binary RPM
License:        ASL 2.0
URL:            http://bnd.bndtools.org/
BuildArch:      noarch

Source0:        %{version}.REL.tar.gz
# removes bundled jars from upstream tarball
# run as:
# ./repack-tarball.sh
Source1:        repack-tarball.sh

Source2:        parent.pom
Source3:        https://repo1.maven.org/maven2/biz/aQute/bnd/aQute.libg/%{version}/aQute.libg-%{version}.pom
Source4:        https://repo1.maven.org/maven2/biz/aQute/bnd/biz.aQute.bnd/%{version}/biz.aQute.bnd-%{version}.pom
Source5:        https://repo1.maven.org/maven2/biz/aQute/bnd/biz.aQute.bndlib/%{version}/biz.aQute.bndlib-%{version}.pom
Source6:        https://repo1.maven.org/maven2/biz/aQute/bnd/biz.aQute.bnd.annotation/%{version}/biz.aQute.bnd.annotation-%{version}.pom

Patch0:         0001-Disable-removed-commands.patch
Patch1:         0002-Fix-ant-compatibility.patch

BuildRequires:  maven-local
BuildRequires:  mvn(org.osgi:osgi.annotation)
BuildRequires:  mvn(org.osgi:osgi.cmpn)
BuildRequires:  mvn(org.osgi:osgi.core)
BuildRequires:  mvn(org.slf4j:slf4j-api)
BuildRequires:  mvn(org.slf4j:slf4j-simple)
%if %{with ant_tasks}
BuildRequires:  mvn(org.apache.ant:ant)
%endif
%if %{with maven_plugin}
BuildRequires:  mvn(junit:junit)
BuildRequires:  mvn(org.apache.maven:maven-artifact)
BuildRequires:  mvn(org.apache.maven:maven-compat)
BuildRequires:  mvn(org.apache.maven:maven-core)
BuildRequires:  mvn(org.apache.maven:maven-plugin-api)
BuildRequires:  mvn(org.apache.maven.plugins:maven-plugin-plugin)
BuildRequires:  mvn(org.apache.maven.plugins:maven-source-plugin)
BuildRequires:  mvn(org.apache.maven.plugin-tools:maven-plugin-annotations)
BuildRequires:  mvn(org.eclipse.aether:aether-api)
BuildRequires:  mvn(org.sonatype.plexus:plexus-build-api)
%endif
# Explicit javapackages-tools requires since bnd script uses
# /usr/share/java-utils/java-functions
Requires:       javapackages-tools

%description
The bnd tool helps you create and diagnose OSGi bundles.
The key functions are:
- Show the manifest and JAR contents of a bundle
- Wrap a JAR so that it becomes a bundle
- Create a Bundle from a specification and a class path
- Verify the validity of the manifest entries
The tool is capable of acting as:
- Command line tool
- File format
- Directives
- Use of macros

%package -n aqute-bndlib
Summary:        BND library

%description -n aqute-bndlib
%{summary}.

%if %{with maven_plugin}
%package -n bnd-maven-plugin
Summary:        BND Maven plugin

%description -n bnd-maven-plugin
%{summary}.
%endif

%package javadoc
Summary:        Javadoc for %{name}

%description javadoc
API documentation for %{name}.

%prep
%setup -q -n bnd-%{version}.REL

rm gradlew*

%patch0 -p1
%patch1 -p1

# the commands pull in more dependencies than we want (felix-resolver, jetty)
rm biz.aQute.bnd/src/aQute/bnd/main/{RemoteCommand,ResolveCommand}.java

sed 's/@VERSION@/%{version}/' %SOURCE2 > pom.xml
sed -i 's|${Bundle-Version}|%{version}|' biz.aQute.bndlib/src/aQute/bnd/osgi/bnd.info

%if %{without ant_tasks}
rm -rf biz.aQute.bnd/src/aQute/bnd/ant
%endif

%if %{without maven_plugin}
%pom_disable_module maven
%endif

# libg
pushd aQute.libg
cp -p %{SOURCE3} pom.xml
%pom_add_parent biz.aQute.bnd:parent:%{version}
%pom_add_dep org.osgi:osgi.cmpn
%pom_add_dep org.slf4j:slf4j-api
popd

# bndlib.annotations
pushd biz.aQute.bnd.annotation
cp -p %{SOURCE6} pom.xml
%pom_add_parent biz.aQute.bnd:parent:%{version}
popd

# bndlib
pushd biz.aQute.bndlib
cp -p %{SOURCE5} pom.xml
%pom_add_parent biz.aQute.bnd:parent:%{version}

%pom_add_dep org.osgi:osgi.annotation
%pom_add_dep org.osgi:osgi.core
%pom_add_dep org.osgi:osgi.cmpn
%pom_add_dep org.slf4j:slf4j-api
%pom_add_dep biz.aQute.bnd:aQute.libg:%{version}
%pom_add_dep biz.aQute.bnd:biz.aQute.bnd.annotation:%{version}
popd

# bnd
pushd biz.aQute.bnd
cp -p %{SOURCE4} pom.xml
%pom_add_parent biz.aQute.bnd:parent:%{version}

%pom_add_dep biz.aQute.bnd:biz.aQute.bndlib:%{version}
%pom_add_dep biz.aQute.bnd:aQute.libg:%{version}
%pom_add_dep biz.aQute.bnd:biz.aQute.bnd.annotation:%{version}
%if %{with ant_tasks}
%pom_add_dep org.apache.ant:ant
%endif
%pom_add_dep org.osgi:osgi.annotation
%pom_add_dep org.osgi:osgi.core
%pom_add_dep org.osgi:osgi.cmpn
%pom_add_dep org.slf4j:slf4j-api

%pom_add_dep org.slf4j:slf4j-simple::runtime
popd

# maven-plugins
pushd maven
rm bnd-shared-maven-lib/src/main/java/aQute/bnd/maven/lib/resolve/DependencyResolver.java
%pom_remove_dep -r :biz.aQute.resolve
%pom_remove_dep -r :biz.aQute.repository
# Unavailable reactor dependency - org.osgi.impl.bundle.repoindex.cli
%pom_disable_module bnd-indexer-maven-plugin
# Requires unbuilt parts of bnd
%pom_disable_module bnd-export-maven-plugin
%pom_disable_module bnd-resolver-maven-plugin
%pom_disable_module bnd-testing-maven-plugin
# Integration tests require Internet access
%pom_remove_plugin -r :maven-invoker-plugin
%pom_remove_plugin -r :maven-javadoc-plugin

%pom_remove_plugin -r :flatten-maven-plugin
popd


%mvn_alias biz.aQute.bnd:biz.aQute.bnd :bnd biz.aQute:bnd
%mvn_alias biz.aQute.bnd:biz.aQute.bndlib :bndlib biz.aQute:bndlib

%mvn_package biz.aQute.bnd:biz.aQute.bndlib bndlib
%mvn_package biz.aQute.bnd:biz.aQute.bnd.annotation bndlib
%mvn_package biz.aQute.bnd:aQute.libg bndlib
%mvn_package biz.aQute.bnd:bnd-shared-maven-lib maven
%mvn_package biz.aQute.bnd:bnd-maven-plugin maven
%mvn_package biz.aQute.bnd:bnd-baseline-maven-plugin maven
%mvn_package biz.aQute.bnd:parent __noinstall
%mvn_package biz.aQute.bnd:bnd-plugin-parent __noinstall

%build
%mvn_build -- -Dproject.build.sourceEncoding=UTF-8

%install
%mvn_install

%if %{with ant_tasks}
install -d -m 755 %{buildroot}%{_sysconfdir}/ant.d
echo "aqute-bnd slf4j/api slf4j/simple osgi-annotation osgi-core osgi-compendium" >%{buildroot}%{_sysconfdir}/ant.d/%{name}
%endif

%jpackage_script aQute.bnd.main.bnd "" "" aqute-bnd:slf4j/slf4j-api:slf4j/slf4j-simple:osgi-annotation:osgi-core:osgi-compendium bnd 1

%files -f .mfiles
%license LICENSE
%{_bindir}/bnd
%if %{with ant_tasks}
%config(noreplace) %{_sysconfdir}/ant.d/*
%endif

%files -n aqute-bndlib -f .mfiles-bndlib
%license LICENSE

%if %{with maven_plugin}
%files -n bnd-maven-plugin -f .mfiles-maven
%endif

%files javadoc -f .mfiles-javadoc
%license LICENSE

%changelog
* Mon Jul 30 2018 Severin Gehwolf <sgehwolf@redhat.com> - 3.5.0-4
- Add requirement on javapackages-tools for bnd script.

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.5.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.5.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Oct 13 2017 Michael Simacek <msimacek@redhat.com> - 3.5.0-1
- Update to upstream version 3.5.0

* Mon Oct 02 2017 Troy Dawson <tdawson@redhat.com> - 3.4.0-3
- Cleanup spec file conditionals

* Sat Sep 23 2017 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.4.0-2
- Remove unneeded javadoc plugin

* Tue Sep 12 2017 Michael Simacek <msimacek@redhat.com> - 3.4.0-1
- Update to upstream version 3.4.0

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.3.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.3.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Oct 10 2016 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.3.0-5
- Don't use legacy Ant artifact coordinates

* Mon Oct 10 2016 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.3.0-4
- Allow conditional builds without Ant tasks

* Mon Oct 10 2016 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.3.0-3
- Allow conditional builds without Maven plugin

* Thu Oct 06 2016 Michael Simacek <msimacek@redhat.com> - 3.3.0-2
- Fix ant.d classpath

* Thu Sep 29 2016 Michael Simacek <msimacek@redhat.com> - 3.3.0-1
- Update to upstream version 3.3.0
- Build against osgi-{core,compendium}

* Tue Sep 27 2016 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.2.0-5
- Add felix-scr-annotations to classpath

* Mon Sep 26 2016 Michael Simacek <msimacek@redhat.com> - 3.2.0-4
- Use felix-annotations

* Wed Sep 14 2016 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.2.0-3
- Build and install Maven plugins
- Resolves: rhbz#1375904

* Wed Jun  1 2016 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.2.0-2
- Install ant.d config files

* Tue May 24 2016 Michael Simacek <msimacek@redhat.com> - 3.2.0-1
- Update to upstream version 3.2.0

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.4.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jul 17 2015 Michael Simacek <msimacek@redhat.com> - 2.4.1-2
- Fix Tool header generation

* Wed Jul 08 2015 Michael Simacek <msimacek@redhat.com> - 2.4.1-1
- Update to upstream version 2.4.1

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.0.363-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu May 14 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.0.363-15
- Disable javadoc doclint

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.0.363-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu May 29 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.0.363-13
- Use .mfiles generated during build

* Fri May 09 2014 Jaromir Capik <jcapik@redhat.com> - 0.0.363-12
- Fixing ambiguous base64 class

* Fri May 09 2014 Gil Cattaneo <puntogil@libero.it> 0.0.363-11
- fix rhbz#991985
- add source compatibility with ant 1.9
- remove and rebuild from source aQute.runtime.jar
- update to current packaging guidelines

* Tue Mar 04 2014 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0.0.363-10
- Use Requires: java-headless rebuild (#1067528)

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.0.363-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.0.363-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.0.363-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Apr 25 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0.0.363-6
- Get rid of unusable eclipse plugins to simplify dependencies

* Fri Mar 02 2012 Jaromir Capik <jcapik@redhat.com> - 0.0.363-5
- Fixing build failures on f16 and later

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.0.363-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Sep 22 2011 Jaromir Capik <jcapik@redhat.com> - 0.0.363-3
- Resurrection of bundled non-class files

* Thu Sep 22 2011 Jaromir Capik <jcapik@redhat.com> - 0.0.363-2
- Bundled classes removed
- jpackage-utils dependency added to the javadoc subpackage

* Wed Sep 21 2011 Jaromir Capik <jcapik@redhat.com> - 0.0.363-1
- Initial version (cloned from aqute-bndlib 0.0.363)
