#!/usr/bin/env python3
import subprocess
import platform
import socket
import threading
import queue
import os
import time
import json
import re
import logging
from datetime import datetime

# Intentar importar scapy con un manejo de errores mejorado
try:
    os.environ['SCAPY_NOLOAD'] = 'netflow'
    from scapy.all import sniff, DNS, DNSQR, DNSRR
except ImportError as e:
    print(f"Error al importar Scapy: {e}")
    print("Asegúrate de tener instalada la versión correcta de Scapy (pip install scapy)")
    print("Si el problema persiste, intenta con una versión más antigua o más nueva de Scapy.")
    exit(1)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dns_protection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('dns_protection')

# Constantes
DNS_CACHE_FILE = '/tmp/dns_cache.json' if platform.system() != 'Windows' else os.path.join(os.environ['TEMP'],
                                                                                           'dns_cache.json')
CRITICAL_DOMAINS = [
    'google.com', 'facebook.com', 'amazon.com', 'microsoft.com',
    'apple.com', 'paypal.com', 'netflix.com', 'gmail.com',
    'outlook.com', 'yahoo.com', 'bank', 'gov', 'login'
]


class DNSCache:
    def __init__(self):
        self.cache = {}
        self.load_cache()

    def load_cache(self):
        if os.path.exists(DNS_CACHE_FILE):
            try:
                with open(DNS_CACHE_FILE, 'r') as f:
                    self.cache = json.load(f)
                logger.info(f"Caché DNS cargada desde {DNS_CACHE_FILE}")
            except:
                logger.warning("No se pudo cargar el caché DNS. Iniciando vacío.")
        else:
            logger.info("Creando un nuevo caché DNS")

    def save_cache(self):
        try:
            with open(DNS_CACHE_FILE, 'w') as f:
                json.dump(self.cache, f, indent=2)
            logger.debug("Caché DNS guardada")
        except Exception as e:
            logger.error(f"Error al guardar caché DNS: {e}")

    def get(self, domain):
        if domain in self.cache:
            entry = self.cache[domain]
            if time.time() < entry['expiry']:
                return entry['ip']
        return None

    def put(self, domain, ip, ttl=3600):
        self.cache[domain] = {
            'ip': ip,
            'first_seen': time.time(),
            'expiry': time.time() + ttl,
            'verified': False
        }
        self.save_cache()

    def mark_verified(self, domain):
        if domain in self.cache:
            self.cache[domain]['verified'] = True
            self.save_cache()


# Inicialización de variables globales
dns_queue = queue.Queue()
dns_cache = DNSCache()
alert_count = 0


def get_trusted_dns_response(domain, dns_server='1.1.1.1'):
    """Obtiene respuesta DNS de un servidor de confianza con DNSSEC habilitado"""
    try:
        cmd = f"dig @{dns_server} +dnssec +short {domain} A"
        result = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        if result:
            # Filtrar solo direcciones IP válidas
            ips = [line for line in result.split('\n') if is_valid_ip(line)]
            if ips:
                return ips[0]
    except Exception as e:
        logger.error(f"Error al consultar DNS confiable: {e}")
    return None


