# coding:utf8
# usage：python generate-docker-compose.py [path-to-workflow-config]
import argparse
import os.path
import subprocess

import yaml

fn = '../etc/input.yml'
VALID_HOST_TYPES = ['rucio', 'xrd']
VALID_STATIC_TYPES = ['fts']

RUCIO_PREFIX_PATH = '../common/rucio'
ALTO_PREFIX_PATH = '../common/alto'
FTS_PREFIX_PATH = '../common/fts'

RUCIO_CERTS_PATH = os.path.join(RUCIO_PREFIX_PATH, 'etc/certs')
RUCIO_CERTS_KEY = os.path.join(RUCIO_CERTS_PATH, 'rucio_ca.key.pem')
RUCIO_CERTS_CA = os.path.join(RUCIO_CERTS_PATH, 'rucio_ca.pem')
PASSPHRASE = {
    'key': 'PASSPHRASE',
    'val': 123456
}

RUCIO_PORTS = [
    "127.0.0.1:8443:443",
    "127.0.0.1:5432:5432",
    "127.0.0.1:8080:80",
    "127.0.0.1:8446:8446",
    "127.0.0.1:8449:8449",
    "127.0.0.1:3306:3306",
    "127.0.0.1:9000:9000",
    "127.0.0.1:61613:61613",
    "127.0.0.1:2222:22"
]
RUCIO_ENVS = [
    'X509_USER_CERT=/opt/rucio/etc/usercert.pem',
    'X509_USER_KEY=/opt/rucio/etc/userkey.pem',
    'RDBMS=postgres14'
]
XRD_ENVS = ['XRDPORT=1094']
XRD_CAP_ADD = ['NET_ADMIN']

IMAGES = {
    'rucio': 'openalto/rucio-dev',
    'xrd': 'openalto/xrootd',
}
XRD_CLIENT_CONF_FILEPATH = '../common/xrootd/client.conf'


def generate(filepath):
    """
    :param filepath:
    :return:
    """
    with open(filepath, 'r') as f:
        cfg = yaml.safe_load(f)
        check_config(cfg)
        dynamic_services, static_services, xrd_name_list = parse_cfg(cfg)
        # print(dynamic_services)
        # print(static_services)
        dynamic_cfg = {
            'services': dynamic_services
        }
        static_cfg = {
            'services': static_services
        }
        # print(xrd_name_list)
        generate_key(xrd_name_list)
        save_docker_compose_file(cfg['name'], 'dynamic', dynamic_cfg)
        save_docker_compose_file(cfg['name'], 'static', static_cfg)


def check_dir_exit():
    pass


def check_file_exit():
    pass


def check_config(cfg):
    """
    check if the configuration has all required fields
    :param cfg:
    :return:
    """
    assert ('name' in cfg), "Must have the name field in configuration"

    static_types = cfg.get('static')
    if static_types:
        for static_type in static_types:
            assert static_type in VALID_STATIC_TYPES, "The static field must be one of %s and it's type must be a list" % (
                ','.join(VALID_STATIC_TYPES))

    assert ('dynamic' in cfg), "Must have the dynamic field in configuration"

    dynamic = cfg['dynamic']
    assert ('domains' in dynamic), "Must have the domains field in dynamic configuration"
    domains = dynamic['domains']

    for domain in domains:
        hosts = domain['hosts']
        assert 'name' in domain, 'Must set the name field for every domains item'
        has_rucio = False
        for host in hosts:
            assert 'name' in host, "Must set the name field in the {}"
            assert 'type' in host, "Must set the type field"
            assert host['type'] in VALID_HOST_TYPES, "The type field must be one of %s" % (','.join(VALID_HOST_TYPES))
            assert 'ip' in host, "Must set the ip field"
            if host['type'] == 'rucio':
                assert (has_rucio is False), "Must have only one instance of Rucio in each net"
                has_rucio = True

        assert has_rucio, "Must have one instance of Rucio"


def collect_hosts(cfg):
    """
    collect host information
    :param cfg:
    :return:
    """
    workflow_name = cfg['name']
    domains = cfg['dynamic']['domains']
    # print(domains)
    net_host_map = dict()
    extra_hosts = list()
    for domain in domains:
        hosts = domain['hosts']
        net_name = domain['name']
        net_host_map[net_name] = hosts
        for host in hosts:
            host_name, host_type, ip = host['name'], host['type'], host['ip']
            name = '{workflow_name}_{net_name}_{host_name}'.format(workflow_name=workflow_name, net_name=net_name,
                                                                   host_name=host_name)
            if host_type == 'rucio':
                extra_hosts += [str('rucio:%s' % ip), 'ruciodb:%s' % ip,
                                'fts:%s' % ip, 'ftsdb:%s' % ip,
                                'activemq:%s' % ip]
            elif host_type == 'xrd':
                extra_hosts += ['%s:%s' % (name, ip)]
    extra_hosts = list(set(extra_hosts))
    extra_hosts.sort()
    return net_host_map, extra_hosts


