# Bitácora de Uso de IA 

Este documento registra las consultas realizadas a la Inteligencia Artificial, las respuestas obtenidas y el análisis crítico aplicado por el estudiante para la construcción del script `netlab_monitor.py`.

---

**Integrante 3 (Rol: Desarrollador y Auditor)**

---

### 1. Desacoplamiento de la configuración (`monitor.json`)

**Prompt (Pregunta a la IA):** 
> *"¿Por qué es mejor desacoplar la configuración en un archivo monitor.json en lugar de poner las IPs y puertos directamente en el código Python?"*

**Respuesta de la IA (Resumen):** 
La IA explicó el patrón de **Separación de Intereses (Separation of Concerns)** e **Infraestructura como Código (IaC)**. Indicó que hardcodear hace que el script sea rígido. El JSON actúa como la "fuente de la verdad", permitiendo que si se agrega una VLAN o un servidor (como el Cambio Asignado de la Pregunta 4), no se modifique el código Python, solo el JSON.

**Decisión del Estudiante:** 
**Aceptado y aplicado.** Se implementó el archivo `monitor.json` para almacenar los nodos, rutas esperadas y servicios, cumpliendo con el requisito del proyecto.

---

### 2. Uso exclusivo de la librería estándar (Rechazo de librerías externas)

**Prompt (Pregunta a la IA):** 
> *"¿Cómo puedo hacer peticiones HTTP o conectarme por SSH a los routers desde Python?"*

**Respuesta de la IA (Resumen):** 
La IA sugirió inicialmente usar librerías externas como `paramiko` (para SSH) o `requests` (para validar HTTP). 

**Decisión del Estudiante:** 
**Rechazado y Corregido.** El PDF prohíbe librerías externas y exige solo librerías estándar. Se reemplazó la sugerencia de la IA por:
*   **`subprocess` en vez de SSH:** Containerlab ya corre sobre Docker en la misma máquina. Usar `docker exec` es instantáneo, no requiere instalar servicios SSH ni gestionar contraseñas.
*   **`socket` en vez de `requests`:** Interactúa directamente con la pila TCP/UDP (Capa 4). Hace un handshake en milisegundos para ver si el puerto está `LISTEN` sin la sobrecarga de interpretar HTTP.
*(**Nota para el video - Pregunta 5.6:** Usa exactamente esta justificación para responder qué rechazaste de la IA y por qué).*

---

### 3. Metodología de diagnóstico (Escalera de fallas)

**Prompt (Pregunta a la IA):** 
> *"¿En qué orden debo programar las verificaciones de red para que el diagnóstico tenga sentido lógico?"*

**Respuesta de la IA (Resumen):** 
La IA recomendó el enfoque **Bottom-Up (de abajo hacia arriba)**. Primero verificar lo físico/lógico (contenedores, interfaces), luego el enrutamiento (tablas), después la conectividad (pings) y finalmente los servicios (puertos).

**Decisión del Estudiante:** 
**Aceptado y aplicado.** El script sigue esta estructura:
1. Inventario (Capa 1/2) -> 2. VLANs -> 3. Rutas -> 4. Ping -> 5. Puertos (Capa 7).
Si el contenedor está apagado, no tiene sentido hacer ping. Esto ahorra tiempo de diagnóstico.

---

### 4. Manejo de errores en `docker exec` (Rutas)

**Prompt (Pregunta a la IA):** 
> *"¿Qué pasa si el comando docker exec falla porque el contenedor está apagado, y cómo evito que el script entero se caiga?"*

**Respuesta de la IA (Resumen):** 
La IA explicó que `subprocess.run` puede lanzar excepciones. Recomendó usar bloques `try/except` y capturar el `returncode` del subproceso. Si el returncode no es 0, se debe retornar un estado de error controlado.

