# coding:utf8
# usage：python generate-docker-compose.py [path-to-workflow-config]
import argparse
import os
import shutil
import subprocess

import yaml

VALID_HOST_TYPES = ['rucio', 'xrd']

PASSPHRASE = {'key': 'PASSPHRASE', 'val': 123456}

ODL_CONF = {
    'image': 'openalto/odl:0.8.4',
    # 'network_mode': "service:mininet",
    'entrypoint': '/bin/bash',
    'command': "-c '/opt/opendaylight/bin/start && tail -f /dev/null'",
}

RUCIO_CONF = {
    'image': 'openalto/rucio-dev',
    'ports': [
        "127.0.0.1:8443:443",
        "127.0.0.1:5432:5432",
        "127.0.0.1:8080:80",
        "127.0.0.1:8446:8446",
        "127.0.0.1:8449:8449",
        "127.0.0.1:3306:3306",
        "127.0.0.1:9000:9000",
        "127.0.0.1:61613:61613",
        "127.0.0.1:2222:22"
    ],
    'environment': [
        'X509_USER_CERT=/opt/rucio/etc/usercert.pem',
        'X509_USER_KEY=/opt/rucio/etc/userkey.pem',
        'RDBMS=postgres14'
    ],

    'build': 'rucio-containers/dev',
    'cap_add': ['NET_ADMIN', ],
    'container_name': 'rucio'
}

RUCIODB_CONF = {
    'image': 'docker.io/postgres:14',
    'network_mode': "service:rucio",
    'environment': [
        'POSTGRES_USER=rucio',
        'POSTGRES_DB=rucio',
        'POSTGRES_PASSWORD=secret'
    ],
    'command': ["-c", "fsync=off", "-c", "synchronous_commit=off", "-c", "full_page_writes=off"],
}

FTS_CONF = {
    'image': 'docker.io/rucio/fts',
    'network_mode': "service:rucio",
}
FTSDB_CONF = {
    'image': 'docker.io/mysql:8',
    'network_mode': "service:rucio",
    'command': '--default-authentication-plugin=mysql_native_password',
    'environment': [
        'MYSQL_USER=fts',
        'MYSQL_PASSWORD=fts',
        'MYSQL_ROOT_PASSWORD=fts',
        'MYSQL_DATABASE=fts'
    ]
}

ACTIVEMQ_CONF = {
    'image': 'docker.io/webcenter/activemq:latest',
    'network_mode': "service:rucio",
    'environment': [
        'ACTIVEMQ_CONFIG_NAME=activemq',
        'ACTIVEMQ_CONFIG_DEFAULTACCOUNT=false',
        'ACTIVEMQ_USERS_fts=supersecret',
        'ACTIVEMQ_GROUPS_writes=fts',
        'ACTIVEMQ_USERS_receiver=supersecret',
        'ACTIVEMQ_GROUPS_reads=receiver',
        'ACTIVEMQ_CONFIG_SCHEDULERENABLED=true'
    ]
}

MININET_CONF = {
    'image': 'openalto/g2-mininet:minimal',
    'pid': 'host',
    'cap_add': ['NET_ADMIN', 'SYS_ADMIN'],
    'privileged': True,
    'entrypoint': '/bin/bash',
    'command': "-c 'service openvswitch-switch start && tail -f /dev/null'"
}

XRD_CONF = {
    'image': 'openalto/xrootd',
    'environment': ['XRDPORT=1094'],
    'cap_add': ['NET_ADMIN']
}

COMMON_BASE_PATH = {
    'rucio': os.path.abspath('../common/rucio'),
    'fts': os.path.abspath('../common/fts'),
    'xrd': os.path.abspath('../common/xrootd')
}

BASE_PATH = {
    'utils': os.path.abspath('../utils')
}

COMMON_DETAIL_PATH = {
    # 'rucio_certs': os.path.abspath(os.path.join(COMMON_BASE_PATH['rucio'], 'etc/certs')),
    'rucio_ca_key': os.path.abspath(os.path.join(COMMON_BASE_PATH['rucio'], 'etc/certs/rucio_ca.key.pem')),
    'rucio_ca': os.path.abspath(os.path.join(COMMON_BASE_PATH['rucio'], 'etc/certs/rucio_ca.pem')),
    'xrd_conf': os.path.join(COMMON_BASE_PATH['xrd'], 'client.conf')
}

print(COMMON_DETAIL_PATH)

STATIC_CONF = {
    'ftsdb': FTSDB_CONF,
    'activemq': ACTIVEMQ_CONF,
    'ruciodb': RUCIODB_CONF
}

