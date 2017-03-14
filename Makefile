
setup:
	sudo yum install \
	cmake \
	irrlict-devel \
	bzip2-devel \
	gettext-devel \
	jthread-devel \
	sqlite-devel \
	libpng-devel \
	libjpeg-turbo-devel \
	libXxf86vm \
	mesa-libGL-devel \
	desktop-file-utils

rpm:
	rpmbuild \
        -D"_topdir `pwd`" \
	-D"_sourcedir `pwd`" \
	-D"_specdir `pwd`" \
	-bb minetest.spec

rpm-install:
	sudo yum install -y RPMS/x86_64/*.rpm

rpm-uninstall:
	sudo yum remove -y minetest*

clean:
	rm -rf SRPMS RPMS BUILD BUILDROOT

sources:
	spectool -g minetest.spec	
