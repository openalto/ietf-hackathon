from threading import Thread

from flask import Flask, jsonify
from werkzeug.serving import make_server
from mininet.net import Mininet


SWITCH_REQUIRED_KEYS = ['domain', 'name', 'opf_version', 'ports']
HOST_REQUIRED_KEYS = ['name', 'ip', 'mac', 'ports']
LINK_REQUIRED_KEYS = ['src', 'dst', 'type']


def get_link_type(domain1, domain2):
    if not domain1 and not domain2 and domain1 != domain2:
        return 'interdomain'
    else:
        return 'intradomain'


def start_data_source_agent(net: Mininet):
    """
    Generate network map and cost map from mininet topology.
    """
    server = DataSourceAgent(net)
    server.start()
    return server


def stop_data_source_agent(server):
    server.shutdown()


class DataSourceAgent(Thread):

    def __init__(self, net: Mininet, host='0.0.0.0', port=9090):
        Thread.__init__(self)
        self.net = net
        self.host = host
        self.port = port
        self.app = Flask('mininet-data-source-agent')
        self.app.add_url_rule('/topology', 'topology', lambda: self.get_topology())
        self.server = make_server(self.host, self.port, self.app)


    def run(self):
        self.server.serve_forever()


    def shutdown(self):
        self.server.shutdown()


    def get_topology(self):
        """
        """
        topology_dict = dict()

        switch_dict = dict()
        for sw in self.net.switches:
            try:
                switch_dict[sw.name] = {
                    'name': sw.name,
                    'domain': sw.vsctl('get-controller', sw.name).strip(),
                    'opf_version': sw.protocols,
                    'ports': [
                        {
                            'name': port.name,
                            **port.params
                        } for port in sw.ports.keys()
                    ],
                    **{k: v for k, v in sw.params.items() if k not in SWITCH_REQUIRED_KEYS}
                }
            except:
                pass
        topology_dict['switch'] = list(switch_dict.values())

        host_list = []
        for h in self.net.hosts:
            try:
                host_list.append({
                    'name': h.name,
                    'ip': h.IP(),
                    'mac': h.MAC(),
                    'ports': [
                        {
                            'name': port.name,
                            **port.params
                        } for port in h.ports.keys()
                    ],
                    **{k: v for k, v in h.params.items() if k not in HOST_REQUIRED_KEYS}
                })
            except:
                pass
        topology_dict['host'] = host_list

        link_list = []
        for l in self.net.links:
            try:
                link_list.append({
                    'src': l.intf1.name,
                    'dst': l.intf2.name,
                    'type': get_link_type(
                        switch_dict.get(intf1.node.name, dict()).get('domain', None),
                        switch_dict.get(intf2.node.name, dict()).get('domain', None)
                    ),
                    **{k: v for k, v in l.params.items() if k not in LINK_REQUIRED_KEYS}
                })
            except:
                pass
        topology_dict['link'] = link_list

        return jsonify(topology_dict)

