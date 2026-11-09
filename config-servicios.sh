#!/bin/bash
# config-servicios.sh - Levanta los servicios de los servidores

# srv-web: servidor HTTP en el puerto 80
docker exec -d clab-netlab-srv-web python3 -m http.server 80

# srv-datos: servicio con netcat en el puerto TCP 1234
docker exec -d clab-netlab-srv-datos sh -c 'while true; do nc -l -p 1234; done'
