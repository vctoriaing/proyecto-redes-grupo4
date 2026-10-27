#!/usr/bin/env python3
import subprocess
import socket
import json
import argparse
import datetime
import os

# Variables globales para colores (opcional, para que se vea pro en el video)
OK = "[ OK ]"
FAIL = "[FAIL]"

def cargar_configuracion(ruta):
    try:
        with open(ruta, 'r') as archivo:
            return json.load(archivo)
    except Exception as e:
        print(f"{FAIL} Error al leer el JSON: {e}")
        exit(1)

def ejecutar_comando(nodo, comando):
    """Ejecuta un comando dentro de un contenedor. Retorna (True/False, salida)."""
    try:
        # Simulamos docker exec. En un entorno real, usa ["docker", "exec", nodo, "bash", "-c", comando]
        # Para pruebas sin red, puedes cambiar esto por leer archivos .txt
        resultado = subprocess.run(
            ["docker", "exec", nodo, "bash", "-c", comando],
            capture_output=True, text=True, timeout=5
        )
        if resultado.returncode == 0:
            return True, resultado.stdout
        return False, resultado.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout: El nodo no responde."
    except Exception as e:
        return False, str(e)

def verificar_inventario(config):
    print("\n--- [1] Verificando Inventario ---")
    fallos = 0
    for nodo in config["nodos"]:
        exito, _ = ejecutar_comando(nodo, "hostname")
        if exito:
            print(f"{OK} Nodo {nodo} está en ejecución.")
        else:
            print(f"{FAIL} Nodo {nodo} NO responde (Capa: Enlace/Contenedor).")
            fallos += 1
    return fallos == 0

def verificar_interfaces(config):
    print("\n--- [2] Verificando Interfaces y VLANs ---")
    # Revisamos las subinterfaces VLAN en r2 (deben tener '.10' o '.20' en el nombre)
    exito, salida = ejecutar_comando("r2", "ip -br a")
    if not exito:
        print(f"{FAIL} No se pudo consultar r2 (Capa: Enlace).")
        return False
    
    if "eth1.10" in salida or "eth1.20" in salida or "vlan" in salida.lower():
        print(f"{OK} Subinterfaces VLAN detectadas en r2.")
        return True
    else:
        print(f"{FAIL} No se encontraron subinterfaces VLAN en r2 (Capa: VLAN).")
        return False

def verificar_rutas(config):
    print("\n--- [3] Verificando Rutas ---")
    todo_ok = True
    for router, rutas_esperadas in config["rutas_esperadas"].items():
        exito, salida = ejecutar_comando(router, "ip route")
        if not exito:
            print(f"{FAIL} No se pudo leer rutas de {router} (Capa: Enlace).")
            todo_ok = False
            continue
        
        for red in rutas_esperadas:
            if red in salida:
                print(f"{OK} {router} tiene la ruta {red}.")
            else:
                print(f"{FAIL} {router} NO conoce la ruta {red} (Capa: Rutas/OSPF).")
                todo_ok = False
    return todo_ok

def verificar_conectividad(config):
    print("\n--- [4] Verificando Conectividad (Ping) ---")
    todo_ok = True
    for prueba in config["pruebas_conectividad"]:
        origen = prueba["origen"]
        destino = prueba["destino_ip"]
        # Ping con 1 paquete y timeout de 2 segundos para no colgar el script
        exito, _ = ejecutar_comando(origen, f"ping -c 1 -W 2 {destino}")
        if exito:
            print(f"{OK} {origen} -> {destino} ({prueba['descripcion']}).")
        else:
            print(f"{FAIL} {origen} NO llega a {destino} (Capa: IP/Gateway o NAT).")
            todo_ok = False
    return todo_ok

