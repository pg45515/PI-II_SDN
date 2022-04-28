# PI-II_SDN
Repository used to develop the project of Communications Project II curricular unit

### Run the code

1. Start some topology with multiple switches with mininet

(download the topology and move it to /mininet/custom directory)
```sudo python3 mininet/custom/pi_topology.py``` 

2. Run some controller with the monitor code together

```ryu-manager tp1_ex1_layer2_controller.py monitor_api.py```

Example to check all the switches you have in your topology, open your browser at the URL: 

```http://127.0.0.1:8080/monitor/switches```

Example of network statistics of port 2 from switch 1:

```http://127.0.0.1:8080/monitor/switch/1/port/2```


Example of network statistics of all ports details from switch 3:

```http://127.0.0.1:8080/monitor/switch/3/portdetails```


Check the code comments for others URI endpoints

### VM image (Virtual Box): 

https://uminho365-my.sharepoint.com/:u:/g/personal/pg45517_uminho_pt/EUobulazcKdPo9VWy6h6mVcBCUXDgSMm2Nz_GkCOCNRvrg?e=SSzWbo

password: uminho

Fedora 34 linux with:
 * Mininet 2.3.0
 * Ryu
 * WireShark
 * Visual Studio code
 * 3.8 GB of size

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
