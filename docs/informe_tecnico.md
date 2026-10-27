# Informe Técnico de Arquitectura y Auditoría de Red

**Proyecto Final:** NetLab Monitor  
**Asignatura:** Redes y Comunicaciones  
**Carrera:** Ingeniería Civil Informática  
**Universidad Autónoma de Chile**  
**Grupo N°:** 4  
**Integrantes:** Fiorella Bovet (Rol 1), Javier Vidal (Rol 2), Victoria Rojas (Rol 3)

---

## 1. Resumen Ejecutivo y Objetivos

El presente documento detalla el diseño, implementación y auditoría de la infraestructura de red empresarial virtualizada para el **Grupo 4**. El proyecto integra segmentación en Capa 2 (VLANs 802.1Q), enrutamiento dinámico en Capa 3 (OSPF Área 0), traducción de direcciones de red (NAT MASQUERADE) y servicios de aplicación en Capa 7 (HTTP y Syslog), junto con un sistema autodesarrollado de monitoreo automatizado en Python (`netlab_monitor.py`).

---

## 2. Plan de Direccionamiento VLSM (Bloque Asignado: `172.16.4.0/24`)

Siguiendo la metodología de asignación de mayor a menor número de hosts requeridos para optimizar el espacio de direcciones IPv4 sin solapamientos, se calculó la siguiente distribución de subredes:

| Subred / Segmento | Hosts Req. | Prefijo CIDR | Bits Host (n) | Capacidad IPs (2^n) | Hosts Útiles (2^n - 2) | Salto / Bloque | Dirección de Red | Máscara Decimal | Primer Host (Gateway) | Último Host | Broadcast |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **VLAN 10 (Administración)** | 25 | `/27` | 5 | 32 | 30 | 32 | `172.16.4.0` | `255.255.255.224` | `172.16.4.1` | `172.16.4.30` | `172.16.4.31` |
| **VLAN 20 (Ventas)** | 12 | `/28` | 4 | 16 | 14 | 16 | `172.16.4.32` | `255.255.255.240` | `172.16.4.33` | `172.16.4.46` | `172.16.4.47` |
| **Servidores (HTTP/Syslog)** | 6 | `/29` | 3 | 8 | 6 | 8 | `172.16.4.48` | `255.255.255.248` | `172.16.4.49` | `172.16.4.54` | `172.16.4.55` |
| **WAN 1 (r1 - r2)** | 2 | `/30` | 2 | 4 | 2 | 4 | `172.16.4.56` | `255.255.255.252` | `172.16.4.57` | `172.16.4.58` | `172.16.4.59` |
| **WAN 2 (r2 - r3)** | 2 | `/30` | 2 | 4 | 2 | 4 | `172.16.4.60` | `255.255.255.252` | `172.16.4.61` | `172.16.4.62` | `172.16.4.63` |
| **WAN 3 (r3 - r1)** | 2 | `/30` | 2 | 4 | 2 | 4 | `172.16.4.64` | `255.255.255.252` | `172.16.4.65` | `172.16.4.66` | `172.16.4.67` |
| **Red Externa (Simulada)** | 2 | `/29` | 3 | 8 | 6 | 8 | `203.0.113.0` | `255.255.255.248` | `203.0.113.1` | `203.0.113.6` | `203.0.113.7` |
| **TOTALES** | **51** | **-** | **-** | **76** | **62** | **76** | **-** | **-** | **-** | **-** | **-** |

---

## 3. Análisis Arquitectónico por Capas del Modelo OSI

El diseño de la red responde directamente a la pila de protocolos del modelo OSI/TCP-IP:

* **Capa 1/2 (Física y Enlace de Datos):**
  * Interconexión de contenedores Linux mediante puentes virtuales en Containerlab.
  * Segmentación mediante etiquetado **IEEE 802.1Q** en el enlace troncal (Trunk) entre el switch de sede (`sw-a`) y las subinterfaces `eth1.10` y `eth1.20` del router `r2`.
