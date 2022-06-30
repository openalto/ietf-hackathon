# FTS Test

## Docker Environment Setup

```
$ cd docker
$ docker-compose -f docker-compose-with-fts.yml up -d
```

## Network Topology Setup

```
$ docker-compose -f docker-compose-with-fts.yml exec mininet python3 /util/rucio_example.py
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
$ dump_optimizer_hist $(date --frc-3339=date)
```

