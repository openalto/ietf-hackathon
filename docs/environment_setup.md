# Enviroment Setup

This is a guide to help set up the basic development environment of ALTO over OpenDayliught on a 
local machine.

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

Then enter the `docker` directory and build all the containers:

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

### Launching the OpenDaylight Controller

Execute OpenDaylight from the `odl` container:

``` sh
$ docker-compose exec odl /opt/opendaylight/bin/client
```

Then you will enter the OpenDaylight shell:

``` sh
opendaylight-user@root>
```

You can check all the features which has been already installed:

``` sh
opendaylight-user@root> feature:list -i
```

### Starting & Testing the ALTO Server

Install the `odl-alto-manual-maps` feature to test the basic functionality
of the ALTO server:

``` sh
opendaylight-user@root> feature:install odl-alto-core odl-alto-manual-maps
```

First, verify all the required features are installed successfully:

``` sh
opendaylight-user@root> feature:list -i | grep odl-alto-
odl-alto-manual-maps                 │ 0.6.4            │ x        │ Started │ odl-alto-0.6.4                       │ OpenDaylight :: alto :: Manual Maps
odl-alto-standard-service-models     │ 0.6.4            │          │ Started │ odl-alto-standard-service-models     │ OpenDaylight :: alto :: Standard Service Model
odl-alto-standard-types              │ 0.6.4            │          │ Started │ odl-alto-standard-types              │ OpenDaylight :: alto :: Standard Types
odl-alto-simpleird                   │ 0.6.4            │          │ Started │ odl-alto-simpleird                   │ OpenDaylight :: alto :: Simple IRD
odl-alto-resourcepool                │ 0.6.4            │          │ Started │ odl-alto-resourcepool                │ OpenDaylight :: alto :: Resourcepool
odl-alto-core                        │ 0.6.4            │ x        │ Started │ odl-alto-core                        │ OpenDaylight :: alto :: Core
odl-alto-northbound                  │ 0.6.4            │          │ Started │ odl-alto-northbound                  │ OpenDaylight :: alto :: Northbound
odl-alto-standard-northbound-route   │ 0.6.4            │          │ Started │ odl-alto-standard-northbound-route   │ OpenDaylight :: alto :: Standard Northbound Route
```

