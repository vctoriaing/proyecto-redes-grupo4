#!/bin/bash
echo "Configurando NAT MASQUERADE..."
sudo docker exec clab-netlab-r1 sysctl -w net.ipv4.ip_forward=1
sudo docker exec clab-netlab-r1 iptables -t nat -A POSTROUTING -o eth1 -j MASQUERADE
echo "NAT configurado en r1."
