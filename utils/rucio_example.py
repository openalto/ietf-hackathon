#!/usr/bin/python
"""
This is a simple example to demostrate rucio with containernet.
"""
from node_ext import DynamicDocker
from sflow import wrapper
from mininet.net import Mininet, Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
setLogLevel('info')

setattr(Mininet, 'start', wrapper(Mininet.__dict__['start']))

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

net = Containernet(controller=Controller)
info('*** Adding controller\n')
net.addController('c0')

info('*** Adding docker containers\n')
rucio = net.addHost('rc', cname='rucio', ip='10.0.0.250', cls=DynamicDocker)
xrd1 = net.addHost('xrd1', ip='10.0.0.251', cls=DynamicDocker)
xrd2 = net.addHost('xrd2', ip='10.0.0.252', cls=DynamicDocker)
xrd3 = net.addHost('xrd3', ip='10.0.0.253', cls=DynamicDocker)
xrd4 = net.addHost('xrd4', ip='10.0.0.254', cls=DynamicDocker)

info('*** Adding switches\n')
s1 = net.addSwitch('s1')
s2 = net.addSwitch('s2')
s3 = net.addSwitch('s3')
s4 = net.addSwitch('s4')
s5 = net.addSwitch('s5')

info('*** Creating links\n')
net.addLink(xrd1, s1)
net.addLink(xrd2, s2)
net.addLink(rucio, s3)
net.addLink(s1, s3, cls=TCLink, delay='25ms', bw=1)
net.addLink(s2, s3, cls=TCLink, delay='25ms', bw=1)
net.addLink(xrd3, s4)
net.addLink(s3, s4, cls=TCLink, delay='25ms', bw=2)
net.addLink(xrd4, s5)
net.addLink(s4, s5, cls=TCLink, delay='50ms', bw=5)
info('*** Starting network\n')
net.start()
info('*** Testing connectivity\n')
net.ping([rucio, xrd1, xrd2, xrd3, xrd4])
info('*** Running CLI\n')
CLI(net)
info('*** Stopping network')
net.stop()