Then you can log out the OpenDaylight shell, and run a simple test for default
the ALTO [Information Resource Directory (IRD)](https://www.rfc-editor.org/rfc/rfc7285.html#section-9):

> *NOTE*: The default configured authorization is (username: `admin`, password:
`admin`). It is provided by the Authentication, Authorization and Accounting
(AAA) plugin of OpenDaylight. You can change the authorization later by
following the [AAA User
Guide](https://docs.opendaylight.org/en/stable-oxygen/user-guide/authentication-and-authorization-services.html).

``` sh
opendaylight-user@root> logout
$ curl -u admin:admin -s http://localhost:8181/alto/simpleird/default | python3 -m json.tool
{
    "meta": {},
    "resources": {}
}
```

You can see the IRD is empty right now. Then let's add an [example default network map](../templates/alto_manual_networkmap_config.template):

``` sh
$ curl -u admin:admin -X PUT -H "Content-Type: application/json" -d "$(cat ../templates/alto_manual_networkmap_config.template)" http://localhost:8181/restconf/config/alto-manual-maps:config-context/00000000-0000-0000-0000-000000000000/resource-network-map/default-networkmap

HTTP/1.1 201 Created
Set-Cookie: JSESSIONID=qjwnyyqn8098jlb1q2vkhu3z;Path=/restconf
Expires: Thu, 01 Jan 1970 00:00:00 GMT
Set-Cookie: rememberMe=deleteMe; Path=/restconf; Max-Age=0; Expires=Tue, 08-Mar-2022 02:27:30 GMT
Content-Length: 0
```

The IRD will be automatically updated:

``` sh
$ curl -u admin:admin -s http://localhost:8181/alto/simpleird/default | python3 -m json.tool
{
    "meta": {
        "cost-types": {}
    },
    "resources": {
        "default-networkmap": {
            "media-type": "application/alto-networkmap+json",
            "uri": "http://172.26.0.2:8181/alto/networkmap/default-networkmap"
        }
    }
}
```

Now, the network map can be got via ALTO protocol:

``` sh
{
    "meta": {
        "vtag": {
            "resource-id": "default-networkmap",
            "tag": "da65eca2eb7a10ce8b059740b0b2e3f8"
        }
    },
    "network-map": {
        "PID0": {
            "ipv4": [
                "0.0.0.0/0"
            ],
            "ipv6": [
                "::/0"
            ]
        },
        "PID2": {
            "ipv4": [
                "198.51.100.128/25"
            ]
        },
        "PID1": {
            "ipv4": [
                "198.51.100.0/25",
                "192.0.2.0/24"
            ]
        }
    }
}
```

Then add an [example default cost map](../templates/alto_manual_costmap_config.template):

``` sh
$ curl -u admin:admin -X PUT -H "Content-Type: application/json" -d "$(cat ../templates/alto_manual_networkmap_config.template)" http://localhost:8181/restconf/config/alto-manual-maps:config-context/00000000-0000-0000-0000-000000000000/resource-cost-map/default-costmap

HTTP/1.1 201 Created
Set-Cookie: JSESSIONID=1n6dris5mngy51hdis0cpebhp7;Path=/restconf
Expires: Thu, 01 Jan 1970 00:00:00 GMT
Set-Cookie: rememberMe=deleteMe; Path=/restconf; Max-Age=0; Expires=Tue, 08-Mar-2022 02:36:39 GMT
Content-Length: 0
```

The cost map will be added into the IRD:

``` sh
$ curl -u admin:admin -s http://localhost:8181/alto/simpleird/default | python3 -m json.tool
{
    "meta": {
        "cost-types": {}
    },
    "resources": {
        "default-costmap": {
            "uses": [
                "default-networkmap"
            ],
            "media-type": "application/alto-costmap+json",
            "uri": "http://172.26.0.2:8181/alto/costmap/default-costmap"
        },
        "default-networkmap": {
            "media-type": "application/alto-networkmap+json",
            "uri": "http://172.26.0.2:8181/alto/networkmap/default-networkmap"
        }
    }
}
```

You can get cost map via ALTO protocol:

``` sh
{
    "meta": {
        "dependent-vtags": [
            {
                "resource-id": "default-networkmap",
                "tag": "da65eca2eb7a10ce8b059740b0b2e3f8"
            }
        ],
        "cost-type": {
            "cost-mode": "numerical",
            "cost-metric": "hopcount"
        },
        "vtag": {
            "resource-id": "default-costmap",
            "tag": "3ee2cb7e8d63d9fab71b9b34cbf76443"
        }
    },
    "cost-map": {
        "PID2": {
            "PID0": "15",
            "PID2": "1",
            "PID1": "5"
        },
        "PID0": {
            "PID2": "15",
            "PID1": "10"
        },
        "PID1": {
            "PID0": "10",
            "PID2": "5",
            "PID1": "1"
        }
    }
}
```

### Dealing with Mininet

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

## Developing Hackathon Project

### Running Container for ALTO integrated Rucio

Clone codebase for Rucio with ALTO integration:

``` sh
$ git clone -b alto-integration https://github.com/openalto/rucio.git
```

> *NOTE*: As the `alto-integration` branch may not be stable, you can first
> switch to the `master` branch to do some simple tests.

Build extended docker images for rucio development environment:

``` sh
$ ./build_docker_images.sh
```

> *NOTE*: This command will build extended docker images for `rucio-dev` and
> `xrootd`. More specifically, the extended docker images will install
> `net-tools` and `iproute` packages on the original images. Because mininet
> requires `ifconfig` and `ip` commands to operate network devices.

Launch all docker containers:

``` sh
$ docker-compose -f docker-compose-with-rucio.yml up -d
[+] Running 15/15
⠿ Network docker_default       Created                     0.7s
⠿ Container rucio              Started                     88.8s
⠿ Container docker-mininet-1   Started                     75.1s
⠿ Container xrd4               Started                     87.7s
⠿ Container xrd1               Started                     71.7s
⠿ Container xrd2               Started                     78.4s
⠿ Container xrd3               Started                     86.8s
⠿ Container docker-sflow-1     Started                     44.9s
⠿ Container docker-activemq-1  Started                     81.5s
⠿ Container docker-ruciodb-1   Started                     78.2s
⠿ Container docker-ftsdb-1     Started                     78.9s
⠿ Container docker-graphite-1  Started                     83.7s
⠿ Container docker-fts-1       Started                     76.7s
⠿ Container docker-minio-1     Started                     80.3s
⠿ Container docker-ssh1-1      Started                     77.0s
```

Then you can start a test topology for those containers:

``` sh
$ docker-compose -f docker-compose-with-rucio.yml exec mininet python3 /utils/rucio_example.py
```

This will build the following topology:

```
              Rucio
      1Mbps    |     5Mbps
      25ms     |     25ms
  s1 --------- s3 ----------- s4 -- XRD3
  |            |              |
  |            | 25ms         | 50ms
  |            | 1Mbps        | 2Mbps
  |            |              |
 XRD1          s2 -- XRD2     s5 -- XRD4
```

> *NOTE*: Learn more details from the [Rucio Documentation](http://rucio.cern.ch/documentation/setting_up_demo).

### Testing Rucio with ALTO

TBD.
