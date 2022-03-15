
build-rucio:
ifeq ($(shell docker images openalto/rucio-dev:latest -q),)
	# docker build -t openalto/rucio-dev rucio-containers/dev/
else
	@echo "Image openalto/rucio-dev exists."
endif
ifeq ($(shell docker images openalto/xrootd:latest -q),)
	# docker build -t openalto/xrootd rucio-containers/xrootd/
else
	@echo "Image openalto/xrootd exists."
endif

build-g2-mininet:
ifeq ($(shell docker images openalto/g2-mininet:latest -q),)
	docker build -t openalto/g2-mininet g2-mininet/
else
	@echo "Image openalto/g2-mininet exists."
endif

build: build-rucio build-g2-mininet

update-rucio:
	docker build -t openalto/rucio-dev rucio-containers/dev/
	docker build -t openalto/xrootd rucio-containers/xrootd/

update-g2-mininet:
	docker build -t openalto/g2-mininet g2-mininet/

update: upate-rucio update-g2-mininet

