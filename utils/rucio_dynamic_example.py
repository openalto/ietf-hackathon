#!/usr/bin/python
"""
Modified from: rucio_example.py
This is a simple example to show how to generate a topology from 
the .yml workflow file.
"""
# from alto_server import config_server
import argparse
import yaml
from node_ext import DynamicDocker
from sflow import wrapper
from mininet.net import Mininet, Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel

setLogLevel('info')


class MyNet(Containernet):

    def __init__(self, **params):
        super().__init__(**params)

    def addMyHost(self, host):
        host.node_instance = self.addHost(host.name, ip=host.ip, cls=host.cls, **host.params)

    def addMySwitch(self, switch):
        switch.node_instance = self.addSwitch(switch.name)

    def addMyLink(self, link):
        link.link_instance = self.addLink(link.node1.node_instance,
                                          link.node2.node_instance,
                                          cls=link.cls, delay=link.delay, bw=link.bw)


class Host:

    def __init__(self, name, type, ip, cls=DynamicDocker, **params):
        self.name = name
        self.type = type
        self.ip = ip
        self.cls = cls
        self.params = params
        self.node_instance = None


class Link:

    def __init__(self, node1, node2, delay, bw, cls=TCLink):
        self.node1 = node1
        self.node2 = node2
        self.cls = cls
        self.delay = delay
        self.bw = bw
        self.link_instance = None


class Switch:

    def __init__(self, name):
        self.name = name
        self.node_instance = None


# Return a Host dict, a Switch dict and a Link list.
# Use Host, Switch and Link to abstract elements in the .yaml file.
def read_from_yml(yml_str):
    data = yaml.load(yml_str, Loader=yaml.FullLoader)
    hosts = {}
    switches = {}
    links = []
    for host in data['dynamic']['hosts']:
        hosts[host['name']] = Host(host['name'], host['type'], host['ip'])

    all_nodes = set()
    for link in data['dynamic']['links']:
        all_nodes.add(link['endpoints'][0])
        all_nodes.add(link['endpoints'][1])
    switches_name = list(all_nodes - set(hosts.keys()))
    for name in switches_name:
        switches[name] = Switch(name)

    nodes = dict()
    nodes.update(hosts)
    nodes.update(switches)
    for link in data['dynamic']['links']:
        links.append(Link(nodes[link['endpoints'][0]],
                          nodes[link['endpoints'][1]],
                          None if not link.keys().__contains__('latency') else link['latency'],
                          None if not link.keys().__contains__('bandwidth') else link['bandwidth']))
    return hosts, switches, links


# setattr(Mininet, 'start', wrapper(Mininet.__dict__['start']))

"""
Create the following topology:

              Rucio
      1Mbps    |     5Mbps
      25ms     |     25ms
  s1 --------- s3 ----------- s4 -- XRD3
  |            |              |
  |            | 25ms         | 50ms
  |            | 1Mbps        | 2Mbps
  |            |              |
 XRD1          s2 -- XRD2     s5 -- XRD4
"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a mininet topology from workflow .yaml file')
    parser.add_argument('--str', type=str, help='.yaml file content')
    args = parser.parse_args()
    hosts, switches, links = read_from_yml(args.str)

    net = MyNet(controller=Controller)
    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Adding docker containers\n')
    for host in hosts.values():
        net.addMyHost(host)

    info('*** Adding switches\n')
    for switch in switches.values():
        net.addMySwitch(switch)

    info('*** Creating links\n')
    for link in links:
        net.addMyLink(link)

    info('*** Starting network\n')
    net.start()

    info('*** Configuring ALTO server\n')
    # config_server(net)

    info('*** Testing connectivity\n')
    # net.ping([rucio, xrd1, xrd2, xrd3, xrd4])
    net.pingAll()
    info('*** Running CLI\n')
    CLI(net)
    info('*** Stopping network')
    net.stop()
