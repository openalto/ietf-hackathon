# FTS Test

Check [`environment_setup.md`](environment_setup.md) for prerequisite.

## Docker Environment Setup

```
$ cd docker
$ docker-compose -f docker-compose-with-fts.yml up -d
```

## Network Topology Setup

*Test network connectivity*
```
$ docker-compose -f docker-compose-with-fts.yml exec mininet python3 /utils/rucio_example.py
```

*Test network connectivity(topology from .yml workflow file)*
```
$ docker-compose -f docker-compose-with-fts.yml exec mininet python3 /utils/rucio_dynamic_example.py --str "$(cat ../etc/ietf-hackathon-114-test2.yml)"
```

## FTS Usage

```
$ cd ../utils
$ . fts_utils.sh
$ init_fts
$ gen_batch_files xrd1 10 48 1 testfile   # generate 48x10M files (testfile1 to testfile48)
$ config_fts_link root://xrd1 '*' 2 8    # configure working range for link set xrd1 -> *
$ config_optimizer root://xrd1 root://xrd2 8    # preconfigure active of xrd1 -> xrd2 to 8
$ config_optimizer root://xrd1 root://xrd3 2    # preconfigure active of xrd1 -> xrd3 to 2
$ submit_batch_transfer xrd1 xrd3 48 1 testfile
$ submit_batch_transfer xrd1 xrd2 48 1 testfile
$ dump_optimizer_hist $(date --rfc-3339=date)
```

## Known Issues

When too many concurrent fts-url-copy processes are running, there is high
probability getting the "Operation expired" error from XrootD. (See details in
<https://github.com/openalto/ietf-hackathon/issues/53>)

## Build Your Own FTS

```
$ git clone https://github.com/cern-fts/fts3 [PATH_TO_FTS_REPO]

... Modify FTS source code ...

$ cd ../docker
$ docker build -t fts-dev rucio-containers/fts-dev
$ docker run -ti --rm -v <PATH_TO_FTS_REPO>:/fts3 fts-dev bash
[root@22fa4d38704e /]# cd /fts3
[root@22fa4d38704e /]# mkdir -p build
[root@22fa4d38704e /]# cd build
[root@22fa4d38704e /]# cmake /fts3 -DALLBUILD=ON
[root@22fa4d38704e /]# make
```

## Setup Environment using Your Own FTS

Modify the docker compose YAML file and mount the following binary files to the
fts container:

```
  fts:
    image: docker.io/rucio/fts
    network_mode: "service:rucio"
    volumes:
      - ./fts3config:/etc/fts3/fts3config:Z
      - <path-to-your-fts-repo>/build/src/server/libfts_server_lib.so.3.11.3:/usr/lib64/libfts_server_lib.so:z
      - <path-to-your-fts-repo>/build/src/server/fts_server:/usr/sbin/fts_server:z
```

> NOTE: You should mount all the binary files under directories that you
> modified. e.g., If you modified source code under `fts3/src/config`, you
> should also mount all the executable binary and dynamic libraries under
> `fts3/build/src/config`.

