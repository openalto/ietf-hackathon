RUCIO_IMAGE := fno2010/rucio-dev
XROOTD_IMAGE := fno2010/xrootd:5.4.2
FTS_IMAGE := fno2010/fts:3.12.0
MN_IMAGE := fno2010/g2-mininet:minimal

prebuilt-rucio:
ifeq ($(shell docker images -q -f 'reference=openalto/rucio-dev'))
	docker tag openalto/rucio-dev openalto/rucio-dev:build
	docker rmi openalto/rucio-dev
endif
	docker pull $(RUCIO_IMAGE)
	docker tag openalto/rucio-dev $(RUCIO_IMAGE)

prebuilt-xrootd:
ifeq ($(shell docker images -q -f 'reference=openalto/xrootd'))
	docker tag openalto/xrootd openalto/xrootd:build
	docker rmi openalto/xrootd
endif
	docker pull $(XROOTD_IMAGE)
	docker tag openalto/xrootd $(XROOTD_IMAGE)

prebuilt-fts:
ifeq ($(shell docker images -q -f 'reference=openalto/fts'))
	docker tag openalto/fts openalto/fts:build
	docker rmi openalto/fts
endif
	docker pull $(FTS_IMAGE)
	docker tag openalto/fts $(FTS_IMAGE)

prebuilt-g2-mininet:
ifeq ($(shell docker images -q -f 'reference=openalto/g2-mininet:minimal'))
	docker tag openalto/g2-mininet:minimal openalto/g2-mininet:minimal-build
	docker rmi openalto/g2-mininet:minimal
endif
	docker pull $(MN_IMAGE)
	docker tag openalto/g2-mininet:minimal $(MN_IMAGE)
