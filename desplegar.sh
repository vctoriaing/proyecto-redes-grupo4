#!/bin/bash
# desplegar.sh - levanta todo el laboratorio
# uso: ./desplegar.sh   (desde carpeta del proyecto)

# crear los switches (bridges host)
sudo ip link add name sw-a type bridge
sudo ip link set sw-a up
sudo ip link add name sw-b type bridge
sudo ip link set sw-b up
sudo sysctl -w net.bridge.bridge-nf-call-iptables=0

# crear los contenedores y los cables
sudo containerlab deploy -t netlab.clab.yml

# configurar la red (por orden)
./config-ip.sh
./config-vlans.sh
./config-ospf.sh
./config-nat.sh