def parse_cfg(cfg):
    """

    :param cfg:
    :return:
    """
    dynamic_services = {}
    static_services = {}
    xrd_name_list = []
    net_host_map, extra_hosts = collect_hosts(cfg)
    workflow_name = cfg['name']
    static_types = cfg.get('static')
    if static_types:
        for static_type in static_types:
            if static_type == 'fts':
                add_fts_service(static_services)
    for net_name in net_host_map:
        hosts = net_host_map[net_name]
        for host in hosts:
            host_type = host['type']
            if host_type == 'xrd':
                host_name = host['name']
                container_name = '{}_{}_{}'.format(workflow_name, net_name, host_name)
                xrd_name_list.append(container_name)
                add_xrd_service(dynamic_services, extra_hosts, container_name)
            elif host_type == 'rucio':
                add_rucio_service(static_services, extra_hosts)
    return dynamic_services, static_services, xrd_name_list


def add_xrd_service(services, extra_hosts, container_name):
    """

    :param services:
    :param extra_hosts:
    :param container_name:
    :return:
    """
    xrd = {}
    xrd['image'] = IMAGES['xrd']
    xrd['build'] = "rucio-containers/dev/"
    xrd['container_name'] = container_name
    xrd['extra_hosts'] = extra_hosts
    # crate hostcert_containaer_name
    xrd['volumes'] = [
        '{}/etc/certs/hostcert_{}.pem:/tmp/xrdcert.pem:Z'.format(RUCIO_PREFIX_PATH, container_name),
        '{}/etc/certs/hostcert_{}.key.pem:/tmp/xrdkey.pem:Z'.format(RUCIO_PREFIX_PATH, container_name),
        '{}:/etc/xrootd/client.conf:Z'.format(XRD_CLIENT_CONF_FILEPATH)
    ]
    xrd['environment'] = XRD_ENVS
    xrd['cap_add'] = XRD_CAP_ADD
    services[container_name] = xrd


def add_rucio_service(services, extra_hosts):
    """

    :param services:
    :param extra_hosts:
    :return:
    """
    rucio = {}
    rucio['image'] = IMAGES['rucio']
    rucio['build'] = 'rucio-containers/dev'
    rucio['container_name'] = 'rucio'
    rucio['extra_hosts'] = extra_hosts
    rucio['ports'] = RUCIO_PORTS
    rucio['volumes'] = [
        '{}/tools:/opt/rucio/tools:Z'.format(RUCIO_PREFIX_PATH),
        '{}/bin:/opt/rucio/bin:Z'.format(RUCIO_PREFIX_PATH),
        '{}/lib:/opt/rucio/lib:Z'.format(RUCIO_PREFIX_PATH),
        '{}:/opt/alto'.format(ALTO_PREFIX_PATH)
    ]
    #  usercert  userkey?
    rucio['environment'] = RUCIO_ENVS
    rucio['cap_add'] = ['NET_ADMIN']
    services['rucio'] = rucio


def add_fts_service(services):
    services['fts'] = {
        'image': 'docker.io/rucio/fts',
        'network_mode': 'service:rucio',
        'volumes': [
            '{}/fts3config:/etc/fts3/fts3config:Z'.format(FTS_PREFIX_PATH)
        ],
    }


def save_docker_compose_file(workflow_name, mode, cfg):
    """

    :param workflow_name:
    :param mode:
    :param cfg:
    :return:
    """
    filepath = '../workflow/{}'.format(workflow_name)
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    dp_fn = '{}-docker-compose.yml'.format(mode)
    filepath = os.path.join(filepath, dp_fn)
    with open(filepath, 'w') as f:
        # https://qa.1r1g.com/sf/ask/946317361/
        yaml.Dumper.ignore_aliases = lambda *args: True
        yaml.dump(cfg, f, default_flow_style=False)
        print('[{}]'.format(dp_fn) + 'is saved to ' + os.path.abspath(
            filepath))


def export_passin_env():
    return 'export {}={}'.format(PASSPHRASE['key'], PASSPHRASE['val'])


def generate_key(host_name_list):
    file_demo = '#!/bin/bash\n{}\n'.format(export_passin_env())
    for host_name in host_name_list:
        out_filename = os.path.join(RUCIO_CERTS_PATH, 'hostcert_' + host_name)
        export_passin_env()
        xrd_key_pem = 'openssl req -new -newkey rsa:2048 -nodes -keyout {out_filename}.key.pem -subj "/CN={host_name}" > {out_filename}.csr'.format(
            out_filename=out_filename, host_name=host_name)
        xrd_pem = 'openssl x509 -req -days 9999 -CAcreateserial -extfile <( printf "subjectAltName=DNS:{host_name},DNS:localhost,DNS:{host_name}.default.svc.cluster.local" ) -in {out_filename}.csr -CA {RUCIO_CERTS_CA} -CAkey {RUCIO_CERTS_KEY} -out {out_filename}.pem -passin env:{PASSPHRASE}'.format(
            host_name=host_name, RUCIO_CERTS_KEY=RUCIO_CERTS_KEY, RUCIO_CERTS_CA=RUCIO_CERTS_CA,
            out_filename=out_filename,
            PASSPHRASE=PASSPHRASE['key'])
        file_demo += '{}\n{}\n'.format(xrd_key_pem, xrd_pem)
    with open('./generate_xrd_cert.sh', 'w', encoding='utf8') as f:
        f.write(file_demo)
        f.close()
    subprocess.Popen('chmod +x generate_xrd_cert.sh', shell=True).wait()
    subprocess.run('./generate_xrd_cert.sh')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate dynamic docker-compose file and dynamic docker-compose file from workflow.yaml file')
    parser.add_argument('-f', type=str, default='../etc/input.yml', help='workflow.yml filepath')
    args = parser.parse_args()
    fn = os.path.abspath(args.f)
    generate(fn)
