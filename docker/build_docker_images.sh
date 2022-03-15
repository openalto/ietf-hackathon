#!/bin/bash

docker build -t openalto/rucio-dev rucio-containers/dev/
docker build -t openalto/xrootd rucio-containers/xrootd/
docker build -t openalto/g2-mininet g2-mininet/

