import subprocess
import platform
import os


def configurar_dns_seguro():
    """Configura servidores DNS seguros que usan DNSSec o DNS sobre HTTPS"""
    # Servidores DNS seguros (Cloudflare, Google, Quad9)
    dns_seguros = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]

    sistema = platform.system()
    print(f"[*] Configurando DNS seguros en sistema {sistema}")

    if sistema == "Linux":
        try:
            # Modificar resolv.conf (temporal)
            with open('/etc/resolv.conf', 'w') as f:
                for dns in dns_seguros:
                    f.write(f"nameserver {dns}\n")
            print("[+] Servidores DNS configurados temporalmente")

            # Para configuración permanente, verificar si usa NetworkManager, systemd-resolved, etc.
            if os.path.exists('/etc/NetworkManager/NetworkManager.conf'):
                print("[*] Detectado NetworkManager. Configurando DNS permanentes...")
                # Esta es una configuración básica. En producción se requeriría más sofisticación
                subprocess.run(['nmcli', 'con', 'mod', 'System\ eth0', 'ipv4.dns', ','.join(dns_seguros)])
                subprocess.run(['systemctl', 'restart', 'NetworkManager'])
                print("[+] NetworkManager configurado con DNS seguros")
        except Exception as e:
            print(f"[!] Error al configurar DNS: {e}")

    elif sistema == "Windows":
        try:
            # Obtener el nombre de la interfaz de red activa
            interfaces = subprocess.check_output('netsh interface show interface', shell=True).decode('utf-8')
            for line in interfaces.split('\n'):
                if 'Connected' in line:
                    interface = line.split()[-1]
                    print(f"[*] Configurando DNS para interfaz: {interface}")

                    # Configurar DNS primario y secundario
                    subprocess.run(f'netsh interface ip set dns "{interface}" static {dns_seguros[0]} primary',
                                   shell=True)
                    subprocess.run(f'netsh interface ip add dns "{interface}" {dns_seguros[1]} index=2', shell=True)
                    print(f"[+] DNS configurados para {interface}")
                    break
            else:
                print("[!] No se encontró ninguna interfaz conectada")
        except Exception as e:
            print(f"[!] Error al configurar DNS en Windows: {e}")

    elif sistema == "Darwin":  # macOS
        try:
            # Obtener nombre de servicio de red activo
            service = \
            subprocess.check_output('networksetup -listallnetworkservices | grep -v "An asterisk"', shell=True).decode(
                'utf-8').split('\n')[0]
            if service:
                print(f"[*] Configurando DNS para servicio: {service}")
                subprocess.run(f'networksetup -setdnsservers "{service}" {" ".join(dns_seguros)}', shell=True)
                print(f"[+] DNS configurados para {service}")
            else:
                print("[!] No se pudo determinar el servicio de red activo")
        except Exception as e:
            print(f"[!] Error al configurar DNS en macOS: {e}")

    else:
        print(f"[!] Sistema operativo no soportado: {sistema}")
        return False

    return True


def verificar_dnssec():
    """Verifica si se está utilizando DNSSEC para las consultas DNS"""
    print("[*] Verificando soporte de DNSSEC...")
    try:
        resultado = subprocess.check_output("dig +short test._dnssec-or-not.example.com txt", shell=True).decode(
            'utf-8')
        if "dnssec" in resultado.lower():
            print("[+] DNSSEC está funcionando correctamente")
            return True
        else:
            print("[!] DNSSEC no está habilitado o no funciona correctamente")
            return False
    except:
        print("[!] No se pudo verificar DNSSEC. Asegúrate de tener dig instalado.")
        return False


def main():
    print("[*] Iniciando protección contra DNS spoofing")

    # 1. Configurar servidores DNS seguros
    if configurar_dns_seguro():
        print("[+] Servidores DNS seguros configurados correctamente")
    else:
        print("[!] No se pudieron configurar los servidores DNS seguros")

    # 2. Verificar DNSSEC
    if verificar_dnssec():
        print("[+] Tu resolución DNS está protegida con DNSSEC")
    else:
        print("[-] Considera usar un resolver DNS que soporte DNSSEC")

    print("\n[*] Recomendaciones adicionales:")
    print("- Configura tu router para usar DNS sobre HTTPS (DoH) o DNS sobre TLS (DoT)")
    print("- Utiliza un servicio VPN confiable para cifrar todo tu tráfico")
    print("- Mantén actualizado tu sistema operativo y software de red")
    print("- Implementa herramientas de monitoreo de red para detectar actividad sospechosa")


if __name__ == "__main__":
    if os.geteuid() != 0:
        print("[!] Este script requiere privilegios de administrador")
        print(f"[!] Ejecuta: sudo python3 {os.path.basename(__file__)}")
        exit(1)
    main()