def verificar_servicios(config):
    print("\n--- [5] Verificando Servicios (Sockets) ---")
    todo_ok = True
    for servicio in config["servicios"]:
        ip = servicio["ip"]
        puerto = servicio["puerto"]
        try:
            # Intentamos conectar por Socket (TCP)
            with socket.create_connection((ip, puerto), timeout=2):
                print(f"{OK} Servicio en {ip}:{puerto} está escuchando.")
        except (socket.timeout, ConnectionRefusedError):
            print(f"{FAIL} Servicio en {ip}:{puerto} NO responde (Capa: Servicios).")
            todo_ok = False
    return todo_ok

def verificar_ospf(config):
    print("\n--- [6] Verificando Vecinos OSPF ---")
    # FRRouting usa el comando 'vtysh' para mostrar el estado
    exito, salida = ejecutar_comando("r1", "vtysh -c 'show ip ospf neighbor'")
    if not exito:
        print(f"{FAIL} No se pudo consultar OSPF en r1 (Capa: Enlace).")
        return False
    
    if "Full" in salida:
        print(f"{OK} Vecinos OSPF en estado Full detectados en r1.")
        return True
    else:
        print(f"{FAIL} Vecinos OSPF NO están en Full (Capa: Rutas/OSPF).")
        return False

def verificar_nat(config):
    print("\n--- [7] Verificando NAT en r1 ---")
    exito, salida = ejecutar_comando("r1", "iptables -t nat -L -n -v")
    if not exito:
        print(f"{FAIL} No se pudo consultar iptables en r1 (Capa: Enlace).")
        return False
        
    if "MASQUERADE" in salida:
        print(f"{OK} Regla NAT (MASQUERADE) encontrada en r1.")
        return True
    else:
        print(f"{FAIL} No hay reglas NAT activas en r1 (Capa: NAT).")
        return False

def generar_reporte(resultados):
    print("\n--- [8] Generando Reporte ---")
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_archivo = f"evidencias/reporte_netlab_{datetime.datetime.now().strftime('%H%M%S')}.txt"
    
    # Crear la carpeta evidencias si no existe
    if not os.path.exists("evidencias"):
        os.makedirs("evidencias")
        
    with open(nombre_archivo, "w") as f:
        f.write(f"=========================================\n")
        f.write(f" REPORTE DE AUDITORÍA - NETLAB MONITOR\n")
        f.write(f" Fecha: {fecha}\n")
        f.write(f"=========================================\n\n")
        
        for i, (nombre, estado) in enumerate(resultados.items(), 1):
            texto_estado = "OK" if estado else "FAIL"
            f.write(f"[{i}] {nombre}: {texto_estado}\n")
            
        if all(resultados.values()):
            f.write("\n=> RED COMPLETAMENTE OPERATIVA (Todo en verde).\n")
        else:
            f.write("\n=> SE ENCONTRARON FALLAS. Revise las capas superiores (Rutas/Servicios).\n")
            
    print(f"{OK} Reporte guardado exitosamente en: {nombre_archivo}")

# --- FUNCION PRINCIPAL ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NetLab Monitor - Auditor de Red")
    parser.add_argument("-c", "--config", default="monitor.json", help="Ruta al archivo JSON")
    args = parser.parse_args()

    print("=========================================")
    print(f" INICIANDO NETLAB MONITOR - {datetime.datetime.now()}")
    print("=========================================")
    
    config = cargar_configuracion(args.config)
    
    # Ejecutamos cada prueba y guardamos su resultado (True/False)
    resultados = {
        "Inventario (Capa Enlace)": verificar_inventario(config),
        "Interfaces y VLANs (Capa VLAN)": verificar_interfaces(config),
        "Rutas (Capa Red)": verificar_rutas(config),
        "Conectividad (Capa Red/Transporte)": verificar_conectividad(config),
        "Servicios (Capa Aplicación)": verificar_servicios(config),
        "OSPF (Capa Enrutamiento)": verificar_ospf(config),
        "NAT (Capa Seguridad/Traducción)": verificar_nat(config)
    }
    
    generar_reporte(resultados)

    # Código de salida (0 si todo ok, 1 si algo falló - Requisito del PDF)
    if all(resultados.values()):
        exit(0)
    else:
        exit(1)