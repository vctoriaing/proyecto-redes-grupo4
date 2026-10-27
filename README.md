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
| **Javier Vidal** | **Rol 2:** Servicios y NAT | Salida a Internet con NAT/iptables (`config-nat.sh`), servidores HTTP y Syslog/netcat. | 
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
├── test_monitor.py         # Script de simulación (Mocks) para probar la lógica sin red
├── monitor.json            # Matriz de inventario, rutas, pings y servicios esperados
├── evidencias/             # Evidencias de comandos en texto plano
│   └── historial.txt       # Historial de comandos ejecutados (`history`)
├── docs/                   # Documentación técnica y diagramas
│   ├── diagrama.png        # Diagrama de topología de red
│   ├── plan_vlsm.xlsx      # Tabla de subnetting VLSM
│   └── informe_tecnico.md  # Informe con análisis de capas y fallas
└── bitacora-ia.md          # Registro del uso, correcciones y rechazos de IA
```

---

## Guía de Despliegue y Ejecución

### 1. Desplegar el laboratorio
Ejecutar el script de despliegue principal. Este se encarga de levantar los contenedores, aplicar las IPs, configurar las VLANs, OSPF y las reglas de NAT en el orden correcto:

```bash
sudo ./desplegar.sh
```
*(Nota: Para destruir el laboratorio y limpiar los bridges que Containerlab no elimina, ejecutar `sudo ./destruir.sh`)*

### 2. Ejecutar el Monitor de Auditoría
Una vez que la red esté desplegada y convergida, ejecutar el script de Python leyendo el archivo de configuración externo:

```bash
python3 netlab_monitor.py --config monitor.json
```

---

## ¿Cómo leer el reporte del Monitor? (Escalera de Diagnóstico)

El script `netlab_monitor.py` no hace pruebas al azar. Sigue la **escalera de diagnóstico del curso** (de Capa 1 a Capa 7). Esto significa que si una capa inferior falla, el script lo detectará primero para ahorrar tiempo de resolución.

Las 8 verificaciones que se imprimen en pantalla y se guardan en el reporte son:

1. **Inventario (Capa 1/2):** Verifica que los contenedores (nodos) estén vivos usando `docker exec`.
2. **Interfaces y VLANs (Capa 2):** Revisa que las subinterfaces 802.1Q en `r2` existan (`ip -br a`).
3. **Rutas (Capa 3):** Compara la tabla `ip route` de cada router contra las rutas esperadas en el JSON. (Diferencia entre ruta estática `S` y aprendida por OSPF `O`).
4. **Conectividad (Capa 3/4):** Realiza ping desde los clientes hacia los servidores y hacia el exterior (matriz de conectividad).
5. **Servicios (Capa 7):** Usa sockets de Python para intentar conectarse a los puertos HTTP (80) y Syslog, validando que la aplicación esté escuchando.
6. **OSPF (Capa 3):** Verifica que los vecinos estén en estado `Full` para asegurar que las rutas dinámicas se propagaron.
7. **NAT (Capa 3/4):** Revisa las reglas de MASQUERADE en `r1` y confirma que el tráfico sale con la IP del router (no la del cliente).
8. **Reporte:** Genera un archivo de texto en la carpeta `evidencias/` con la fecha, el estado `[OK]` o `[FAIL]` de cada prueba y la capa exacta donde ocurrió el fallo.

*Si el script finaliza con fallos, el sistema devuelve un código de salida distinto de cero, lo que permite automatizar alertas.*

---

## Pruebas Unitarias y Simulación (Entorno sin Red)

Dado que el script se basa en leer salidas de `docker exec`, se diseñó un **entorno de simulación (Mocks)** en el archivo `test_monitor.py` para probar la lógica del código sin necesidad de tener el laboratorio levantado.

**¿Para qué sirve?**
Permite validar la lógica de comparación de rutas y la generación de reportes. Si la red falla, asegura que el problema es de infraestructura y no de un error de programación.

```bash
python3 test_monitor.py
```

---

## Uso del script con IA (Bitácora)

El desarrollo de este proyecto integró herramientas de IA para la generación de código base. Todo el proceso de prompts, correcciones y rechazos se encuentra documentado en el archivo [`bitacora-ia.md`](bitacora-ia.md).
