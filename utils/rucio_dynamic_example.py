#!/usr/bin/python
"""
This is a simple example to demostrate rucio with containernet.
"""
# from alto_server import config_server
import argparse
import json
import requests
import yaml
import networkx
from itertools import groupby
from socket import gethostbyname
from node_ext import DynamicDocker
from mininet.net import Containernet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel

setLogLevel('info')

# url_format % (address, vSwitch, flow_id)
url_format = "http://%s:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:%s/table/0/flow/%s"

# flow_format % (flow_id, ingress_port, ethertype, action)
flow_format = """
{"flow":
    {
        "id": "%s",
        "priority": 100,
        "table_id": 0,
        "match": {
            "in-port": "%s",
            "ethernet-match": {
                "ethernet-type": {
                    "type": %s
                }
            }
        },
        "instructions": {
            "instruction": [
                {
                    "order": 0,
                    "apply-actions": {
                        "action": [
                            %s
                        ]
                    }
                }
            ]
        }
    }
}
"""

# action_format % (order, egress_port)
action_format = """
        {
             "order": %s,
             "output-action": {
                 "max-length": 65535,
                 "output-node-connector": "%s"
             }
        },"""

# to_controller % (order)
to_controller = """
        {
            "order": %s,
            "output-action": {
                "max-length": 65535,
                "output-node-connector": "CONTROLLER"
            }
        }"""


class MininetSimulator:

    def __init__(self, graph, **params):
        self.graph = graph
        self.net = Containernet(**params)

    """
    Add hosts, switches, links according to the networkx graph.
    """
    def buildNet(self):
        controllers = set()
        nodes = self.graph.nodes()
        edges = self.graph.edges()
        hosts = [n for n in nodes if 1 == networkx.degree(self.graph, n)]
        info('*** Adding controllers\n')
        for node in nodes:
            if "controller" in nodes[node].keys():
                controllers.add(nodes[node]["controller"])
        for hostname in controllers:
            self.net.addController(hostname, controller=RemoteController, ip=gethostbyname(hostname))

        # Use nodes_port to record the port number of each switch that will be used.
        nodes_port = {}
        info('*** Adding nodes\n')
        for node in nodes:
            nodes_port[node] = 1
            if node in hosts:
                self.net.addHost(**nodes[node], cls=DynamicDocker)
            else:
                # If you want different switch connected to different controller,
                # you must switch.start() with your controller.
                # In net.start(), all switches are connected to the same controller.
                self.net.addSwitch(node, protocols="OpenFlow13").start(
                    controllers=[self.net.get(nodes[node]['controller'])]
                )

        info('*** Creating links\n')
        for edge in edges:
            self.net.addLink(edge[0], edge[1], cls=TCLink, **edges[edge])
            # Append link attributes with a dict like {'xrd1': 1, 's2': 1},
            # which means the link connected to xrd1 port 1 and s2 port 1.
            edges[edge][edge[0]] = nodes_port[edge[0]]
            nodes_port[edge[0]] += 1
            edges[edge][edge[1]] = nodes_port[edge[1]]
            nodes_port[edge[1]] += 1
            g.add_edge(edge[0], edge[1], **edges[edge])

    def startNet(self):
        info('*** Starting network\n')
        self.start()

        info('*** Configuring ALTO server\n')
        # config_server(net)

        self.applySTP()
        info('*** Testing connectivity\n')
        self.net.pingAll()

        info('*** Running CLI\n')
        CLI(self.net)
        info('*** Stopping network')
        self.net.stop()

    '''
    Copied from the start method of Containernet with switch.start() deleted
    '''
    def start(self):
        "Start controller and switches."
        if not self.net.built:
            self.net.build()
        info('*** Starting controller\n')
        for controller in self.net.controllers:
            info(controller.name + ' ')
            controller.start()
        info('\n')
        info('*** Starting %s switches\n' % len(self.net.switches))
        for switch in self.net.switches:
            info(switch.name + ' ')
            # switch.start( self.net.controllers )
        started = {}
        for swclass, switches in groupby(
                sorted(self.net.switches,
                       key=lambda s: str(type(s))), type):
            switches = tuple(switches)
            if hasattr(swclass, 'batchStartup'):
                success = swclass.batchStartup(switches)
                started.update({s: s for s in success})
        info('\n')
        if self.net.waitConn:
            self.net.waitConnected(self.net.waitConn)

    """
    Apply STP to the network
    """
    def applySTP(self):
        self.graph = networkx.minimum_spanning_tree(self.graph)
        nodes = self.graph.nodes()
        switches = [n for n in nodes if 1 != networkx.degree(self.graph, n)]
        for s in switches:
            ports = set()
            adj = self.graph[s]
            for d in adj.keys():
                ports.add(adj[d][s])
            for ingress_port in ports:
                enable_broadcast(nodes[s]["controller"], s[1:], ingress_port, ports-{ingress_port})


