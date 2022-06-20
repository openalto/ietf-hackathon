#!/bin/bash

COMPOSE_FILE=../docker/docker-compose-with-fts.yml
FTS_NODE=rucio
FTS_HOST=fts
FTSDB_NODE=ftsdb

gen_test_file () {
    local target_se=$1
    local filename=$2
    local filesize=$3
    docker-compose -f $COMPOSE_FILE exec $target_se dd if=/dev/urandom of=/rucio/$filename bs=1M count=$filesize
}

submit_test_transfers () {
    local source_se=$1
    local dest_se=$2
    local filename=$3
    docker-compose -f $COMPOSE_FILE exec $FTS_NODE fts-rest-transfer-submit -v -s https://$FTS_HOST:8446 root://$source_se//rucio/$filename root://$dest_se//rucio/$filename
}

clean_up_storage () {
    local target_se=$1
    docker-compose -f $COMPOSE_FILE exec $target_se bash -c 'rm /rucio/*'
}

gen_batch_files () {
    local target_se=$1
    local filesize=$2
    local filenum=$3
    local start=${4:-1}
    local prefix=${5:-test}
    let end=start+filenum-1

    for i in `seq $start $end`
    do
        gen_test_file $target_se $prefix$i $filesize
    done
}

submit_batch_transfer () {
    local source_se=$1
    local dest_se=$2
    local filenum=$3
    local start=${4:-1}
    local prefix=${5:-test}
    let end=start+filenum-1

    for i in `seq $start $end`
    do
        submit_test_transfers $source_se $dest_se $prefix$i
    done
}

dump_optimizer_hist () {
    local sql_stmt='select * from t_optimizer_evolution where datetime > '"'"$1"'"
    docker-compose -f $COMPOSE_FILE exec $FTSDB_NODE bash -c 'echo "'"$sql_stmt"'" | mysql -u fts --password=fts fts'
}

