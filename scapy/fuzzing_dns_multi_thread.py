import threading

from scapy.all import *
from scapy.layers.dns import *
from scapy.layers.inet import ICMP

"""
Este es un ejemplo sobre como enviar paquetes y esperar su respuesta usando hilos, de manera que un hilo es el 
sniffer que está leyendo la respuesta de los paquetes que hemos enviado en otro hilo.

(attendance-system-py3.10) ┌<▸> ~/g/a/scapy 
└➤ sudo poetry run python fuzzing_dns_multi_thread.py 1.1.1.1 10 10
Password:
usage: fuzzing_dns_multi_thread.py [-h] [--packets PACKETS] [--timeout TIMEOUT] target
fuzzing_dns_multi_thread.py: error: unrecognized arguments: 10 10
(attendance-system-py3.10) ┌<▪> ~/g/a/scapy 
└➤ sudo poetry run python fuzzing_dns_multi_thread.py 1.1.1.1 --packets 10 --timeout 10
Target: 1.1.1.1, Packets: 10, Timeout: 10
.
Sent 1 packets.
Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0
Ether / IP / ICMP 1.1.1.1 > 192.168.1.112 echo-reply 0 / Padding
.Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0

Sent 1 packets.
Ether / IP / ICMP 1.1.1.1 > 192.168.1.112 echo-reply 0 / Padding
.Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0

Sent 1 packets.
Ether / IP / ICMP 1.1.1.1 > 192.168.1.112 echo-reply 0 / Padding
.Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0

Sent 1 packets.
Ether / IP / ICMP 1.1.1.1 > 192.168.1.112 echo-reply 0 / Padding
.Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0

Sent 1 packets.
.Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0

Sent 1 packets.
Ether / IP / ICMP 1.1.1.1 > 192.168.1.112 echo-reply 0 / Padding
.Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0

Sent 1 packets.
Ether / IP / ICMP 1.1.1.1 > 192.168.1.112 echo-reply 0 / Padding
.Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0

Sent 1 packets.
Ether / IP / ICMP 1.1.1.1 > 192.168.1.112 echo-reply 0 / Padding
.Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0

Sent 1 packets.
Ether / IP / ICMP 1.1.1.1 > 192.168.1.112 echo-reply 0 / Padding
.Ether / IP / ICMP 192.168.1.112 > 1.1.1.1 echo-request 0

Sent 1 packets.
Ether / IP / ICMP 1.1.1.1 > 192.168.1.112 echo-reply 0 / Padding
(attendance-system-py3.10) ┌<▸> ~/g/a/scapy 
└➤ 


"""
def test_dns_valid():
    target = "8.8.8.8"
    pkt = IP(dst=target) / UDP(dport=53) / DNS(rd=1, qd=DNSQR(qname="google.com"))
    response = sr1(pkt, timeout=2)
    print(response.show())
    return response

def send_icmp_packages(target,num_packets):
    icmp = IP(dst=target) / ICMP()
    for _ in range(num_packets):
        send(icmp)
        time.sleep(1)

def sniff_packets(timeout):
    sniff(filter="icmp", prn = lambda x:x.summary(),timeout=timeout)

def main(target, num_packages, timeout):
    '''
    Si queremos capturar todas las respuestas, hay que asegurarse de lanzar primero el sniffer.
    :param target:
    :param num_packages:
    :param timeout:
    :return:
    '''
    sniffer_thead = threading.Thread(target=sniff_packets, args=(timeout,), daemon=True)
    icmp_thread = threading.Thread(target=send_icmp_packages,args=(target,num_packages),daemon=True)

    sniffer_thead.start()
    icmp_thread.start()

    threads=[icmp_thread,sniffer_thead]
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fuzzing DNS multiThread")
    parser.add_argument('target', type=str, help="Target IP")
    parser.add_argument('--packets', type=int, default=10, help="Number of packets to send")
    parser.add_argument('--timeout', type=int, default=10, help="Timeout for the sniffer")

    args = parser.parse_args()
    print(f"Target: {args.target}, Packets: {args.packets}, Timeout: {args.timeout}")

    main(args.target, args.packets, args.timeout)