import concurrent
import datetime
import json
import logging
import os
import socket
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from typing import Optional, Dict, List

import netifaces
import psutil
import requests
import scapy
import shodan
import whois
from attr import asdict
from dotenv import load_dotenv

from dataclasses import AttackerInfo, GeoLocation, Cache


class ARPMonitor:
    def __init__(self):
        # Cargar variables de entorno
        load_dotenv()

        # Configuración de logging
        logging.basicConfig(
            filename='arp_monitor.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        # Configurar Shodan
        self.shodan_api_key = os.getenv('SHODAN_API_KEY')
        if not self.shodan_api_key:
            logging.warning("No se encontró SHODAN_API_KEY. La funcionalidad de Shodan estará deshabilitada.")
            self.shodan_api = None
        else:
            try:
                self.shodan_api = shodan.Shodan(self.shodan_api_key)
                logging.info("API de Shodan iniciada correctamente")
            except Exception as e:
                logging.error(f"Error al inicializar Shodan: {e}")
                self.shodan_api = None

        self.setup_network_info()
        self.known_macs = self.load_known_devices()
        self.blocked_ips = set()
        self.cache = Cache()
        self.scan_queue = Queue()
        self.worker_threads = []
        self.start_worker_threads()

    def setup_network_info(self):
        """Configura información de red inicial"""
        try:
            gateways = netifaces.gateways()
            self.router_ip = gateways['default'][netifaces.AF_INET][0]
            self.interface = gateways['default'][netifaces.AF_INET][1]
            self.network_prefix = '.'.join(self.router_ip.split('.')[:-1])
            self.router_mac = self.get_router_mac()
            logging.info(f"Red configurada: {self.router_ip} ({self.router_mac})")
        except Exception as e:
            logging.error(f"Error configurando red: {e}")
            raise

    def load_known_devices(self):
        """Carga dispositivos conocidos desde archivo"""
        try:
            with open('known_devices.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def get_router_mac(self):
        """Obtiene MAC del router"""
        try:
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if f"({self.router_ip})" in line:
                    return line.split()[3]
        except Exception as e:
            logging.error(f"Error obteniendo MAC del router: {e}")
        return None

    def get_mac(self, ip):
        """Obtiene MAC de una IP"""
        try:
            # Crear paquete ARP
            arp_request = scapy.all.ARP()
            arp_request.pdst = ip

            # Crear frame Ethernet broadcast
            broadcast = scapy.all.Ether()
            broadcast.dst = "ff:ff:ff:ff:ff:ff"

            # Combinar los paquetes
            arp_request_broadcast = broadcast / arp_request

            # Enviar paquete y obtener respuesta
            answered_list = scapy.all.srp(arp_request_broadcast, timeout=2, verbose=False)[0]

            # Extraer MAC de la respuesta si existe
            if answered_list:
                return answered_list[0][1].hwsrc
            return None

        except Exception as e:
            logging.error(f"Error obteniendo MAC para {ip}: {e}")
            return None

    def start_worker_threads(self, num_threads=4):
        """Inicia threads trabajadores"""
        for _ in range(num_threads):
            thread = threading.Thread(target=self.worker_process, daemon=True)
            thread.start()
            self.worker_threads.append(thread)

    def worker_process(self):
        """Proceso trabajador para tareas en cola"""
        while True:
            task = self.scan_queue.get()
            if task is None:
                break

            ip, mac = task
            try:
                attacker_info = self.get_attacker_info(ip, mac)
                self.process_attacker_info(attacker_info)
            except Exception as e:
                logging.error(f"Error procesando IP {ip}: {e}")
            finally:
                self.scan_queue.task_done()

    def check_port(self, ip: str, port: int) -> bool:
        """Comprueba si un puerto está abierto"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            result = sock.connect_ex((ip, port)) == 0
            return result
        finally:
            sock.close()

    def scan_ports(self, ip: str, ports: List[int]) -> List[int]:
        """Escaneo de puertos multihilo"""
        open_ports = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_port = {
                executor.submit(self.check_port, ip, port): port
                for port in ports
            }
            for future in concurrent.futures.as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    if future.result():
                        open_ports.append(port)
                except Exception:
                    continue
        return open_ports

    def get_geolocation(self, ip: str) -> Optional[GeoLocation]:
        """Obtiene geolocalización con múltiples servicios"""
        cached_data = self.cache.get(ip)
        if cached_data and 'geolocation' in cached_data:
            return GeoLocation(**cached_data['geolocation'])

        services = [
            ('https://ipapi.co/{}/json/', lambda r: {
                'country': r.get('country_name'),
                'region': r.get('region'),
                'city': r.get('city'),
                'lat': r.get('latitude'),
                'lon': r.get('longitude')
            }),
            ('https://ipinfo.io/{}/json', lambda r: {
                'country': r.get('country'),
                'region': r.get('region'),
                'city': r.get('city'),
                'lat': float(r.get('loc', ',').split(',')[0]),
                'lon': float(r.get('loc', ',').split(',')[1])
            }),
            ('https://extreme-ip-lookup.com/json/{}', lambda r: {
                'country': r.get('country'),
                'region': r.get('region'),
                'city': r.get('city'),
                'lat': float(r.get('lat')),
                'lon': float(r.get('lon'))
            })
        ]

        for url_template, parser in services:
            try:
                response = requests.get(url_template.format(ip))
                if response.status_code == 200:
                    data = parser(response.json())
                    geo = GeoLocation(**data)
                    self.cache.set(ip, {'geolocation': asdict(geo)})
                    return geo
            except Exception as e:
                logging.error(f"Error con servicio de geolocalización: {e}")
                continue
        return None

    def check_tor_exit_node(self, ip: str) -> bool:
        """Verifica si la IP es un nodo de salida Tor"""
        try:
            response = requests.get("https://check.torproject.org/exit-addresses")
            return ip in response.text
        except Exception as e:
            logging.error(f"Error verificando nodo Tor: {e}")
            return False

    def detect_vpn(self, ip: str) -> bool:
        """Detecta si la IP podría ser de una VPN"""
        try:
            response = requests.get(f"https://ipapi.co/{ip}/json/")
            if response.status_code == 200:
                data = response.json()
                return any(vpn_keyword in data.get('org', '').lower()
                           for vpn_keyword in ['vpn', 'proxy', 'hosting'])
        except Exception as e:
            logging.error(f"Error detectando VPN: {e}")
        return False

    def get_network_stats(self, ip: str) -> Dict:
        """Obtiene estadísticas de red"""
        try:
            connections = psutil.net_connections()
            return {
                "active_connections": len([c for c in connections if c.raddr and c.raddr[0] == ip]),
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv
            }
        except Exception as e:
            logging.error(f"Error obteniendo estadísticas de red: {e}")
            return {}

    def get_shodan_info(self, ip: str) -> Dict:
        """Obtiene información de Shodan"""
        if not self.shodan_api:
            return {}

        try:
            return self.shodan_api.host(ip)
        except Exception as e:
            logging.error(f"Error con Shodan: {e}")
            return {}

    def get_attacker_info(self, ip: str, mac: str) -> AttackerInfo:
        """Recopila información detallada del atacante"""
        cached_data = self.cache.get(ip)
        if cached_data:
            return AttackerInfo(**cached_data)

        with ThreadPoolExecutor(max_workers=4) as executor:
            geo_future = executor.submit(self.get_geolocation, ip)
            ports_future = executor.submit(self.scan_ports, ip, range(1, 1025))
            shodan_future = executor.submit(self.get_shodan_info, ip)
            whois_future = executor.submit(whois.whois, ip)

        info = AttackerInfo(
            timestamp=datetime.now().isoformat(),
            ip=ip,
            mac=mac,
            hostname=socket.getfqdn(ip),
            open_ports=ports_future.result(),
            geolocation=geo_future.result(),
            isp=None,
            tor_exit_node=self.check_tor_exit_node(ip),
            vpn_detected=self.detect_vpn(ip),
            whois=whois_future.result(),
            network_stats=self.get_network_stats(ip),
            shodan_info=shodan_future.result()
        )

        self.cache.set(ip, asdict(info))
        return info

    def block_attacker(self, ip: str):
        """Bloquea IP atacante"""
        if ip in self.blocked_ips:
            return

        try:
            commands = [
                f"sudo iptables -A INPUT -s {ip} -j DROP",
                f"sudo iptables -A OUTPUT -d {ip} -j DROP",
                f"sudo iptables -A FORWARD -s {ip} -j DROP",
                f"sudo iptables -A FORWARD -d {ip} -j DROP"
            ]
            for cmd in commands:
                subprocess.run(cmd.split(), check=True)

            self.blocked_ips.add(ip)
            logging.info(f"IP bloqueada: {ip}")
        except Exception as e:
            logging.error(f"Error bloqueando IP {ip}: {e}")

    def restore_arp(self):
        """Restaura tabla ARP"""
        try:
            for _ in range(5):
                scapy.send(
                    scapy.ARP(
                        op=2,
                        pdst=self.router_ip,
                        hwdst="ff:ff:ff:ff:ff:ff",
                        psrc=self.router_ip,
                        hwsrc=self.router_mac
                    ),
                    verbose=False
                )
                time.sleep(1)
            logging.info("Tabla ARP restaurada")
        except Exception as e:
            logging.error(f"Error restaurando ARP: {e}")

    def process_attacker_info(self, info: AttackerInfo):
        """Procesa la información del atacante"""
        print(f"\n[!] Atacante identificado: {info.ip}")
        print(f"[*] MAC: {info.mac}")
        print(f"[*] Hostname: {info.hostname}")

        if info.geolocation:
            print(f"[*] Ubicación: {info.geolocation.city}, {info.geolocation.country}")

        print(f"[*] Puertos abiertos: {', '.join(map(str, info.open_ports))}")
        print(f"[*] Nodo Tor: {'Sí' if info.tor_exit_node else 'No'}")
        print(f"[*] VPN detectada: {'Sí' if info.vpn_detected else 'No'}")

        with open("attackers_detailed.json", "a") as f:
            json.dump(asdict(info), f, indent=2)
            f.write("\n")

        # Bloquear al atacante
        self.block_attacker(info.ip)

        # Restaurar tabla ARP
        self.restore_arp()

        def monitor(self):
            """Monitoreo principal con procesamiento asíncrono"""
            print(f"[*] Iniciando monitoreo en {self.interface}")
            print(f"[*] Router: {self.router_ip} (MAC: {self.router_mac})")
            print("[*] Presiona Ctrl+C para detener el monitoreo")

            try:
                while True:
                    current_mac = self.get_mac(self.router_ip)

                    if current_mac and current_mac != self.router_mac:
                        print(f"\n[ALERTA] ¡Posible ataque ARP Spoofing detectado!")
                        print(f"[*] MAC original del router: {self.router_mac}")
                        print(f"[*] MAC actual detectada: {current_mac}")

                        # Búsqueda del atacante en paralelo
                        with ThreadPoolExecutor() as executor:
                            future_to_ip = {
                                executor.submit(self.get_mac, f"{self.network_prefix}.{i}"): i
                                for i in range(1, 255)
                            }

                            for future in concurrent.futures.as_completed(future_to_ip):
                                ip_suffix = future_to_ip[future]
                                try:
                                    mac = future.result()
                                    if mac == current_mac:
                                        attacker_ip = f"{self.network_prefix}.{ip_suffix}"
                                        print(f"[+] Atacante localizado: {attacker_ip}")
                                        self.scan_queue.put((attacker_ip, current_mac))
                                        break
                                except Exception as e:
                                    logging.error(f"Error procesando IP .{ip_suffix}: {e}")

                    time.sleep(2)  # Intervalo de escaneo

            except KeyboardInterrupt:
                print("\n[*] Deteniendo monitoreo...")
                self.cleanup()
            except Exception as e:
                logging.error(f"Error en ciclo principal de monitoreo: {e}")
                self.cleanup()
                raise

        def cleanup(self):
            """Limpia recursos y termina threads"""
            print("[*] Realizando limpieza...")

            # Terminar threads trabajadores
            for _ in self.worker_threads:
                self.scan_queue.put(None)

            for thread in self.worker_threads:
                thread.join()

            # Restaurar tabla ARP una última vez
            self.restore_arp()

            # Cerrar conexiones de red pendientes
            try:
                for conn in psutil.net_connections():
                    if conn.status == 'ESTABLISHED':
                        try:
                            socket.fromfd(conn.fd, socket.AF_INET, socket.SOCK_STREAM).close()
                        except:
                            pass
            except:
                pass

            logging.info("Limpieza completada")
            print("[*] Monitoreo finalizado")