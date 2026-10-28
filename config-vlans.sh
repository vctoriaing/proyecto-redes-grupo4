#!/bin/bash
# config-vlans.sh
# subinterfaces VLAN 802.1Q en r2 (trunk) y en los clientes.
# los switches sw-a y sw-b son bridges del host y dejan pasar los tags

# r2: trunk con VLAN 10 y VLAN 20
docker exec clab-netlab-r2 ip link add link eth1 name eth1.10 type vlan id 10
docker exec clab-netlab-r2 ip addr add 172.16.4.1/27 dev eth1.10
docker exec clab-netlab-r2 ip link add link eth1 name eth1.20 type vlan id 20
docker exec clab-netlab-r2 ip addr add 172.16.4.33/28 dev eth1.20
docker exec clab-netlab-r2 ip link set eth1 up
docker exec clab-netlab-r2 ip link set eth1.10 up
docker exec clab-netlab-r2 ip link set eth1.20 up

# pc-admin: VLAN 10
docker exec clab-netlab-pc-admin ip link add link eth1 name eth1.10 type vlan id 10
docker exec clab-netlab-pc-admin ip addr add 172.16.4.2/27 dev eth1.10
docker exec clab-netlab-pc-admin ip link set eth1 up
docker exec clab-netlab-pc-admin ip link set eth1.10 up
docker exec clab-netlab-pc-admin ip route replace default via 172.16.4.1

# pc-ventas: VLAN 20
docker exec clab-netlab-pc-ventas ip link add link eth1 name eth1.20 type vlan id 20
docker exec clab-netlab-pc-ventas ip addr add 172.16.4.34/28 dev eth1.20
docker exec clab-netlab-pc-ventas ip link set eth1 up
docker exec clab-netlab-pc-ventas ip link set eth1.20 up
docker exec clab-netlab-pc-ventas ip route replace default via 172.16.4.33
