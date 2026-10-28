#!/bin/bash
# config-ip.sh
# ips de routers (enlaces, servidores, externo)
# las ips de las VLAN se ponen en config-vlans.sh

# r1
docker exec clab-netlab-r1 ip addr add 172.16.4.57/30 dev eth1
docker exec clab-netlab-r1 ip addr add 172.16.4.65/30 dev eth2
docker exec clab-netlab-r1 ip addr add 172.16.4.49/29 dev eth3
docker exec clab-netlab-r1 ip addr add 203.0.113.1/29 dev eth4
docker exec clab-netlab-r1 ip link set eth1 up
docker exec clab-netlab-r1 ip link set eth2 up
docker exec clab-netlab-r1 ip link set eth3 up
docker exec clab-netlab-r1 ip link set eth4 up
docker exec clab-netlab-r1 sysctl -w net.ipv4.ip_forward=1

# r2 (eth1 es el trunk, se configura en config-vlans.sh)
docker exec clab-netlab-r2 ip addr add 172.16.4.58/30 dev eth2
docker exec clab-netlab-r2 ip addr add 172.16.4.61/30 dev eth3
docker exec clab-netlab-r2 ip link set eth2 up
docker exec clab-netlab-r2 ip link set eth3 up
docker exec clab-netlab-r2 sysctl -w net.ipv4.ip_forward=1

# r3
docker exec clab-netlab-r3 ip addr add 172.16.4.66/30 dev eth1
docker exec clab-netlab-r3 ip addr add 172.16.4.62/30 dev eth2
docker exec clab-netlab-r3 ip link set eth1 up
docker exec clab-netlab-r3 ip link set eth2 up
docker exec clab-netlab-r3 sysctl -w net.ipv4.ip_forward=1

# srv-web
docker exec clab-netlab-srv-web ip addr add 172.16.4.50/29 dev eth1
docker exec clab-netlab-srv-web ip link set eth1 up
docker exec clab-netlab-srv-web ip route replace default via 172.16.4.49

# srv-datos
docker exec clab-netlab-srv-datos ip addr add 172.16.4.51/29 dev eth1
docker exec clab-netlab-srv-datos ip link set eth1 up
docker exec clab-netlab-srv-datos ip route replace default via 172.16.4.49

# externo
docker exec clab-netlab-externo ip addr add 203.0.113.2/29 dev eth1
docker exec clab-netlab-externo ip link set eth1 up
