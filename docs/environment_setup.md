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
$ git clone -b ietf-hackathon-113 https://github.com/openalto/rucio.git
$ git clone https://github.com/openalto/alto.git
```

> *NOTE*: [`ietf-hackathon-113`][ietf-hackathon-113] is a checkpoint of a
> modified rucio version for demo purpose. The `feature-*` branches will
> include changes to be merged into upstream rucio source code in the future.

[ietf-hackathon-113]: https://github.com/openalto/rucio/tree/ietf-hackathon-113

Build extended docker images for rucio development environment:

``` sh
$ make build-rucio
```

> *NOTE*: This command will build extended docker images for `rucio-dev` and
> `xrootd`. More specifically, the extended docker images will install
> `net-tools` and `iproute` packages on the original images. Because mininet
> requires `ifconfig` and `ip` commands to operate network devices.

Launch all docker containers:

> *NOTE*: You can use either `docker-compose-with-rucio.yml` or
> `docker-compose-with-rucio-monit.yml`. The later one will provide more
> containers for monitoring purpose.

``` sh
$ docker-compose -f docker-compose-with-rucio.yml up -d
[+] Running 18/18
 ⠿ Container xrd3                    Started                       71.6s
 ⠿ Container docker-mininet-1        Started                        8.9s
 ⠿ Container xrd1                    Started                       78.7s
 ⠿ Container rucio                   Started                        9.3s
 ⠿ Container xrd2                    Started                       75.2s
 ⠿ Container xrd4                    Started                       77.3s
 ⠿ Container docker-sflow-1          Started                       25.9s
 ⠿ Container docker-activemq-1       Started                       29.9s
 ⠿ Container docker-fts-1            Started                       60.5s
 ⠿ Container docker-ruciodb-1        Started                       22.1s
 ⠿ Container docker-kibana-1         Started                       22.4s
 ⠿ Container docker-ftsdb-1          Started                       53.3s
 ⠿ Container docker-logstash-1       Started                       58.2s
 ⠿ Container docker-ssh1-1           Started                       31.5s
 ⠿ Container docker-minio-1          Started                       27.1s
 ⠿ Container docker-grafana-1        Started                       37.0s
 ⠿ Container docker-graphite-1       Started                       50.4s
 ⠿ Container docker-elasticsearch-1  Started                       39.5s
```

Then you can start a test topology for those containers:

``` sh
$ docker-compose -f docker-compose-with-rucio-monit.yml exec mininet python3 /utils/rucio_example.py
  .
  .
  .
*** Testing connectivity
rc -> xrd1 xrd2 xrd3 xrd4
xrd1 -> rc xrd2 xrd3 xrd4
xrd2 -> rc xrd1 xrd3 xrd4
xrd3 -> rc xrd1 xrd2 xrd4
xrd4 -> rc xrd1 xrd2 xrd3
*** Results: 0% dropped (20/20 received)
*** Running CLI
*** Starting CLI:
containernet>
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

After the topology built, you can access the rucio node and RSE nodes from the
mininet shell.

Then you can set up the demo rucio datasets and replicas as follows:

```sh
containernet> rc tools/run_tests_docker.sh -ir
 .
 .
 .
containernet> rc rucio list-rules --account root
ID                                ACCOUNT    SCOPE:NAME      STATE[OK/REPL/STUCK]    RSE_EXPRESSION    COPIES    EXPIRES (UTC)    CREATED (UTC)
--------------------------------  ---------  --------------  ----------------------  ----------------  --------  ---------------  -------------------
f732a820108b4fe59902fbbb8e08850a  root       test:file1      OK[1/0/0]               XRD1              1                          2022-03-16 12:54:59
a7675fa9cbbe45c8ae130e442995afaa  root       test:file2      OK[1/0/0]               XRD1              1                          2022-03-16 12:56:55
07724ab6c06640138db0f145ea78616b  root       test:file3      OK[1/0/0]               XRD2              1                          2022-03-16 12:58:37
f589161cd00b4cb1b0eda9d7d2479617  root       test:file4      OK[1/0/0]               XRD2              1                          2022-03-16 13:00:20
d5635b9d97ae42b59b64bd5215bc6e20  root       test:container  REPL[0/4/0]             XRD3              1                          2022-03-16 13:02:17
```

