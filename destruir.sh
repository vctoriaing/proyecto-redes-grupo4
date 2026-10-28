#!/bin/bash
# destruir.sh - borra lab y los bridges
# uso: ./destruir.sh   (desde carpeta del proyecto)

# borrar contenedores y cables
sudo containerlab destroy -t netlab.clab.yml

# borrar los bridges (no se borran solos
sudo ip link del sw-a
sudo ip link del sw-b
