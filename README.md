# PI-II_SDN
Repository used to develop the project of Communications Project II curricular unit

### Run the code

1. Start some topology with multiple switches with mininet

(download the topology and move it to /mininet/custom directory)

```sudo python3 mininet/custom/pi_topology.py``` 

2. Run some controller with the monitor code together

```ryu-manager ryu.app.simple_switch_13 monitor_api.py```

Example to check all the switches you have in your topology, open your browser at the URL: 

```http://127.0.0.1:8080/monitor/switches```

Example of network statistics of port 2 from switch 1:

```http://127.0.0.1:8080/monitor/switch/1/port/2```


Example of network statistics of all ports details from switch 3:

```http://127.0.0.1:8080/monitor/switch/3/portdetails```


Check the code comments for others URI endpoints

### VM images (Virtual Box): 

Fedora with mininet and Ryu:
https://uminho365-my.sharepoint.com/:u:/g/personal/pg45517_uminho_pt/EUobulazcKdPo9VWy6h6mVcBCUXDgSMm2Nz_GkCOCNRvrg?e=SSzWbo

Fedora 34 linux (password: uminho) with:
 * Mininet 2.3.0
 * Ryu
 * WireShark
 * Visual Studio code
 * 3.8 GB of size

CentOS 7 with Zabbix Server 5.0 (password uminho)
https://uminho365-my.sharepoint.com/:u:/g/personal/pg45517_uminho_pt/EXRlbu279vZPinXyK64Imy0Bp9B1ueOKLAmK-1Xbn9YnQA?e=elLmow

### Setup VM connection:

VirtualBox > Select VM > Settings > Network > Adaptor 2 > Enable and select attached to "Internal Network"

IP for Zabbix VM internal network interface: 10.0.0.1/30
IP for Fedora VM internal network interface: 10.0.0.2/30

Access Zabbix Server Web GUI through Fedora VM web browser at http://10.0.0.1/zabbix

Zabbix username: Admin
Zabbix password: zabbix

### Mininet emulator:

Mininet installation and setup: http://mininet.org/vm-setup-notes/

To install GUI in the VM run the command:
sudo tasksel install ubuntu-desktop-minimal

Follow the Mininet Walkthrough to get use with the application:
http://mininet.org/walkthrough/

### Ryu SDN Controller:

Overview: https://ryu.readthedocs.io/en/latest/index.html

https://thenewstack.io/sdn-series-part-iv-ryu-a-rich-featured-open-source-sdn-controller-supported-by-ntt-labs/

Introduction: https://ryu-sdn.org/slides/ONS2013-april-ryu-intro.pdf

Framework documentation: https://book.ryu-sdn.org/en/Ryubook.pdf

GitHub: https://github.com/faucetsdn/ryu

Programming a simple switch (starting at 10 minutes): https://www.youtube.com/watch?v=2VRsituJ6a8
