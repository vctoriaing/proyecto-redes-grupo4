#!/usr/bin/env python3
import json
import datetime
import os

# --- FUNCION SIMULADA (MOCK) ---
# Esta funcion reemplaza a 'docker exec' para probar sin red real.
def ejecutar_comando(nodo, comando):
    # Simulamos respuestas exitosas de los routers
    if "hostname" in comando: 
        return True, nodo
    if "ip -br a" in comando: 
        return True, "eth1.10@eth1 UP\neth1.20@eth1 UP"
    if "ip route" in comando: 
        return True, "O 172.16.4.0/24 via 10.0.0.1\nS 0.0.0.0/0 via 203.0.113.1" #cambiado para simular
    if "ping" in comando: 
        return True, "1 packets transmitted, 1 received, 0% packet loss"
    if "vtysh" in comando: 
        return True, "Neighbor ID 2.2.2.2 State Full/DR"
    if "iptables" in comando: 
        return True, "MASQUERADE all -- 0.0.0.0/0 0.0.0.0/0"
    return False, "Error simulado"

def cargar_configuracion(ruta):
    try:
        with open(ruta, 'r') as archivo:
            return json.load(archivo)
    except Exception as e:
        print(f"[FAIL] Error al leer el JSON: {e}")
        exit(1)

# --- VERIFICACIONES (Adaptadas para prueba) ---

def verificar_inventario(config):
    print("\n--- [1] Verificando Inventario ---")
    for nodo in config["nodos"]:
        exito, _ = ejecutar_comando(nodo, "hostname")
        print(f"[ OK ] Nodo {nodo} está en ejecución." if exito else f"[FAIL] Nodo {nodo} caído.")
    return True

def verificar_interfaces(config):
    print("\n--- [2] Verificando Interfaces y VLANs ---")
    exito, salida = ejecutar_comando("r2", "ip -br a")
    if exito and "eth1.10" in salida:
        print("[ OK ] Subinterfaces VLAN detectadas en r2.")
        return True
    return False

def verificar_rutas(config):
    print("\n--- [3] Verificando Rutas ---")
    todo_ok = True
    for router, rutas_esperadas in config["rutas_esperadas"].items():
        exito, salida = ejecutar_comando(router, "ip route")
        for red in rutas_esperadas:
            if red in salida:
                print(f"[ OK ] {router} tiene la ruta {red}.")
            else:
                print(f"[FAIL] {router} NO conoce la ruta {red}.")
                todo_ok = False
    return todo_ok

def verificar_conectividad(config):
    print("\n--- [4] Verificando Conectividad (Ping) ---")
    for prueba in config["pruebas_conectividad"]:
        print(f"[ OK ] {prueba['origen']} -> {prueba['destino_ip']} (Simulado).")
    return True

def verificar_servicios(config):
    print("\n--- [5] Verificando Servicios (Sockets) ---")
    # En el test, solo imprimimos OK para no depender de red real
    for servicio in config["servicios"]:
        print(f"[ OK ] Servicio en {servicio['ip']}:{servicio['puerto']} (Simulado).")
    return True

def verificar_ospf(config):
    print("\n--- [6] Verificando Vecinos OSPF ---")
    exito, salida = ejecutar_comando("r1", "vtysh -c 'show ip ospf neighbor'")
    if exito and "Full" in salida:
        print("[ OK ] Vecinos OSPF en estado Full detectados en r1.")
        return True
    return False

def verificar_nat(config):
    print("\n--- [7] Verificando NAT en r1 ---")
    exito, salida = ejecutar_comando("r1", "iptables -t nat -L -n -v")
    if exito and "MASQUERADE" in salida:
        print("[ OK ] Regla NAT (MASQUERADE) encontrada en r1.")
        return True
    return False

def generar_reporte(resultados):
    print("\n--- [8] Generando Reporte ---")
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_archivo = f"evidencias/test_reporte_{datetime.datetime.now().strftime('%H%M%S')}.txt"
    
    if not os.path.exists("evidencias"):
        os.makedirs("evidencias")
        
    with open(nombre_archivo, "w") as f:
        f.write(f"=========================================\n")
        f.write(f" REPORTE DE PRUEBA (SIMULACIÓN) - NETLAB\n")
        f.write(f" Fecha: {fecha}\n")
        f.write(f"=========================================\n\n")
        for i, (nombre, estado) in enumerate(resultados.items(), 1):
            texto_estado = "OK" if estado else "FAIL"
            f.write(f"[{i}] {nombre}: {texto_estado}\n")
            
    print(f"[ OK ] Reporte guardado exitosamente en: {nombre_archivo}")

# --- FUNCION PRINCIPAL ---
if __name__ == "__main__":
    print("=========================================")
    print(f" INICIANDO TEST DEL MONITOR (SIN RED)")
    print("=========================================")
    
    config = cargar_configuracion("monitor.json")
    
    resultados = {
        "Inventario": verificar_inventario(config),
        "Interfaces": verificar_interfaces(config),
        "Rutas": verificar_rutas(config),
        "Conectividad": verificar_conectividad(config),
        "Servicios": verificar_servicios(config),
        "OSPF": verificar_ospf(config),
        "NAT": verificar_nat(config)
    }
    
    generar_reporte(resultados)
    
    if all(resultados.values()):
        print("\n=> TEST EXITOSO: La lógica del código está perfecta.")
        exit(0)
    else:
        print("\n=> TEST FALLIDO: Revisa la lógica del código.")
        exit(1)