def enable_broadcast(address, vSwitch, ingress_port, egress_ports):
    action = ""
    for order, egress_port in enumerate(egress_ports):
        action += action_format % (order, egress_port)
    action = action[:-1]
    ip_payload = flow_format % (f"ip-{ingress_port}", ingress_port, 2048, action)
    requests.put(auth=("admin", "admin"), json=json.loads(ip_payload), url=url_format % (address, vSwitch, "ip-%s"%ingress_port))

    action += "," + to_controller % (len(egress_ports))
    arp_payload = flow_format % (f"arp-{ingress_port}", ingress_port, 2054, action)
    requests.put(auth=("admin", "admin"), json=json.loads(arp_payload), url=url_format % (address, vSwitch, "arp-%s"%ingress_port))


def yml_to_graph(yml, mode="file" or "str"):
    data = None
    if mode == "file":
        with open(yml) as f:
            data = yaml.load(f.read(), Loader=yaml.FullLoader)
    elif mode == "str":
        data = yaml.load(yml, Loader=yaml.FullLoader)
    else:
        print("unsupported mode")
        exit(1)
    hosts = {}
    switches = {}
    nodes = {}
    links = {}
    controllers = []

    for domain in data['dynamic']['domains']:
        # Add the controller of the domain
        controllers.append(domain['controller']['name'])

        # Add hosts in a domain
        for host in domain['hosts']:
            hosts[host['name']] = host

        # Add switches in a domain, switches set = {{nodes} - {hosts}}
        all_nodes_in_domain = set()
        for link in domain['links']:
            all_nodes_in_domain.add(link['endpoints'][0])
            all_nodes_in_domain.add(link['endpoints'][1])
        switches_name = list(all_nodes_in_domain - set(hosts.keys()))
        for name in switches_name:
            switches[name] = {"controller": domain['controller']['name']}

        # Add links in a domain
        nodes.update(hosts)
        nodes.update(switches)
        for link in domain['links']:
            links[(link['endpoints'][0], link['endpoints'][1])] = {
                "network": domain['name'],
                "delay": None if not link.keys().__contains__('latency') else link['latency'],
                "bw": None if not link.keys().__contains__('bandwidth') else link['bandwidth']
            }

    # Add links in the interdomain
    for link in data['dynamic']['interdomain']:
        links[(link['endpoints'][0], link['endpoints'][1])] = {
            "network": "interdomain",
            "delay": None if not link.keys().__contains__('latency') else link['latency'],
            "bw": None if not link.keys().__contains__('bandwidth') else link['bandwidth']
        }

    g = networkx.Graph()
    nodes = list(nodes.items())
    g.add_nodes_from(nodes)
    for link, attr in links.items():
        g.add_edge(link[0], link[1], **attr)
    return g


"""
Create custom topology from .yml workflow file:
"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a mininet topology from workflow .yaml file')
    parser.add_argument('--str', type=str, help='.yaml file content')
    args = parser.parse_args()
    g = yml_to_graph(yml=args.str, mode="str")
    MS = MininetSimulator(g)
    MS.buildNet()
    MS.startNet()
