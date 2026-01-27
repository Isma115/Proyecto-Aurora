
import socket
import psutil

def get_ip_addresses():
    print("\n=== Direcciones IP Disponibles ===")
    print("Prueba conectar con CUALQUIERA de estas IPs:")
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == socket.AF_INET:
                print(f" - {interface}: {snic.address}")

def check_port(port):
    print(f"\n=== Estado del Puerto {port} ===")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    if result == 0:
        print(f"✅ El puerto {port} está ABIERTO y escuchando (OK)")
    else:
        print(f"❌ El puerto {port} está CERRADO. ¿Se está ejecutando chatbot.py?")
    sock.close()

if __name__ == "__main__":
    try:
        print("Diagnóstico de Red para Proyecto Aurora")
        get_ip_addresses()
        check_port(5000)
        print("\n=== Consejos ===")
        print("1. Si ves varias IPs, prueba con la que empiece por 192.168.x.x")
        print("2. IMPORTANTE: Desactiva el Firewall de Windows temporalmente para probar.")
    except Exception as e:
        print(f"Error: {e}")
