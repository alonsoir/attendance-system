from scapy.all import *
import time
import socket
import threading
import queue

from scapy.layers.dns import DNS, DNSQR, DNSRR
"""
Este script:

Captura todas las respuestas DNS en la red.
Para cada respuesta, verifica si la dirección IP proporcionada coincide con la que se obtiene realizando una consulta DNS legítima.
Alerta si se detecta una discrepancia, lo que podría indicar un ataque de DNS spoofing.

"""
# Cola para comunicación entre hilos
dns_queue = queue.Queue()
respuestas = {}


def resolver_dns_legitimo(dominio):
    try:
        return socket.gethostbyname(dominio)
    except:
        return None


def verificador_dns():
    while True:
        try:
            pregunta, respuesta_recibida = dns_queue.get(timeout=1)
            if pregunta in respuestas:
                continue  # Ya verificada

            # Obtener resolución legítima
            ip_legitima = resolver_dns_legitimo(pregunta)
            if ip_legitima and ip_legitima != respuesta_recibida:
                print(f"[!] ALERTA: Posible DNS spoofing detectado!")
                print(f"    Dominio: {pregunta}")
                print(f"    IP recibida: {respuesta_recibida}")
                print(f"    IP esperada: {ip_legitima}")

            # Guardar para no verificar de nuevo
            respuestas[pregunta] = ip_legitima

        except queue.Empty:
            time.sleep(0.1)
        except Exception as e:
            print(f"[!] Error en verificador: {e}")


def sniffer_callback(pkt):
    if DNS in pkt and pkt[DNS].qr == 1 and pkt[DNS].ancount > 0:
        try:
            dominio = pkt[DNSQR].qname.decode('utf-8').rstrip('.')
            for i in range(pkt[DNS].ancount):
                if pkt[DNSRR][i].type == 1:  # Tipo A (dirección IPv4)
                    ip_recibida = pkt[DNSRR][i].rdata
                    dns_queue.put((dominio, ip_recibida))
        except:
            pass


def main():
    # Iniciar el hilo verificador
    verificador = threading.Thread(target=verificador_dns)
    verificador.daemon = True
    verificador.start()

    print("[*] Iniciando detector de DNS spoofing...")
    print("[*] Presiona Ctrl+C para detener")

    try:
        sniff(filter="udp port 53", prn=sniffer_callback)
    except KeyboardInterrupt:
        print("[*] Deteniendo detector...")


if __name__ == "__main__":
    main()