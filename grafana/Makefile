all: grafana-$(VER)/ \
	 grafana-vendor-$(VER).tar.xz \
	 grafana-webpack-$(VER).tar.gz

grafana-$(VER)/: grafana-$(VER).tar.gz
	tar xfz grafana-$(VER).tar.gz
	cd grafana-$(VER) && shopt -s nullglob && \
		for patch in ../*.patch; do patch -p1 < $$patch; done && \
		npm install

grafana-$(VER).tar.gz:
	wget https://github.com/grafana/grafana/archive/v$(VER)/grafana-$(VER).tar.gz

grafana-vendor-$(VER).tar.xz: grafana-$(VER)/
	# Go
	cd grafana-$(VER) && go mod vendor -v
	awk '$$2~/^v/ && $$4 != "indirect" {print "Provides: bundled(golang(" $$1 ")) = " substr($$2, 2)}' grafana-$(VER)/go.mod | \
		sed -E 's/=(.*)-(.*)-(.*)/=\1-\2.\3/g' > $@.manifest

	# Node.js
	cd grafana-$(VER) && yarn install --pure-lockfile
	# Remove files with licensing issues
	find grafana-$(VER) -type d -name 'node-notifier' -prune -exec rm -r {} \;
	find grafana-$(VER) -name '*.exe' -delete
	./list_bundled_nodejs_packages.py grafana-$(VER)/ >> $@.manifest

	# Create tarball
	XZ_OPT=-9 tar cfJ $@ \
		grafana-$(VER)/vendor \
		$$(find grafana-$(VER) -type d -name "node_modules" -prune)

grafana-webpack-$(VER).tar.gz: grafana-$(VER)/
	cd grafana-$(VER) && \
		yarn install --pure-lockfile && \
		../build_frontend.sh

	tar cfz $@ grafana-$(VER)/public/build grafana-$(VER)/public/views grafana-$(VER)/plugins-bundled

clean:
	rm -rf *.tar.gz *.tar.xz *.manifest *.rpm grafana-*/
