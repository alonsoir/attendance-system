import os
import time
import scapy.all as scapy
import subprocess

def get_router_mac():
    result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if "(192.168.1.1)" in line:  # Ajustar según tu gateway
            return line.split()[3]
    return None

def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]
    if answered_list:
        return answered_list[0][1].hwsrc
    return None

def log_attacker_info(attacker_ip, current_mac):
    with open("attackers.log", "a") as log_file:
        log_file.write(f"Atacante detectado: IP={attacker_ip}, MAC={current_mac}, Timestamp={time.ctime()}\n")

def block_attacker(ip):
    print(f"[!] Bloqueando atacante: {ip}")
    os.system(f"sudo iptables -A INPUT -s {ip} -j DROP")
    os.system(f"sudo iptables -A FORWARD -s {ip} -j DROP")

def restore_arp(router_ip, router_mac):
    print("[+] Restaurando ARP del router...")
    for _ in range(5):
        scapy.send(scapy.ARP(op=2, pdst=router_ip, hwdst="ff:ff:ff:ff:ff:ff", psrc=router_ip, hwsrc=router_mac), verbose=False)
        time.sleep(1)

def monitor_arp():
    router_ip = "192.168.1.1"  # Ajusta según tu red
    original_mac = get_router_mac()
    if not original_mac:
        print("[!] No se pudo obtener la MAC del router. Abortando...")
        return
    print(f"[*] MAC original del router: {original_mac}")
    while True:
        current_mac = get_mac(router_ip)
        if current_mac and current_mac != original_mac:
            print(f"[ALERTA] Posible ARP Spoofing detectado! MAC del router cambió: {current_mac}")
            attacker_ip = None
            for ip in [f"192.168.1.{i}" for i in range(2, 255)]:
                if get_mac(ip) == current_mac:
                    attacker_ip = ip
                    break
            if attacker_ip:
                print(f"[!] Atacante identificado: {attacker_ip}")
                log_attacker_info(attacker_ip, current_mac)
                block_attacker(attacker_ip)
            restore_arp(router_ip, original_mac)
        time.sleep(5)

if __name__ == "__main__":
    monitor_arp()