def is_valid_ip(text):
    """Verifica si el texto es una dirección IPv4 válida"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(pattern, text):
        return all(0 <= int(part) <= 255 for part in text.split('.'))
    return False


def is_critical_domain(domain):
    """Verifica si un dominio es considerado crítico para seguridad"""
    domain = domain.lower()
    return any(critical in domain for critical in CRITICAL_DOMAINS)


def verificador_dns():
    """Hilo que verifica las consultas DNS contra servidores confiables"""
    while True:
        try:
            dominio, respuesta_recibida = dns_queue.get(timeout=1)

            # Primero revisar nuestro caché local
            cached_ip = dns_cache.get(dominio)
            if cached_ip and cached_ip != respuesta_recibida:
                if is_critical_domain(dominio):
                    handle_critical_spoofing(dominio, respuesta_recibida, cached_ip)
                else:
                    logger.warning(
                        f"Posible DNS spoofing: {dominio} -> Recibido: {respuesta_recibida}, Caché: {cached_ip}")

            # Si no está en caché o queremos verificar de todos modos
            if cached_ip is None or not dns_cache.cache[dominio].get('verified'):
                trusted_ip = get_trusted_dns_response(dominio)
                if trusted_ip and trusted_ip != respuesta_recibida:
                    if is_critical_domain(dominio):
                        handle_critical_spoofing(dominio, respuesta_recibida, trusted_ip)
                    else:
                        logger.warning(
                            f"Verificación DNS fallida: {dominio} -> Recibido: {respuesta_recibida}, Esperado: {trusted_ip}")

                # Actualizar caché con la respuesta confiable
                if trusted_ip:
                    dns_cache.put(dominio, trusted_ip)
                    dns_cache.mark_verified(dominio)

        except queue.Empty:
            time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error en verificador DNS: {e}")


def handle_critical_spoofing(domain, received_ip, expected_ip):
    """Maneja intentos de spoofing en dominios críticos"""
    global alert_count
    alert_count += 1

    logger.critical(f"¡ALERTA DE SEGURIDAD! Posible ataque de DNS spoofing detectado!")
    logger.critical(f"Dominio crítico: {domain}")
    logger.critical(f"IP recibida: {received_ip}")
    logger.critical(f"IP esperada: {expected_ip}")

    # Acciones de mitigación
    update_hosts_file(domain, expected_ip)

    if alert_count >= 3:
        logger.critical("Múltiples intentos de spoofing detectados. Habilitando modo de protección activa.")
        enable_active_protection()


def update_hosts_file(domain, ip):
    """Actualiza el archivo hosts para proteger dominios críticos"""
    hosts_file = 'C:\\Windows\\System32\\drivers\\etc\\hosts' if platform.system() == 'Windows' else '/etc/hosts'

    try:
        # Leer el archivo hosts actual
        with open(hosts_file, 'r') as f:
            content = f.readlines()

        # Buscar si el dominio ya está en el archivo
        domain_exists = False
        new_content = []
        for line in content:
            if line.strip() and not line.startswith('#'):
                parts = line.split()
                if len(parts) >= 2 and domain in parts[1:]:
                    # Actualizar la entrada existente
                    new_content.append(f"{ip} {domain}\n")
                    domain_exists = True
                else:
                    new_content.append(line)
            else:
                new_content.append(line)

        # Agregar el dominio si no existe
        if not domain_exists:
            new_content.append(f"{ip} {domain}\n")

        # Escribir el archivo actualizado
        with open(hosts_file, 'w') as f:
            f.writelines(new_content)

        logger.info(f"Archivo hosts actualizado para proteger {domain} -> {ip}")
    except Exception as e:
        logger.error(f"No se pudo actualizar el archivo hosts: {e}")


def enable_active_protection():
    """Habilita medidas de protección activa ante ataques persistentes"""
    logger.info("Activando medidas de protección avanzadas")

    # 1. Intentar configurar DNS seguros
    configure_secure_dns()

    # 2. Verificar si se puede activar DoH o DoT
    enable_encrypted_dns()

    # 3. Alertar al usuario sobre el posible ataque
    notify_user_attack()


def configure_secure_dns():
    """Configura servidores DNS seguros"""
    dns_servers = ["1.1.1.1", "9.9.9.9", "8.8.8.8"]

    if platform.system() == "Linux":
        try:
            with open('/etc/resolv.conf', 'w') as f:
                for dns in dns_servers:
                    f.write(f"nameserver {dns}\n")
            logger.info("Servidores DNS seguros configurados")
        except:
            logger.error("No se pudieron configurar los servidores DNS")
    elif platform.system() == "Windows":
        try:
            adapters = subprocess.check_output("netsh interface show interface", shell=True).decode('utf-8')
            for line in adapters.split('\n'):
                if 'Connected' in line:
                    adapter = line.split()[-1]
                    subprocess.run(f'netsh interface ip set dns "{adapter}" static {dns_servers[0]} primary',
                                   shell=True)
                    subprocess.run(f'netsh interface ip add dns "{adapter}" {dns_servers[1]} index=2', shell=True)
                    logger.info(f"DNS seguros configurados en {adapter}")
        except:
            logger.error("No se pudieron configurar los DNS en Windows")
    elif platform.system() == "Darwin":  # macOS
        try:
            service = \
            subprocess.check_output('networksetup -listallnetworkservices | grep -v "An asterisk"', shell=True).decode(
                'utf-8').split('\n')[0]
            if service:
                subprocess.run(f'networksetup -setdnsservers "{service}" {" ".join(dns_servers)}', shell=True)
                logger.info(f"DNS seguros configurados en macOS")
        except Exception as e:
            logger.error(f"No se pudieron configurar los DNS en macOS: {e}")


def enable_encrypted_dns():
    """Intenta habilitar DNS cifrado (DoH o DoT) si es posible"""
    logger.info("============= RECOMENDACIONES DE SEGURIDAD =============")
    logger.info("Se recomienda configurar DNS sobre HTTPS (DoH) o DNS sobre TLS (DoT):")
    logger.info("- Firefox: Configuración > Red > Habilitar DNS sobre HTTPS")
    logger.info("- Chrome: chrome://flags/#dns-over-https")
    logger.info("- Edge: edge://flags/#dns-over-https")
    logger.info("- Configurar Pi-hole o AdGuard Home con DoH/DoT en la red local")
    logger.info("=========================================================")


def notify_user_attack():
    """Notifica al usuario sobre el posible ataque en curso"""
    mensaje = """
    ¡ALERTA DE SEGURIDAD!

    Se han detectado múltiples intentos de falsificación de DNS en su red.
    Esto podría indicar que alguien está intentando redirigir su tráfico web.

    Recomendaciones inmediatas:
    1. No realice operaciones sensibles (bancarias, compras) hasta resolver el problema
    2. Considere reiniciar su router
    3. Verifique dispositivos conectados a su red
    4. Use una conexión VPN de confianza si necesita realizar operaciones críticas

    Este sistema ha implementado algunas medidas de protección básicas,
    pero se recomienda una revisión profesional de su red.
    """

    logger.critical(mensaje)

    # En sistemas con interfaz gráfica, intentamos mostrar una notificación
    if platform.system() == "Windows":
        try:
            subprocess.Popen(['msg', '*', mensaje])
        except:
            pass
    elif platform.system() == "Linux":
        try:
            subprocess.Popen(['notify-send', '¡ALERTA DE SEGURIDAD!', mensaje])
        except:
            pass
    elif platform.system() == "Darwin":  # macOS
        try:
            mensaje_mac = mensaje.replace('"', '\\"')
            os.system(f'osascript -e \'display notification "{mensaje_mac}" with title "¡ALERTA DE SEGURIDAD!"\' ')
        except Exception as e:
            logger.error(f"Error al mostrar notificación en macOS: {e}")


def sniffer_callback(pkt):
    """Analiza paquetes DNS capturados"""
    if DNS in pkt and pkt[DNS].qr == 1 and pkt[DNS].ancount > 0:
        try:
            dominio = pkt[DNSQR].qname.decode('utf-8').rstrip('.')
            for i in range(pkt[DNS].ancount):
                if pkt[DNSRR][i].type == 1:  # Tipo A (dirección IPv4)
                    ip_recibida = pkt[DNSRR][i].rdata

                    # Encolamos para verificación
                    dns_queue.put((dominio, ip_recibida))

                    # Cache inmediato si no existe
                    if dns_cache.get(dominio) is None:
                        dns_cache.put(dominio, ip_recibida, ttl=pkt[DNSRR][i].ttl)
        except Exception as e:
            logger.error(f"Error al procesar paquete DNS: {e}")


def check_prerequisites():
    """Verifica si las dependencias necesarias están instaladas"""
    # Comprobar si dig está disponible
    try:
        subprocess.check_output("which dig", shell=True)
    except:
        logger.warning("La herramienta 'dig' no está instalada. Se recomienda instalarla para mejor funcionamiento.")
        if platform.system() == "Darwin":
            logger.info("Puedes instalarla en macOS con: brew install bind")
        elif platform.system() == "Linux":
            logger.info(
                "Puedes instalarla en Linux con: sudo apt-get install dnsutils (Debian/Ubuntu) o sudo yum install bind-utils (CentOS/RHEL)")

    # Comprobar si se tienen permisos para sniffing
    if platform.system() != "Windows":
        if os.geteuid() != 0:
            logger.error("Este script requiere privilegios de administrador para capturar tráfico DNS")
            return False
    return True


def main():
    # Banner
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║  SISTEMA DE PROTECCIÓN CONTRA DNS SPOOFING           ║
    ║  Desarrollado con fines educativos y de seguridad    ║
    ╚══════════════════════════════════════════════════════╝
    """)

    # Verificar requisitos previos
    if not check_prerequisites():
        return

    # Iniciar hilo verificador
    verificador = threading.Thread(target=verificador_dns)
    verificador.daemon = True
    verificador.start()

    logger.info("Sistema de protección DNS iniciado")
    logger.info("Monitoreando tráfico DNS...")

    try:
        # En macOS, es posible que necesitemos especificar la interfaz
        if platform.system() == "Darwin":
            # Intentar obtener la interfaz principal
            try:
                default_if = subprocess.check_output("route -n get default | grep interface | awk '{print $2}'",
                                                     shell=True).decode('utf-8').strip()
                logger.info(f"Usando interfaz: {default_if}")
                sniff(iface=default_if, filter="udp port 53", prn=sniffer_callback)
            except Exception as e:
                logger.warning(f"No se pudo determinar la interfaz automáticamente: {e}")
                logger.info("Intentando sniffing sin especificar interfaz...")
                sniff(filter="udp port 53", prn=sniffer_callback)
        else:
            sniff(filter="udp port 53", prn=sniffer_callback)
    except KeyboardInterrupt:
        logger.info("Deteniendo sistema de protección DNS")
    except Exception as e:
        logger.error(f"Error durante el sniffing: {e}")
        logger.info(
            "Sugerencia: Si estás en macOS y tienes problemas, verifica que el script tenga permisos de acceso completo al disco")
    finally:
        # Guardar cache antes de salir
        dns_cache.save_cache()
        logger.info("Caché DNS guardada. Finalizando.")


if __name__ == "__main__":
    if platform.system() == 'Windows' or os.geteuid() == 0:
        main()
    else:
        print(f"[!] Este script requiere privilegios de administrador")
        print(f"[!] Ejecuta: sudo python3 {os.path.basename(__file__)}")
        exit(1)