You can also access those nodes using `docker exec` directly:

```sh
$ docker-compose -f docker-compose-with-rucio-monit.yml exec rucio /bin/bash
[root@cf3ad7061320 rucio]#
```

Let's add another replica rule to replicate all the files on XRD4:

```sh
[root@cf3ad7061320 rucio]# rucio add-rule test:container 1 XRD4
```

Now, each test files will have 3 replicas. But the replicas on XRD3 and XRD4
are still held by Rucio:

```sh
[root@cf3ad7061320 rucio]# rucio list-rules --account root
ID                                ACCOUNT    SCOPE:NAME      STATE[OK/REPL/STUCK]    RSE_EXPRESSION    COPIES    EXPIRES (UTC)    CREATED (UTC)
--------------------------------  ---------  --------------  ----------------------  ----------------  --------  ---------------  -------------------
f732a820108b4fe59902fbbb8e08850a  root       test:file1      OK[1/0/0]               XRD1              1                          2022-03-16 12:54:59
a7675fa9cbbe45c8ae130e442995afaa  root       test:file2      OK[1/0/0]               XRD1              1                          2022-03-16 12:56:55
07724ab6c06640138db0f145ea78616b  root       test:file3      OK[1/0/0]               XRD2              1                          2022-03-16 12:58:37
f589161cd00b4cb1b0eda9d7d2479617  root       test:file4      OK[1/0/0]               XRD2              1                          2022-03-16 13:00:20
d5635b9d97ae42b59b64bd5215bc6e20  root       test:container  REPL[0/4/0]             XRD3              1                          2022-03-16 13:02:17
68176892d26a4801829b5d1cd98cc5c1  root       test:container  REPL[0/4/0]             XRD4              1                          2022-03-16 14:25:07
```

We need to start daemons to handle the replica rules:

```sh
[root@cf3ad7061320 rucio]# run_daemons
```

Wait for a while, all the replicas will be transferred:

```sh
containernet> rc rucio list-rules --account root
ID                                ACCOUNT    SCOPE:NAME      STATE[OK/REPL/STUCK]    RSE_EXPRESSION    COPIES    EXPIRES (UTC)    CREATED (UTC)
--------------------------------  ---------  --------------  ----------------------  ----------------  --------  ---------------  -------------------
f732a820108b4fe59902fbbb8e08850a  root       test:file1      OK[1/0/0]               XRD1              1                          2022-03-16 12:54:59
a7675fa9cbbe45c8ae130e442995afaa  root       test:file2      OK[1/0/0]               XRD1              1                          2022-03-16 12:56:55
07724ab6c06640138db0f145ea78616b  root       test:file3      OK[1/0/0]               XRD2              1                          2022-03-16 12:58:37
f589161cd00b4cb1b0eda9d7d2479617  root       test:file4      OK[1/0/0]               XRD2              1                          2022-03-16 13:00:20
d5635b9d97ae42b59b64bd5215bc6e20  root       test:container  OK[4/0/0]               XRD3              1                          2022-03-16 13:02:17
68176892d26a4801829b5d1cd98cc5c1  root       test:container  OK[4/0/0]               XRD4              1                          2022-03-16 14:25:07
```

> *NOTE*: The transfer will usually not take too long. It usually can be
> finished in 5 min. If you feel it takes too long, you make manually run the
> schedule daemon to make sure the state be synchronized:
>
> ```sh
> containernet> rc rucio-conveyor-poller --run-once --older-than 0
> containernet> rc rucio-conveyor-finisher --run-once
> ```

