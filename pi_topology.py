#from turtle import speed
from mininet.net import Mininet
#from mininet.topo import Topo
from mininet.node import RemoteController
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import info
from mininet.log import setLogLevel
from mininet.link import TCLink
#from subprocess import call

def Topology():
    net = Mininet( controller=RemoteController, link=TCLink, switch=OVSSwitch )

    c0 = net.addController(name='c0',
                        controller=RemoteController,
                        ip='127.0.0.1',
                        protocol='tcp',
                        port=6633)

    info('Adding 7 switches...\n')
    s1 = net.addSwitch('s1', cls=OVSSwitch, dpid='0000000000000001') # L2 Switch Net B (no ip)
    s2 = net.addSwitch('s2', cls=OVSSwitch, dpid='0000000000000002') # L2 Switch Net C (no ip)
    s3 = net.addSwitch('s3', cls=OVSSwitch, dpid='0000000000000003') # L2 Switch Net C (no ip)
    s4 = net.addSwitch('s4', cls=OVSSwitch, dpid='0000000000000004') # L2 Switch Net B (no ip)
    s5 = net.addSwitch('s5', cls=OVSSwitch, dpid='0000000000000005') # L2 Switch Net B (no ip)
    s6 = net.addSwitch('s6', cls=OVSSwitch, dpid='0000000000000006') # L2 Switch Net B (no ip)
    s7 = net.addSwitch('s7', cls=OVSSwitch, dpid='0000000000000007') # L2 Switch Net B (no ip)

    info('Adding 6 hosts...\n')
    h1 = net.addHost( 'h1', mac = '00:00:00:00:00:01')   # Host 1 
    h2 = net.addHost( 'h2', mac = '00:00:00:00:00:02')   # Host 2
    h3 = net.addHost( 'h3', mac = '00:00:00:00:00:03')   # Host 3 
    h4 = net.addHost( 'h4', mac = '00:00:00:00:00:04')   # Host 4 
    h5 = net.addHost( 'h5', mac = '00:00:00:00:00:05')   # Host 5 
    h6 = net.addHost( 'h6', mac = '00:00:00:00:00:06')   # Host 6 
    
    info('Adding links from hosts to switches...\n')
    net.addLink(h1, s1, cls=TCLink, bw=0.1)
    net.addLink(h2, s2, cls=TCLink)
    net.addLink(h3, s3, cls=TCLink, loss=20)
    net.addLink(h4, s4, cls=TCLink)
    net.addLink(h5, s5, cls=TCLink, delay='20ms')
    net.addLink(h6, s6, cls=TCLink, delay='10ms', loss=10)

    info('Adding links among switches')
    net.addLink(s1, s7)
    net.addLink(s2, s7)
    net.addLink(s3, s7)
    net.addLink(s4, s7)
    net.addLink(s5, s7)
    net.addLink(s6, s7)

    info('Setting MAC addresses to switches')
    s1.setMAC('10:00:00:00:00:01', 's1-eth1')
    s2.setMAC('10:00:00:00:00:02', 's2-eth1')
    s3.setMAC('10:00:00:00:00:03', 's3-eth1')
    s4.setMAC('10:00:00:00:00:04', 's4-eth1')
    s5.setMAC('10:00:00:00:00:05', 's5-eth1')
    s6.setMAC('10:00:00:00:00:06', 's6-eth1')

    net.build()

    s1.start([c0])
    s2.start([c0])
    s3.start([c0])
    s4.start([c0])
    s5.start([c0])
    s6.start([c0])
    s7.start([c0])
    
    CLI(net) # Start command line

    net.stop() # Stop Network

if __name__ == '__main__':
    setLogLevel('info')
    Topology()
