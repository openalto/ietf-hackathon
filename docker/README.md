# Docker Containers for IETF Hackathon

This directory provides all the docker containers for development and demo.

There are four docker compose files for different purposes:

- [`docker-compose.yml`](./docker-compose.yml):
  simple functionality test for ALTO server.
- [`docker-compose-test-containernet.yml`](./docker-compose-test-containernet.yml):
  simple functionality test for mininet topology setup with containerized hosts.
- [`docker-compose-with-rucio.yml`](./docker-compose-with-rucio.yml):
  basic development and test environment for Rucio and ALTO integration.
- [`docker-compose-with-rucio-monit.yml`](./docker-compose-with-rucio-monit.yml):
  comprehensive development and demo environment for Rucio and ALTO integration.

To setup a demo environment, you can use either `docker-compose-with-rucio.yml`
or `docker-compose-with-rucio-monit.yml`. See more details in our [Environment
Setup Documentation](../docs/environment_setup.md).

## Container Environment Description

### [`docker-compose-with-rucio.yml`](./docker-compose-with-rucio.yml)

It provides the following containers:

| Service/Container Name  | Scope      | Short Description                                 |
| ----------------------- | ------     | ------------------                                |
| mininet                 | Mininet    | Extended mininet container for network simulation |
| sflow                   | Mininet    | Network flow sampling and monitoring              |
| odl                     | ALTO       | ALTO server over OpenDaylight controller          |
| rucio                   | Rucio      | Basic Rucio components                            |
| ruciodb                 | Rucio      | ProgresSQL database for Rucio                     |
| fts                     | Rucio      | File transfer system for Rucio                    |
| ftsdb                   | Rucio      | MySQL database for fts                            |
| activemq                | Rucio      | Message queue for Rucio and fts scheduler         |
| xrd{i}                  | Storage    | Xrootd storage node as Rucio [RSE]                |
| ssh{i}                  | Storage    | SSH storage node as Rucio [RSE]                   |
| minio                   | Storage    | MinIO storage node as Rucio [RSE]                 |
| graphite                | Monitoring | Graphtie server for Rucio internal monitoring     |

[RSE]: http://rucio.cern.ch/documentation/rucio_storage_element

### [`docker-compose-with-rucio-monit.yml`](./docker-compose-with-rucio-monit.yml)

Besides the containers above, it also provides the following additional containers:

| Service/Container Name  | Scope      | Short Description                                                    |
| ----------------------- | ------     | ------------------                                                   |
| elasticsearch           | Monitoring | ElasticSearch engine for more complicated monitoring data processing |
| kibana                  | Monitoring | Kibana dashboard for customized visualization                        |
| logstash                | Monitoring | Data processing pipeline for ElasticSearch                           |
| grafana                 | Monitoring | Another dashboard for visualization                                  |

## Container Environment Usage

You can pick proper compose file to set up the container environment:

``` sh
$ docker-compose -f <DOCKER_COMPOSE_FILE> up -d

$ docker-compose -f <DOCKER_COMPOSE_FILE> exec <SERVICE_NAME> <COMMAND>
```

More details can be found in the [Environment Setup
Documentation](../docs/environment_setup.md).

