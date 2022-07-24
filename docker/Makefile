
build-rucio:
ifeq ($(shell docker images openalto/rucio-dev:latest -q),)
	docker build -t openalto/rucio-dev rucio-containers/dev/
else
	@echo "Image openalto/rucio-dev exists. You can run `make update-rucio` to rebuild the image."
endif
ifeq ($(shell docker images openalto/xrootd:latest -q),)
	docker build -t openalto/xrootd rucio-containers/xrootd/
else
	@echo "Image openalto/xrootd exists. You can run `make update-rucio` to rebuild the image."
endif

build-g2-mininet:
ifeq ($(shell docker images openalto/g2-mininet:latest -q),)
	docker build -t openalto/g2-mininet g2-mininet/
else
	@echo "Image openalto/g2-mininet exists."
endif

build-g2-mininet-minimal:
ifeq ($(shell docker images openalto/g2-mininet:minimal -q),)
	docker build -t openalto/g2-mininet:minimal -f g2-mininet/Dockerfile.minimal g2-mininet/
else
	@echo "Image openalto/g2-mininet exists."
endif

build: build-rucio build-g2-mininet-minimal

update-rucio:
	docker build -t openalto/rucio-dev rucio-containers/dev/
	docker build -t openalto/xrootd rucio-containers/xrootd/

update-g2-mininet:
	docker build -t openalto/g2-mininet g2-mininet/

update-g2-mininet-minimal:
	docker build -t openalto/g2-mininet:minimal -f g2-mininet/Dockerfile.minimal g2-mininet/

update: upate-rucio update-g2-mininet-minimal

