#!/bin/bash
# config-ospf.sh
# OSPF area 0 en r1, r2 y r3 con FRRouting (vtysh).

# esperar a que FRR arranque
sleep 5

# r1 (tambien anuncia la red externa para que los clientes lleguen a externo)
docker exec clab-netlab-r1 vtysh \
  -c "configure terminal" \
  -c "router ospf" \
  -c "ospf router-id 1.1.1.1" \
  -c "network 172.16.4.56/30 area 0" \
  -c "network 172.16.4.64/30 area 0" \
  -c "network 172.16.4.48/29 area 0" \
  -c "network 203.0.113.0/29 area 0"

# r2
docker exec clab-netlab-r2 vtysh \
  -c "configure terminal" \
  -c "router ospf" \
  -c "ospf router-id 2.2.2.2" \
  -c "network 172.16.4.0/27 area 0" \
  -c "network 172.16.4.32/28 area 0" \
  -c "network 172.16.4.56/30 area 0" \
  -c "network 172.16.4.60/30 area 0"

# r3
docker exec clab-netlab-r3 vtysh \
  -c "configure terminal" \
  -c "router ospf" \
  -c "ospf router-id 3.3.3.3" \
  -c "network 172.16.4.60/30 area 0" \
  -c "network 172.16.4.64/30 area 0"
