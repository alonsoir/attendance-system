from scapy.all import sniff
import time

from scapy.layers.l2 import ARP

'''
Si habilitas packet forwarding, los paquetes enviados al objetivo se redirigen a tu máquina.

    sysctl -w net.inet.ip.forwarding=1

Literalmente, no quieres que el ip forward se active nunca.

'''
# Diccionario para almacenar IPs y sus MACs asociadas
arp_table = {}

def detect_arp_spoof(pkt):
    if pkt.haslayer(ARP) and pkt[ARP].op == 2:  # Solo respuestas ARP (op=2)
        src_ip = pkt[ARP].psrc  # IP de origen
        src_mac = pkt[ARP].hwsrc  # MAC de origen

        if src_ip in arp_table:
            if arp_table[src_ip] != src_mac:
                print(f"[ALERTA] Posible ARP Spoofing detectado:")
                print(f" - IP: {src_ip} ahora tiene MAC {src_mac}")
                print(f" - Antes: {arp_table[src_ip]}")
        else:
            arp_table[src_ip] = src_mac  # Guardar la relación IP-MAC

# Captura paquetes en la red en tiempo real
print("[*] Monitoreando tráfico ARP...")
sniff(filter="arp", prn=detect_arp_spoof, store=0)

'''
ARP Spoofing permite realizar ataques Man-in-the-Middle (MITM) en máquinas dentro de la misma red local, lo que significa que un atacante que ya ha obtenido acceso a la red (por ejemplo, conectándose a una Wi-Fi sin seguridad, hackeando credenciales o explotando una vulnerabilidad) puede redirigir tráfico de otras máquinas hacia la suya y espiar, modificar o redirigir la información en tiempo real.

🔍 ¿Cómo un atacante puede capturar la información?

Una vez que el atacante ha logrado redirigir el tráfico, tiene varias maneras de capturar y analizar la información:

1️⃣ Sniffing del tráfico con Wireshark o tcpdump
El atacante puede usar herramientas como Wireshark o tcpdump para capturar paquetes en la interfaz de red.
Ejemplo con tcpdump:

sudo tcpdump -i en0 -n
-i en0: Captura tráfico en la interfaz en0 (ajústala según tu sistema).
-n: Evita la resolución de nombres de host para mayor velocidad.
Si quiere capturar solo paquetes HTTP o DNS:

sudo tcpdump -i en0 port 80 or port 53
Y si quiere guardarlos en un archivo:

sudo tcpdump -i en0 -w captura.pcap
Luego, puede abrir captura.pcap en Wireshark para analizar el tráfico.

2️⃣ Haciendo un Proxy para Interceptar y Modificar el Tráfico
Un atacante puede redirigir el tráfico HTTP/HTTPS a través de su máquina y analizarlo con un proxy como mitmproxy o Bettercap.

Ejemplo con mitmproxy:

mitmproxy -T --host
Esto abre un proxy transparente y permite ver las solicitudes HTTP que pasan a través de la máquina atacante.

Si el tráfico está cifrado con HTTPS, el atacante puede:

Usar un ataque SSL Strip para intentar forzar conexiones HTTP en lugar de HTTPS.
Instalar certificados falsos en la víctima para interceptar tráfico cifrado.
3️⃣ Guardando Credenciales con herramientas como Ettercap
Herramientas como Ettercap permiten hacer ARP Spoofing de forma automatizada y capturar credenciales enviadas por HTTP, FTP, Telnet, etc.

ettercap -T -M arp:remote /192.168.1.100/ /192.168.1.1/
Esto envenena la relación entre la víctima (192.168.1.100) y el router (192.168.1.1), permitiendo capturar credenciales.

4️⃣ Creando un Keylogger o Malware en la Red
Si el atacante controla la red, podría:

Inyectar scripts maliciosos en sitios web que visite la víctima (inyección de JavaScript).
Forzar la descarga de malware en la víctima.
Crear un portal falso (Evil Twin Attack) para robar credenciales.
🛡️ ¿Cómo evitar esto?

✅ Usar ARP estático en dispositivos críticos

sudo arp -s 192.168.1.1 42:2e:d0:d9:4d:1e
✅ Usar conexiones cifradas (HTTPS, SSH, VPN) siempre que sea posible
✅ Activar la detección de ARP Spoofing en el router o firewall
✅ Usar IDS/IPS (como Snort o Suricata) para detectar actividad sospechosa
✅ Evitar conectarse a redes Wi-Fi abiertas o no confiables

📌 Resumen:
✔️ ARP Spoofing permite a un atacante en la misma red interceptar tráfico entre una víctima y el router.
✔️ El atacante puede guardar la información capturada en archivos .pcap, usar proxies MITM, keyloggers o malware.
✔️ Protegerse requiere ARP estático, usar VPNs, HTTPS, detección de spoofing y evitar redes inseguras.

(attendance-system-py3.10) ┌<▸> ~/g/a/scapy 
└➤ arp -a

? (192.168.1.1) at NON-VISIBLE on en0 ifscope [ethernet]
? (192.168.1.49) at NON-VISIBLE on en0 ifscope [ethernet]
? (192.168.1.62) at NON-VISIBLE on en0 ifscope [ethernet]
? (192.168.1.107) at NON-VISIBLE on en0 ifscope [ethernet]
? (192.168.1.114) at NON-VISIBLE on en0 ifscope permanent [ethernet]
? (192.168.1.119) at NON-VISIBLE on en0 ifscope [ethernet]
? (192.168.1.255) at NON-VISIBLE on en0 ifscope [ethernet]
mdns.mcast.net (224.0.0.251) at NON-VISIBLE on en0 ifscope permanent [ethernet]
? (239.255.255.250) at NON-VISIBLE on en0 ifscope permanent [ethernet]
(attendance-system-py3.10) ┌<▸> ~/g/a/scapy 
└➤ ip neigh show

...
(attendance-system-py3.10) ┌<▸> ~/g/a/scapy 
└➤ ping -c 1 192.168.1.1 && arp -a | grep 192.168.1.1

PING 192.168.1.1 (192.168.1.1): 56 data bytes
64 bytes from 192.168.1.1: icmp_seq=0 ttl=64 time=10.444 ms

--- 192.168.1.1 ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 10.444/10.444/10.444/0.000 ms
? (192.168.1.1) at NON-VISIBLE on en0 ifscope [ethernet]
? (192.168.1.107) at NON-VISIBLE on en0 ifscope [ethernet]
? (192.168.1.114) at NON-VISIBLE on en0 ifscope permanent [ethernet]
? (192.168.1.119) at NON-VISIBLE on en0 ifscope [ethernet]
(attendance-system-py3.10) ┌<▸> ~/g/a/scapy 
└➤ 

# Este comando fija la arp address de tu router, averigua la arp con el comando arp -a
sudo arp -s 192.168.1.1 NON-VISIBLE

# Este comando examina la arp del router, si ha cambiado, estas bajo ataque 
arp -a | grep 192.168.1.1

'''