* **Capa 3 (Red y Enrutamiento):**
  * Direccionamiento IPv4 privado y asignación de gateways predeterminados en la primera IP de cada subred.
  * Enrutamiento dinámico mediante **OSPFv2 en el Área 0** configurado en FRRouting entre `r1`, `r2` y `r3`. La ruta por defecto (`0.0.0.0/0`) se origina en `r1` hacia Internet.
* **Capa 3/4 (Seguridad y Traducción - NAT):**
  * Regla de **NAT MASQUERADE** en la interfaz de salida de `r1` (`eth2` hacia `externo`). Permite ocultar las direcciones privadas (`172.16.4.0/24`) y sustituirlas por la IP pública de borde (`203.0.113.1`).
* **Capa 7 (Aplicación y Servicios):**
  * Servicio HTTP escuchando en `srv-web` (`172.16.4.50:80/TCP`).
  * Servicio Syslog/Datos escuchando en `srv-datos` (`172.16.4.51:1234/TCP`).

---

## 4. Diagnóstico de Falla Controlada (Letra D: VLAN ID 99 en `pc-ventas`)

### 4.1 Descripción del Incidente
En el escenario de prueba de la Pregunta 3, se configuró intencionalmente una VLAN ID incorrecta (`VLAN 99`) en el cliente `pc-ventas` (el cual pertenece originalmente a la VLAN 20).

### 4.2 Aislamiento de la Falla en la Escalera de Diagnóstico
Al ejecutar `netlab_monitor.py`, se observó el siguiente comportamiento:
1. **Capa 1/2 (Inventario):** `[OK]` — El contenedor `pc-ventas` está activo.
2. **Capa 2 (Interfaces/VLANs):** `[OK]` en `r2`, pero `pc-ventas` queda etiquetado en un dominio de difusión inexistente.
3. **Capa 3/4 (Conectividad / Ping):** **`[FAIL]`** — El tráfico enviado desde `pc-ventas` hacia `srv-web` o `externo` no recibe respuesta ICMP.

### 4.3 Justificación Técnica
La falla pertenece estrictamente a la **Capa 2 (Enlace de Datos)**. Al estar en la VLAN 99, las tramas Ethernet enviadas por `pc-ventas` llevan un Tag 802.1Q que el router `r2` descarta en su enlace troncal, ya que `r2` solo escucha subinterfaces para VLAN 10 y VLAN 20. Al no haber gateway en la VLAN 99, el paquete nunca alcanza la Capa 3 (IP) para ser enrutado.

---

## 5. Modificación de Infraestructura (Letra D: Ampliación VLAN 20 de `/28` a `/27`)

### 5.1 Requerimiento del Cambio
En la Pregunta 4 se solicitó ampliar la capacidad de la **VLAN 20 (Ventas)** para soportar una mayor cantidad de hosts, modificando su máscara de subred de `/28` (14 hosts) a `/27` (30 hosts).

### 5.2 Recálculo del Plan VLSM (Sin Solapamiento)
Al cambiar la VLAN 20 a `/27`, su bloque de direcciones se expande, ocupando desde `172.16.4.32` hasta `172.16.4.63`. Para evitar solapamientos con las subredes posteriores, se reubicaron las subredes de Servidores y enlaces WAN:
1. **VLAN 10 (Administración):** `172.16.4.0/27` (Hosts: `.1` a `.30`, Broadcast: `.31`) — *Sin cambios*.
2. **VLAN 20 (Ventas - Ampliada):** **`172.16.4.32/27`** (Gateway: `.33`, Hosts: `.34` a `.62`, Broadcast: `.63`).
3. **Servidores (Reubicada):** **`172.16.4.64/29`** (Gateway: `.65`, Hosts: `.66` a `.70`, Broadcast: `.71`).
4. **WAN 1 (`r1`-`r2`):** `172.16.4.72/30`
5. **WAN 2 (`r2`-`r3`):** `172.16.4.76/30`
6. **WAN 3 (`r3`-`r1`):** `172.16.4.80/30`

### 5.3 Actualización en `monitor.json`
El desacoplamiento del script permitió reflejar este cambio modificando únicamente el archivo `monitor.json` (actualizando la máscara, la IP de `pc-ventas` a `172.16.4.34` y la de los servidores), sin requerir cambios en el código Python de `netlab_monitor.py`.
