# Docker Containers

- OpenDaylight with ALTO
- G2-Mininet
- sflow-rt

``` sh
docker-compose build

docker-compose up -d

docker-compose exec odl /opt/opendaylight/bin/client

# enter opendaylight shell to install features

docker-compose exec g2-mininet /bin/bash

# start g2-mininet
```

