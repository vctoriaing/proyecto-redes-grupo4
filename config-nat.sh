#!/bin/bash
# config-nat.sh
echo "Configurando NAT MASQUERADE en r1 (salida eth4 = externo)..."
docker exec clab-netlab-r1 sysctl -w net.ipv4.ip_forward=1
docker exec clab-netlab-r1 sh -c \
  "iptables -t nat -C POSTROUTING -o eth4 -j MASQUERADE 2>/dev/null || \
   iptables -t nat -A POSTROUTING -o eth4 -j MASQUERADE"
echo "NAT configurado en r1."
