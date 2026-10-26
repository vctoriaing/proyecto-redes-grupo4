# NetLab Monitor - Proyecto Final de Redes y Comunicaciones

**Asignatura:** Redes y Comunicaciones <br>
**Carrera:** Ingeniería Civil Informática <br>
**Universidad Autónoma de Chile** <br>
**Grupo N°:** 4

---

## Integrantes y Roles 
| Nombre | Rol Asignado | Responsabilidades Principales | 
| :--- | :--- | :--- | 
| **Fiorella Bovet** | **Rol 1:** Infraestructura y Enrutamiento | Topología Containerlab (`netlab.clab.yml`), direccionamiento IP (`config-ip.sh`), VLANs (`config-vlans.sh`) y OSPF (`config-ospf.sh`). | 
| **[2]** | **Rol 2:** Servicios y NAT | Salida a Internet con NAT/iptables (`config-nat.sh`), servidores HTTP y Syslog/netcat. | 
| **Victoria Rojas** | **Rol 3:** Desarrollador y Auditor | Script de auditoría (`netlab\_monitor.py`), configuración (`monitor.json`), evidencias y documentación. | 

---

## Descripción de la Arquitectura de Red

El escenario implementa una infraestructura empresarial virtualizada en **Containerlab** integrada por:

1. **Segmento Clientes:** Hosts en **VLAN 10 (Administración)** y **VLAN 20 (Ventas)** conectados vía enlace Trunk 802.1Q al router de sede (`r2`).
2. **Núcleo de Enrutamiento Dinámico:** Tres routers (`r1`, `r2`, `r3`) interconectados en malla mediante enlaces WAN `/30` corriendo **OSPF en el Área 0**.
3. **Borde y Servicios:** Router de borde (`r1`) administrando el segmento de Servidores (HTTP en `srv-web` y Syslog en `srv-datos`) y aplicando **NAT (MASQUERADE)** para la salida controlada hacia el segmento `externo` (203.0.113.0/29).
4. **Auditoría Automatizada:** Script en Python puro (`netlab_monitor.py`) que audita la red capa por capa utilizando un archivo de configuración externo (`monitor.json`).

---

## Requisitos Previos e Instalación

Para desplegar y auditar este laboratorio es necesario contar con:

*   **Sistema Operativo:** Linux (Ubuntu 22.04 / 24.04 LTS recomendado) o **WSL2** en Windows.
*   **Docker Engine:** Instalado y en ejecución (`docker`).
*   **Containerlab:** Instalado para la orquestación de la topología (`containerlab`).
*   **Python 3.x:** Para la ejecución de `netlab_monitor.py` (**solo requiere la librería estándar nativa, no necesita `pip install`**).

---

## Estructura del Repositorio


```text
~/containerlab/proyecto/
├── README.md               # Guía general de uso y documentación del proyecto
├── netlab.clab.yml         # Definición declarativa de la topología en Containerlab
├── desplegar.sh            # Script maestro de despliegue automatizado
├── destruir.sh             # Script de limpieza y eliminación de entornos/bridges
├── config-ip.sh            # Asignación de direcciones IP e interfaces físicas
├── config-vlans.sh         # Configuración de subinterfaces 802.1Q y bridges VLAN
├── config-ospf.sh          # Configuración de enrutamiento dinámico OSPF (FRRouting)
├── config-nat.sh           # Reglas de IP Forwarding y MASQUERADE en r1
├── netlab_monitor.py       # Script auditor de red en Python (librería estándar)
├── monitor.json            # Matriz de inventario, rutas, pings y servicios esperados
├── evidencias/             # Evidencias de comandos en texto plano
│   └── historial.txt       # Historial de comandos ejecutados (`history`)
├── docs/                   # Documentación técnica y diagramas
│   ├── diagrama.png        # Diagrama de topología de red
│   ├── plan_vlsm.xlsx      # Tabla de subnetting VLSM
│   └── informe_tecnico.md  # Informe con análisis de capas y fallas
└── bitacora-ia.md          # Registro del uso, correcciones y rechazos de IA
