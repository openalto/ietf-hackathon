# Enviroment Setup

This is a guide to help developers to set up the basic development environment
locally.

## Prerequisite

Make sure you have the following required tools and software packages installed:

- `docker`: <https://docs.docker.com/engine/install/>
- `docker-compose`: <https://docs.docker.com/compose/install/>
- `openswitch-switch`: <https://www.openvswitch.org/download/>

## Building Basic Docker Containers

First, clone this repo to your own machine:

``` sh
$ git clone https://github.com/openalto/ietf-hackathon.git
$ cd ietf-hackathon
```

Then enter the `docker` directory and build all the containers

``` sh
$ cd docker
$ docker-compose build
```

## Using Containerized Development Environment

Start all the docker containers:

``` sh
$ docker-compose up -d
[+] Running 4/4
 ⠿ Network docker_default         Created           0.9s
 ⠿ Container docker-g2-mininet-1  Started           16.5s
 ⠿ Container docker-odl-1         Started           14.4s
 ⠿ Container docker-sflow-1       Started           15.5s
```

### Deal with OpenDaylight Controller

Execute OpenDaylight from the `odl` container:

``` sh
$ docker-compose exec odl /opt/opendaylight/bin/client
```

Then you will enter the OpenDaylight shell:

``` sh
opendaylight-user>
```

You can check all the features which has been already installed:

``` sh
opendaylight-user> feature:list -i
```

### Deal with ALTO Server

Let's install the `odl-alto-manual-maps` feature to test the basic functionality
of the ALTO server:

``` sh
opendaylight-user> feature:install odl-alto-manual-maps
```

First, verify all the required features were installed successfully:

``` sh
opendaylight-user> feature:list -i | grep odl-alto-
odl-alto-manual-maps                 │ 0.6.4            │ x        │ Started │ odl-alto-0.6.4                       │ OpenDaylight :: alto :: Manual Maps
odl-alto-standard-service-models     │ 0.6.4            │          │ Started │ odl-alto-standard-service-models     │ OpenDaylight :: alto :: Standard Service Model
odl-alto-standard-types              │ 0.6.4            │          │ Started │ odl-alto-standard-types              │ OpenDaylight :: alto :: Standard Types
odl-alto-simpleird                   │ 0.6.4            │          │ Started │ odl-alto-simpleird                   │ OpenDaylight :: alto :: Simple IRD
odl-alto-resourcepool                │ 0.6.4            │          │ Started │ odl-alto-resourcepool                │ OpenDaylight :: alto :: Resourcepool
odl-alto-northbound                  │ 0.6.4            │          │ Started │ odl-alto-northbound                  │ OpenDaylight :: alto :: Northbound
```

Then you can log out the OpenDaylight shell, and run a simple test for default ALTO IRD:

``` sh
opendaylight-user> logout
$ curl -u admin:admin -s http://localhost:8181/alto/simpleird/default | python3 -m json.tool
{
    "meta": {},
    "resources": {}
}
```

### Deal with Mininet

Before you run the mininet, you should make sure you insert the `openvswitch`
kernel module into your host OS kernel. You can run the following command to
check it:

``` sh
$ lsmod | grep openvswitch
```

If nothing there, you should run the following command to insert the module:

``` sh
$ modprob openvswitch
```

After that, you can start a standard mininet shell from the `g2-mininet`
container:

``` sh
$ docker-compose exec g2-mininet /bin/bash
root# mn
  .
  .
  .
mininet>
```

## Develop the Hackathon Project

TODO: Install ALTO python library

TODO: Install modified rucio