> *NOTE*: Learn more details from the [Rucio Documentation](http://rucio.cern.ch/documentation/setting_up_demo).

### Testing Rucio with ALTO

Since you have learnt how to set up the environment. Let's see how to test your
changes to Rucio and ALTO code.

If you want Rucio to use ALTO client library, you should enter the rucio
container and install the ALTO client first:

```sh
$ docker-compose -f docker-compose-with-rucio-monit.yml exec rucio /bin/bash
[root@cf3ad7061320 rucio]# cd /opt/alto
[root@cf3ad7061320 alto]# pip install .
```

> *NOTE*: Every time when you modified the ALTO client library code, if you
> want to make it effective, you should repeat the commands above.

Then, you can start a test ALTO server inside the rucio container:

```sh
[root@cf3ad7061320 alto]# cd /opt/alto/etc
[root@cf3ad7061320 etc]# cp alto.conf.test alto.conf
[root@cf3ad7061320 tools]# cd /opt/alto/tools
[root@cf3ad7061320 tools]# python server.py
* Serving Flask app "alto-testserver" (lazy loading)
* Environment: production
  WARNING: This is a development server. Do not use it in a production deployment.
  Use a production WSGI server instead.
* Debug mode: off
* Running on http://127.0.0.1:8181/ (Press CTRL+C to quit)
```

Then you can switch to another rucio container or shell to test the ALTO-based
replica sorter:

```sh
containernet> rc rucio list-file-replicas --sort=alto --metalink test:file1
<?xml version="1.0" encoding="UTF-8"?>
<metalink xmlns="urn:ietf:params:xml:ns:metalink">
 <file name="file1">
  <identity>test:file1</identity>
  <hash type="adler32">0f837543</hash>
  <hash type="md5">ed645d9433d30e458d6f757749206747</hash>
  <size>10485760</size>
  <glfn name="/atlas/rucio/test:file1"></glfn>
  <url location="XRD3" domain="wan" priority="1" client_extract="false">root://xrd3:1096//rucio/test/80/25/file1</url>
  <url location="XRD4" domain="wan" priority="2" client_extract="false">root://xrd4:1097//rucio/test/80/25/file1</url>
  <url location="XRD1" domain="wan" priority="3" client_extract="false">root://xrd1:1094//rucio/test/80/25/file1</url>
 </file>
</metalink>

containernet> rc rucio download --dir /tmp --replica-sort alto test:file1
2022-03-17 01:39:53,721 INFO    Processing 1 item(s) for input
2022-03-17 01:39:53,880 INFO    No preferred protocol impl in rucio.cfg: No section: 'download'
2022-03-17 01:39:53,880 INFO    Using main thread to download 1 file(s)
2022-03-17 01:39:53,880 INFO    Preparing download of test:file1
2022-03-17 01:39:53,897 INFO    Trying to download with root and timeout of 80s from XRD3: test:file1
2022-03-17 01:39:55,492 INFO    Using PFN: root://xrd3:1096//rucio/test/80/25/file1
2022-03-17 01:40:41,105 INFO    File test:file1 successfully downloaded. 10.486 MB in 44.73 seconds = 0.23 MBps
----------------------------------
Download summary
----------------------------------------
DID test:file1
Total files (DID):                            1
Total files (filtered):                       1
Downloaded files:                             1
Files already found locally:                  0
Files that cannot be downloaded:              0
```

You can also modify the Rucio code. After you did this, you may need to restart
the containers to make it effective. You need to stop the mininet first, and
then restart the containers, and the rebuild the mininet topology:

```sh
containernet> <CTRL-D>
$ docker-compose -f docker-compose-with-rucio-monit.yml restart
 .
 .
 .
$ docker-compose -f docker-compose-with-rucio-monit.yml exec mininet python3 /utils/rucio_example.py
```

### Monitoring Traffic

The environment has already integrate [sflow-rt]. To enable traffic monitoring,
it is quite simple. You can simply use [mininet-dashboard] to show the
real-time traffic.

Use the following command to install the mininet-dashboard:

```sh
$ docker-compose -f docker-compose-with-rucio-monit.yml exec sflow /sflow-rt/get-app.sh sflow-rt mininet-dashboard
```

Then you can go to your web browser to see the dashboard at
<http://localhost:8008/app/mininet-dashboard/html/>.

[sflow-rt]: https://sflow-rt.com/download.php

[mininet-dashboard]: https://github.com/sflow-rt/mininet-dashboard

### Creating custom topology using G2-Mininet extension

Build the docker image for containernet with G2-Mininet extension:

```sh
$ make build-g2-mininet
```

TBD.