**Decisión del Estudiante:** 
**Aceptado y modificado.** Se implementó la función `ejecutar_comando(nodo, comando)` que captura el error de Docker y devuelve un mensaje en lugar de romper el programa.
*(**Nota para el video - Pregunta 5.1:** Explica que tu función lee el JSON, ejecuta `docker exec`, y si falla el contenedor, el bloque `try/except` lo captura y lo reporta como un `[FAIL]` en la capa de Enlace/Inventario, permitiendo que el script siga auditando el resto de la red).*

---

### 5. Estructuración del README.md y formato Markdown

**Prompt (Pregunta a la IA):** 
> *"Necesito armar el README.md del proyecto. ¿Cómo lo estructuro para que cumpla con la rúbrica de documentación y explique claramente cómo se ejecuta el monitor y la escalera de fallas? Además, tengo problemas con el formato de Markdown, se me juntan las líneas y se me queda todo dentro de un cuadro gris."*

**Respuesta de la IA (Resumen):** 
La IA sugirió una estructura completa dividida en: Roles, Arquitectura, Requisitos, Estructura de Carpetas, Guía de Ejecución y Explicación de las 8 verificaciones. Para solucionar los problemas de formato, la IA recomendó:
1. Usar la etiqueta HTML `<br>` al final de las líneas para forzar los saltos de línea.
2. Usar tres comillas invertidas (```) al principio y al final para delimitar los bloques de código (como la estructura de carpetas) y evitar que el texto de abajo se absorbiera dentro del cuadro.

**Decisión del Estudiante:** 
**Aceptado y aplicado.** Se implementó la estructura sugerida por la IA. Sin embargo, el estudiante corrigió y adaptó el texto para incluir la sección de "Simulación (Mocks) con `test_monitor.py`" (la cual la IA no había considerado) y se aseguró de que la explicación de la "Escalera de Diagnóstico" coincidiera exactamente con la lógica programada en el archivo `netlab_monitor.py`.

---

### 6. Creación del archivo de configuración `monitor.json`

**Prompt (Pregunta a la IA):** 
> *"Tengo que crear un archivo monitor.json para mi proyecto de redes que sea externo al código Python. El bloque de red de mi grupo es 172.16.4.0/24 y la red externa es 203.0.113.0/29. ¿Qué estructura de diccionario en JSON me recomiendas para guardar los nodos, las rutas esperadas, los servicios (puertos 80 y 1234) y la matriz de pings?"*

**Respuesta de la IA (Resumen):** 
La IA propuso una estructura con llaves principales: `nodos`, `rutas_esperadas`, `servicios` y `comandos`. Sugirió guardar las IPs como strings y los puertos como enteros. 

**Decisión del Estudiante:** 
**Aceptado y modificado.** Se utilizó la estructura propuesta, pero se modificaron los valores por defecto. Por ejemplo, la IA no incluía la llave `pruebas_conectividad` para definir explícitamente el origen y destino de los pings. El estudiante la agregó para que el script de Python pudiera iterar sobre ella de forma más limpia. También se ajustaron las IPs para que coincidieran con el plan VLSM (Subnetting) calculado.

---

### 7. Creación del script principal `netlab_monitor.py`

**Prompt (Pregunta a la IA):** 
> *"Escríbeme el esqueleto de un script en Python usando SOLO las librerías estándar (subprocess, socket, json, argparse, datetime, os). Debe tener 8 funciones (una por cada verificación de red) y una función principal con argparse. Usa subprocess.run para simular 'docker exec <nodo> <comando>' y maneja las excepciones si el comando falla."*

**Respuesta de la IA (Resumen):** 
La IA generó el código base con las importaciones correctas y un bloque `if __name__ == "__main__":` bien estructurado. Utilizó `subprocess.run` con `capture_output=True` y `text=True`, y añadió un bloque `try/except` para capturar errores de timeout.

**Decisión del Estudiante:** 
**Aceptado y adaptado.** La estructura de la IA era correcta, pero el estudiante tuvo que programar la lógica de comparación dentro de cada función. Por ejemplo, para `verificar_rutas`, la IA no sabía cómo comparar el output de `ip route` con el JSON; el estudiante escribió el bucle `for red in rutas_esperadas:` para buscar si la subred estaba presente en la salida del comando usando `if red in salida:`. Además, se configuró el código de salida del sistema (`exit(0)` si todo está OK, `exit(1)` si falla), tal como exige la rúbrica en la verificación número 8.

---

### 8. Creación del archivo de simulación `test_monitor.py` (Mocks)

**Prompt (Pregunta a la IA):** 
> *"Estoy programando en GitHub Codespaces y no tengo el laboratorio de Containerlab levantado porque mis compañeros lo están armando en otra PC. ¿Cómo puedo probar la lógica de mi script netlab_monitor.py sin que Docker me lance errores de 'contenedor no encontrado'?"*

**Respuesta de la IA (Resumen):** 
La IA explicó el concepto de **Mocks (objetos simulados)**. Recomendó crear un archivo de prueba aparte (ej. `test_monitor.py`) donde la función `ejecutar_comando` no llame a Docker, sino que devuelva respuestas falsas predefinidas (como el texto real de un `ip route` o un `vtysh`).

**Decisión del Estudiante:** 
**Aceptado y aplicado.** Se creó el archivo `test_monitor.py` implementando una función que usa condicionales (`if "hostname" in comando: return True...`) para simular que todos los equipos están en verde. Esto permitió validar que las funciones de Python no tuvieran errores de sintaxis y que el reporte se generara correctamente, demostrando una buena práctica de desarrollo (aislar la lógica de negocio de la infraestructura).

---

### 9. Integración final con la infraestructura (Ajuste de Datos vs Lógica)

**Prompt (Pregunta a la IA):** 
> *"Mis compañeros están armando la red en Containerlab. ¿Qué partes de mi código debo cambiar para que el monitor funcione con la red real, y qué partes debo dejar intactas?"*

**Respuesta de la IA (Resumen):** 
La IA explicó que gracias al diseño desacoplado (usando `monitor.json`), la lógica de Python (`netlab_monitor.py`) no debería modificarse. Los cambios de la red real solo afectan la "capa de datos" (el JSON). Si la red cambia, solo se edita el JSON. Sin embargo, si los compañeros usan comandos de Linux distintos (ej. `nftables` en vez de `iptables`), o nombres de interfaces diferentes (ej. `eth2` en vez de `eth1`), se debe ajustar el comando exacto dentro de la función de Python.

**Decisión del Estudiante:** 
**Aceptado y planificado.** Se estableció un plan de integración:
1. Solicitar al Rol 1 las IPs finales del VLSM y los nombres exactos de las interfaces de red (`.10` y `.20`) para actualizarlos en el `monitor.json` y en la verificación de interfaces.
2. Solicitar al Rol 2 el puerto exacto configurado en `srv-datos` para actualizar la matriz de servicios en el JSON.
3. Ajustar el comando de la función `verificar_nat` dependiendo de si Rol 2 usó `iptables` o `nftables`.

---

### 10. Creación del Informe Técnico y Formato de Tablas VLSM

**Prompt (Pregunta a la IA):** 
> *"Necesito armar un informe técnico con una tabla VLSM muy detallada. ¿Cómo puedo crear tablas en Markdown (formato raw) para que se vean bien en GitHub? Además, ayúdame a entender los conceptos de 'Bits Host' y 'Salto de bloque' para poder explicarlos en el informe."*

**Respuesta de la IA (Resumen):** 
La IA explicó cómo funcionan las tablas en Markdown usando la barra vertical `|` para las columnas y los guiones `-` para separar el encabezado. También explicó que el "Salto de bloque" es el valor de \(2^n\) (donde \(n\) son los bits de host) y que los hosts útiles siempre son \(2^n - 2\) (restando la dirección de red y la de broadcast). 

**Decisión del Estudiante:** 
**Aceptado y aplicado.** Se utilizó el formato Markdown crudo (`| Columna | Columna |`) para crear la tabla en el archivo `informe_tecnico.md`. Además, se trasladó esa misma tabla a un archivo Excel (`plan_vlsm.xlsx`) para cumplir con el requisito de la rúbrica. Los conceptos explicados por la IA fueron fundamentales para redactar la sección de justificación técnica de la falla (VLAN 99) y el recálculo del cambio a `/27`, demostrando que el estudiante comprendió la matemática detrás del subnetting.

---

**Integrante 1 - Fiorella Bovet (Rol: Infraestructura y Enrutamiento)**

---
### 1. Entorno (GitHub Codespaces) y Git

**Prompt (Pregunta a la IA):** 
> *"No sé nada de Git ni GitHub. ¿Es bueno y efectivo usar Codespaces para este proyecto y mi rol?"*

**Respuesta de la IA (Resumen):** 
Explicó los pasos de Git (clone, add, commit, pull, push) y entregó un devcontainer.json que instala Docker y Containerlab. Advirtió dos límites: la cuota gratis de horas y que debía comprobarse el soporte de VLAN 802.1Q.

**Decisión del Estudiante:** 
**Aceptado y adaptado.** Se usó Codespaces. Los archivos ya existían en el repositorio como plantilla vacía (realizado por rol 3), así que se completó su contenido y se subió solo lo propio (git add archivo por archivo), sin la carpeta clab-netlab/ ni los archivos de otros roles.

---

### 2. Codespace + subir códigos a GitHub

**Prompt (Pregunta a la IA):** 
> *"Dame un paso a paso de como hacer lo del codespace para luego subir los codigos porque no sé muy bien como usar github"*

**Respuesta de la IA (Resumen):** 
Parte A: Tener acceso al repositorio
Parte B: Agregar el archivo de configuración del Codespace
Parte C: Crear el Codespace
Parte D: Subir tus archivos al Codespace
Parte E: Probar que todo funciona
Parte F: Subir tus códigos a GitHub

**Decisión del Estudiante:** 
**Aceptado y aplicado.** Se siguieron las indicaciones dadas por la IA para lograr subir los códigos correctamente.

---

### 3. Elementos que no están en clases

**Prompt (Pregunta a la IA):** 
> *"¿Qué partes del proyecto no se ven en las clases y cómo se resuelven?"*

**Respuesta de la IA (Resumen):** 
1. FRRouting y vtysh (OSPF): el enunciado dice que OSPF se investiga por cuenta propia. Los routers usan la imagen de FRR y se configuran con vtysh -c.
2. Crear los bridges del host antes del deploy: ip link add name sw-a type bridge. Containerlab no los crea ni los borra, por eso destruir.sh los elimina.
3. ip route replace default en lugar de add: Docker ya agrega una ruta por defecto en eth0, y replace evita el error de ruta ya existente.

**Decisión del Estudiante:** 
**Aceptado y comprobado en el laboratorio.** Los tres puntos funcionaron al desplegar (vecinos OSPF en Full, bridges creados, clientes con su gateway).

---
### 4. FRRouting y "vtysh" (configuración de OSPF)

**Prompt (Pregunta a la IA, resumen):** 
> *"Soy la encargada del Rol 1 (infraestructura y enrutamiento) y necesito configurar OSPF en los tres routers (`config-ospf.sh`). El código debe usar los comandos de las clases, con comentarios cortos y claros para yo entender lo que está dentro."*

**Respuesta de la IA (Resumen):** 
La IA entregó "config-ospf.sh", que entra a cada router con "docker exec" y le pasa comandos a "vtysh", la consola de FRRouting, usando un "-c" por cada comando: "configure terminal", "router ospf", "ospf router-id", y un "network <red> area 0" por cada red directamente conectada. Cada router lleva un router-id distinto (1.1.1.1, 2.2.2.2 y 3.3.3.3), y r1 anuncia también "203.0.113.0/29" para que los clientes lleguen a externo. Explicó que "frr/daemons" con "ospfd=yes" enciende el proceso OSPF, que la "\" solo parte un comando largo en varias líneas, y qué es un vecino OSPF y los estados que atraviesa hasta "Full".

**Decisión del Estudiante:** 
**Aceptado y comprobado.** Esta parte no se vio en clases, así que se ejecutó el script y se verificó en el laboratorio. La primera vez falló porque "ospfd" no estaba corriendo. Corregido eso, "show ip ospf neighbor" mostró los vecinos en "Full" y "ip route" mostró rutas con "proto ospf". Se revisó cada comando para poder explicarlo en la defensa.

### 5. Imagen de FRR inexistente

**Prompt (Pregunta a la IA):** 
> *✗ Failed to pull image docker.io/frrouting/frr:v9.1.0: Error response from daemon: failed to resolve reference "docker.io/frrouting/frr:v9.1.0": docker.io/frrouting/frr:v9.1.0: not found*

**Respuesta de la IA (Resumen):** 
La IA había puesto frrouting/frr:v9.1.0 en el .yml sin comprobar que existiera. El deploy falló con not found. Se sugirió buscar una versión existente.

**Decisión del Estudiante:** 
**Aceptado y corregido.** Se probó docker pull frrouting/frr:v8.4.1, que sí existe, y se cambió la imagen en netlab.clab.yml.

---

### 6. Archivo frr/daemons dañado

**Prompt (Pregunta a la IA):** 
> *@foshiguro ➜ /workspaces/proyecto-redes-grupo4 (main) $ ./config-ospf.sh
% Can't open configuration file /etc/frr/vtysh.conf due to 'No such file or directory'.
ospfd is not running
% Can't open configuration file /etc/frr/vtysh.conf due to 'No such file or directory'.
ospfd is not running
% Can't open configuration file /etc/frr/vtysh.conf due to 'No such file or directory'.
ospfd is not running*

**Respuesta de la IA (Resumen):** 
Al revisar el interior del router se vio que en daemons se habían pegado también las líneas del comando (mkdir, cat > ... << 'EOF'). Por eso ospfd no arrancaba (ospfd is not running).

**Decisión del Estudiante:** 
**Aceptado y corregido.** Se borró el archivo, se escribió de nuevo desde la terminal y se verificó con ps que ospfd ya corría. Los vecinos pasaron a Full.

---

### 7. Ping a srv-web fallaba por el firewall del host

**Prompt (Pregunta a la IA):** 
> *@foshiguro ➜ /workspaces/proyecto-redes-grupo4 (main) $ grep "packet loss" evidencias/pings.txt
4 packets transmitted, 4 received, 0% packet loss, time 3098ms
4 packets transmitted, 4 received, 0% packet loss, time 3068ms
4 packets transmitted, 0 received, 100% packet loss, time 3060ms*

**Respuesta de la IA (Resumen):** 
La IA planteó una hipótesis: la política FORWARD DROP del host descartaba el tráfico que cruza el bridge sw-b, porque br_netfilter lo pasaba por iptables. Pidió comprobarlo antes de cambiar nada.

**Decisión del Estudiante:** 
**Aceptado tras verificar.** sysctl net.bridge.bridge-nf-call-iptables valía 1; al ponerlo en 0 el ping funcionó. Se agregó la línea a desplegar.sh y se volvió a guardar la evidencia (los tres pings con 0 % de pérdida).

---

### 8. Preguntas para entender los scripts antes de entregarlos
**Prompt (Pregunta a la IA):** 
> *"¿Para qué sirve #!/bin/bash?", "¿Por qué config-ospf.sh tiene \?" y "¿Por qué se llama vecinos?"*

**Respuesta de la IA (Resumen):** 
Explicó que #!/bin/bash indica con qué programa se ejecuta el script; que la \ continúa un mismo comando en la línea siguiente; y que "vecino" es un router OSPF conectado directamente, que pasa por varios estados hasta Full.

**Decisión del Estudiante:** 
**Aceptado y corregido.** Se hicieron estas preguntas para poder explicar cada script en el video, siguiendo la regla del curso: lo que no se pueda explicar, no se entrega.