VALID_STATIC_TYPES = ['fts', 'mininet'] + [key for key in STATIC_CONF]


# RUCIO_PREFIX_PATH = os.path.abspath('../common/rucio')
# FTS_PREFIX_PATH = os.path.abspath('../common/fts')

# RUCIO_CERTS_PATH = os.path.abspath(os.path.join(RUCIO_PREFIX_PATH, 'etc/certs'))
# XRD_CLIENT_CONF_FILEPATH = os.path.abspath('../common/xrootd/client.conf')

# RUCIO_CERTS_KEY = os.path.join(RUCIO_CERTS_PATH, 'rucio_ca.key.pem')
# RUCIO_CERTS_CA = os.path.join(RUCIO_CERTS_PATH, 'rucio_ca.pem')


def check_or_create_filepath(filepath, children_filepaths=None):
    """
    Check whether the file path exists. If it does not exist, create it
    :param filepath: target filepath
    :param children_filepaths:  subfolders of the destination folder
    :return:
    """
    if children_filepaths:
        for children_filepath in children_filepaths:
            fp = os.path.join(filepath, children_filepath)
            if not os.path.exists(fp):
                os.makedirs(fp)
    else:
        if not os.path.exists(filepath):
            os.makedirs(filepath)


class GenerateDockerCompose:

    def __init__(self):
        self.net_host_map = None
        self.extra_hosts = None
        self.cfg = None
        self.xrd_name_list = []
        self.workflow_name = ''
        self.controller_names = []
        self.dynamic_services = dict()
        self.static_services = dict()
        # workflow filepath
        self.docker_filepath = ''
        self.fts_filepath = ''
        self.alto_filepath = ''
        self.rucio_filepath = ''
        self.base_filepath = ''
        self.xrd_filepath = ''
        self.xrd_file_map = dict()

    def generate(self, filepath):
        """
        :param filepath:
        :return:
        """
        with open(filepath, 'r') as f:
            # load config from yaml file
            self.cfg = yaml.safe_load(f)
            # check whether the configuration file is correct
            self.check_config()
            # parsing configuration file
            self.parse_cfg()
            # generate key for xrd
            self.generate_key()
            # save docker-compose file
            self.save()
            print(self.static_services)

    def check_config(self):
        cfg = self.cfg
        # Check whether the parameters are configured correctly
        assert ('name' in cfg), 'Must have the name field in configuration'
        static_types = cfg.get('static')
        if static_types:
            for static_type in static_types:
                assert static_type in VALID_STATIC_TYPES, "The static field must be one of %s and it's type must be a list" % (
                    ','.join(VALID_STATIC_TYPES))

        assert ('dynamic' in cfg), "Must have the dynamic field in configuration"

        dynamic = cfg['dynamic']
        assert ('domains' in dynamic), "Must have the domains field in dynamic configuration"
        domains = dynamic['domains']

        has_rucio = False
        for domain in domains:
            assert 'controller' in domain, 'Must set the controller field for every domains item'
            assert 'name' in domain['controller'], 'Must set the name field for controller'
            self.controller_names.append(domain['controller']['name'])
            hosts = domain['hosts']
            assert 'name' in domain, 'Must set the name field for every domains item'
            for host in hosts:
                assert 'name' in host, "Must set the name field in the {}"
                assert 'type' in host, "Must set the type field"
                assert host['type'] in VALID_HOST_TYPES, "The type field must be one of %s" % (
                    ','.join(VALID_HOST_TYPES))
                assert 'ip' in host, "Must set the ip field"
                if host['type'] == 'rucio':
                    # assert (has_rucio is False), "Must have only one instance of Rucio in each net"
                    has_rucio = True

        assert has_rucio, "Must have one instance of Rucio"

        self.workflow_name = cfg['name']

        #  Check whether the file path exists

        # ths base filepath is  workflow dir
        base_filepath = '../workflow/{}'.format(self.workflow_name)
        self.base_filepath = base_filepath
        self.docker_filepath = os.path.join(base_filepath, 'docker')
        # docker dir is a empty dir
        check_or_create_filepath(self.docker_filepath)

        # subfolders of the fts dir
        child_filepaths = [
            'log', 'etc'
        ]
        self.fts_filepath = os.path.abspath(os.path.join(base_filepath, 'fts'))
        check_or_create_filepath(self.fts_filepath, child_filepaths)

        self.rucio_filepath = os.path.abspath(os.path.join(base_filepath, 'rucio'))
        rucio_child_filepaths = [
                                    'tools', 'bin', 'lib'
                                ] + child_filepaths
        check_or_create_filepath(self.rucio_filepath, rucio_child_filepaths)

        self.alto_filepath = os.path.abspath(os.path.join(base_filepath, 'alto'))
        check_or_create_filepath(self.alto_filepath)

        # copy configuration fts file from /common/fts/fts3config
        common_cfg_fts_filepath = '../common/fts/fts3config'
        shutil.copyfile(common_cfg_fts_filepath, os.path.join(self.fts_filepath, 'etc/fts3config'))

    def parse_cfg(self):
        cfg = self.cfg

        self.xrd_name_list = []
        self.collect_hosts()

        static_types = cfg.get('static')
        if static_types:
            for static_type in static_types:
                if static_type == 'fts':
                    self.add_fts_service()
                elif static_type == 'mininet':
                    self.add_mininet_service()
                else:
                    self.add_static_service(static_type)
        for controller_name in self.controller_names:
            self.add_odl_service(controller_name)
        for net_name in self.net_host_map:
            hosts = self.net_host_map[net_name]
            for host in hosts:
                host_type = host['type']
                if host_type == 'xrd':
                    host_name = host['name']
                    # container_name = '{}_{}_{}'.format(workflow_name, net_name, host_name)
                    container_name = host_name
                    # list of xrd_name
                    self.xrd_name_list.append(container_name)
                    self.add_xrd_service(container_name)
                # volumes
                elif host_type == 'rucio':
                    self.add_rucio_service()

    def add_odl_service(self, controller_name):
        self.dynamic_services[controller_name] = {
            **ODL_CONF
        }

    def add_static_service(self, static_type):
        self.static_services[static_type] = {
            **STATIC_CONF[static_type]
        }

    def add_mininet_service(self):
        self.static_services['mininet'] = {
            **MININET_CONF,
            'volumes': [
                '/lib/modules:/lib/modules',
                '/var/run/docker.sock:/var/run/docker.sock',
                '{}:/utils'.format(BASE_PATH['utils'])
            ]
        }

    def add_fts_service(self):
        self.static_services['fts'] = {
            **FTS_CONF,
            'volumes': [
                '{}/etc/fts3config:/etc/fts3/fts3config:Z'.format(self.fts_filepath)
            ],
        }

    def add_rucio_service(self):
        rucio = {
            **RUCIO_CONF,
            'extra_hosts': self.extra_hosts,
            'volumes': [
                # workflow dir
                '{}/tools:/opt/rucio/tools:Z'.format(self.rucio_filepath),
                '{}/bin:/opt/rucio/bin:Z'.format(self.rucio_filepath),
                '{}/lib:/opt/rucio/lib:Z'.format(self.rucio_filepath),
                '{}:/opt/alto'.format(self.alto_filepath)
            ]}
        # rucio['image'] = RUCIO_CONF['image']
        # rucio['build'] = 'rucio-containers/dev'
        # rucio['container_name'] = 'rucio'
        # rucio['ports'] = RUCIO_CONF['ports']
        # rucio['environment'] = RUCIO_ENVS
        # rucio['cap_add'] = ['NET_ADMIN']
        self.static_services['rucio'] = rucio

    def add_xrd_service(self, container_name):
        xrd_etc_filepath = os.path.abspath(os.path.join(self.base_filepath, '{}/etc'.format(container_name)))
        xrd = {
            **XRD_CONF,
            'container_name': container_name,
            'extra_hosts': self.extra_hosts,
            'volumes': [
                # move the path to workflow dir
                '{}/xrootd/hostcert_{}.pem:/tmp/xrdcert.pem:Z'.format(xrd_etc_filepath, container_name),
                '{}/xrootd/hostcert_{}.key.pem:/tmp/xrdkey.pem:Z'.format(xrd_etc_filepath, container_name),
                '{}/xrootd/client.conf:/etc/xrootd/client.conf:Z'.format(xrd_etc_filepath)
            ]}
        # xrd['image'] = IMAGES['xrd']
        # xrd['build'] = "rucio-containers/dev/"
        # crate hostcert_containaer_name'
        # xrd['environment'] = XRD_ENVS
        # xrd['cap_add'] = XRD_CAP_ADD
        self.dynamic_services[container_name] = xrd

    def collect_hosts(self):
        cfg = self.cfg
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
                # name = '{workflow_name}_{net_name}_{host_name}'.format(workflow_name=workflow_name, net_name=net_name,
                #                                                        host_name=host_name)
                name = host['name']
                if host_type == 'rucio':
                    extra_hosts += [str('rucio:%s' % ip), 'ruciodb:%s' % ip,
                                    'fts:%s' % ip, 'ftsdb:%s' % ip,
                                    'activemq:%s' % ip]
                elif host_type == 'xrd':
                    extra_hosts += ['%s:%s' % (name, ip)]

        extra_hosts = list(set(extra_hosts))
        extra_hosts.sort()
        self.net_host_map = net_host_map
        self.extra_hosts = extra_hosts

    def export_passin_env(self):
        return 'export {}={}'.format(PASSPHRASE['key'], PASSPHRASE['val'])

    def create_xrd_dir(self):

        for host_name in self.xrd_name_list:
            check_or_create_filepath(os.path.join(self.base_filepath, host_name), [
                'log', 'etc'
            ])
            xrd_etc_filepath = os.path.abspath(os.path.join(self.base_filepath, host_name + '/etc/xrootd'))
            self.xrd_file_map[host_name] = xrd_etc_filepath
            check_or_create_filepath(xrd_etc_filepath)
            # common_xrd_cfg_filepath = XRD_CLIENT_CONF_FILEPATH
            common_xrd_cfg_filepath = COMMON_DETAIL_PATH['xrd_conf']
            print('common_xrd_cfg_filepath', common_xrd_cfg_filepath)
            shutil.copyfile(common_xrd_cfg_filepath, os.path.join(xrd_etc_filepath, 'client.conf'))

    def generate_key(self):
        self.create_xrd_dir()
        file_demo = '#!/bin/bash\n{}\n'.format(self.export_passin_env())

        rucio_certs_key = COMMON_DETAIL_PATH['rucio_ca_key']
        rucio_certs_ca = COMMON_DETAIL_PATH['rucio_ca']

        for host_name in self.xrd_file_map:
            out_filename = os.path.join(self.xrd_file_map[host_name], 'hostcert_' + host_name)

            xrd_key_pem = 'openssl req -new -newkey rsa:2048 -nodes -keyout {out_filename}.key.pem -subj "/CN={host_name}" > {out_filename}.csr'.format(
                out_filename=out_filename, host_name=host_name)
            xrd_pem = 'openssl x509 -req -days 9999 -CAcreateserial -extfile <( printf "subjectAltName=DNS:{host_name},DNS:localhost,DNS:{host_name}.default.svc.cluster.local" ) -in {out_filename}.csr -CA {RUCIO_CERTS_CA} -CAkey {RUCIO_CERTS_KEY} -out {out_filename}.pem -passin env:{PASSPHRASE}'.format(
                host_name=host_name, RUCIO_CERTS_KEY=rucio_certs_key, RUCIO_CERTS_CA=rucio_certs_ca,
                out_filename=out_filename,
                PASSPHRASE=PASSPHRASE['key'])
            file_demo += '{}\n{}\n'.format(xrd_key_pem, xrd_pem)
        generate_xrd_cert_filepath = os.path.abspath(os.path.join(self.docker_filepath, 'generate_xrd_cert.sh'))
        with open(generate_xrd_cert_filepath, 'w', encoding='utf8') as f:
            f.write(file_demo)

        subprocess.run('chmod +x {}'.format(generate_xrd_cert_filepath), shell=True)
        subprocess.run(generate_xrd_cert_filepath)
        os.remove(generate_xrd_cert_filepath)

    def save(self):
        dynamic_cfg = {
            'services': self.dynamic_services
        }
        static_cfg = {
            'services': self.static_services
        }
        self.save_docker_compose_file('dynamic', dynamic_cfg)
        self.save_docker_compose_file('static', static_cfg)

    def save_docker_compose_file(self, mode, cfg):

        dp_fn = '{}-docker-compose.yml'.format(mode)
        filepath = os.path.join(self.docker_filepath, dp_fn)
        with open(filepath, 'w') as f:
            # https://qa.1r1g.com/sf/ask/946317361/
            yaml.Dumper.ignore_aliases = lambda *args: True
            yaml.dump(cfg, f, default_flow_style=False)
            print('[{}]'.format(dp_fn) + 'is saved to ' + os.path.abspath(
                filepath))


if __name__ == '__main__':
    # fn = os.path.abspath('../etc/input.yml')
    # GenerateDockerCompose().generate(filepath=fn)

    parser = argparse.ArgumentParser(
        description='Generate dynamic docker-compose file and dynamic docker-compose file from workflow.yaml file')
    parser.add_argument('-f', type=str, default='../etc/input.yml', help='workflow.yml filepath')
    args = parser.parse_args()
    fn = os.path.abspath(args.f)
    GenerateDockerCompose().generate(filepath=fn)
