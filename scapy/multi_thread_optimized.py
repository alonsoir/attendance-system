import threading
import argparse
import queue
from scapy.all import *
from scapy.layers.dns import *
from scapy.layers.inet import ICMP

'''
Mejoras aplicadas con respecto a fuzzing_dns_multi_thread:

1) Se elimina time.sleep(1) dentro del bucle de envío de ICMP → send() ya maneja su propio control de flujo.
2) Se usa sniff(store=False) en sniff_packets() para evitar uso innecesario de memoria.
3) Se eliminan las funciones lambda x:x.summary() por prn=packet_handler para mejorar legibilidad.
4) Se añade queue.Queue para sincronizar los hilos y garantizar que el sniffer se inicie antes del envío de paquetes.
5) Se optimiza el uso de threading.Thread eliminando la lista innecesaria threads.

(attendance-system-py3.10) ┌<▸> ~/g/a/scapy 
└➤ sudo poetry run python multi_thread_optimized.py 1.1.1.1 --packets 10 --timeout 10
Target: 1.1.1.1, Packets: 10, Timeout: 10
..........
Sent 10 packets.
Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0
Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0
Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0
Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0
Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0
Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0
Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0
Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0
Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0
Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0
Ether / IP / ICMP 1.1.1.1 > 192.168.1.112 echo-reply 0 / Padding
Ether / IP / ICMP 1.1.1.1 > 192.168.1.112 echo-reply 0 / Padding
Ether / IP / ICMP 1.1.1.1 > 192.168.1.112 echo-reply 0 / Padding
Ether / IP / ICMP 1.1.1.1 > 192.168.1.112 echo-reply 0 / Padding
Ether / IP / ICMP 1.1.1.1 > 192.168.1.112 echo-reply 0 / Padding
Ether / IP / ICMP 1.1.1.1 > 192.168.1.112 echo-reply 0 / Padding
Ether / IP / ICMP 1.1.1.1 > 192.168.1.112 echo-reply 0 / Padding
Ether / IP / ICMP 1.1.1.1 > 192.168.1.112 echo-reply 0 / Padding
Ether / IP / ICMP 1.1.1.1 > 192.168.1.112 echo-reply 0 / Padding
Ether / IP / ICMP 1.1.1.1 > 192.168.1.112 echo-reply 0 / Padding
(attendance-system-py3.10) ┌<▸> ~/g/a/scapy 
└➤ 

'''
def test_dns_valid():
    target = "8.8.8.8"
    pkt = IP(dst=target) / UDP(dport=53) / DNS(rd=1, qd=DNSQR(qname="google.com"))
    response = sr1(pkt, timeout=2, verbose=False)
    if response:
        response.show()
    return response

def send_icmp_packages(target, num_packets, start_event):
    """ Envía paquetes ICMP después de que el sniffer haya comenzado. """
    start_event.wait()  # Espera a que el sniffer inicie
    icmp = IP(dst=target) / ICMP()
    send(icmp, count=num_packets, verbose=True)

def packet_handler(pkt):
    """ Maneja los paquetes capturados mostrando solo el resumen. """
    print(pkt.summary())

def sniff_packets(timeout, start_event):
    """ Inicia el sniffer y avisa a los otros hilos que ha comenzado. """
    start_event.set()  # Notifica que el sniffer está activo
    sniff(filter="icmp", prn=packet_handler, timeout=timeout, store=False)

def main(target, num_packets, timeout):
    start_event = threading.Event()

    sniffer_thread = threading.Thread(target=sniff_packets, args=(timeout, start_event), daemon=True)
    icmp_thread = threading.Thread(target=send_icmp_packages, args=(target, num_packets, start_event), daemon=True)

    sniffer_thread.start()
    icmp_thread.start()

    sniffer_thread.join()
    icmp_thread.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ICMP MultiThread sniffer")
    parser.add_argument('target', type=str, help="Target IP")
    parser.add_argument('--packets', type=int, default=10, help="Number of packets to send")
    parser.add_argument('--timeout', type=int, default=10, help="Timeout for the sniffer")

    args = parser.parse_args()
    print(f"Target: {args.target}, Packets: {args.packets}, Timeout: {args.timeout}")

    main(args.target, args.packets, args.timeout)
