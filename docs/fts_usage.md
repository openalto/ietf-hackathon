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
$ gen_batch_files xrd1 10 24 1 testfile
$ submit_batch_transfer xrd1 xrd2 24 1 testfile
$ dump_optimizer_hist $(date --frc-3339)
$ submit_batch_transfer xrd1 xrd3 16 1 testfile
$ dump_optimizer_hist $(date --frc-3339)
```

