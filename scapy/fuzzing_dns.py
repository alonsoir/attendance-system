from scapy.all import *
from scapy.layers.dns import *

'''
Hacer **fuzzing** es una técnica de seguridad informática utilizada para probar la robustez y seguridad de un sistema 
enviándole datos aleatorios, malformados o inesperados para observar cómo responde. 
El objetivo es encontrar vulnerabilidades, fallos o comportamientos inesperados.  

### 🔍 **¿Cómo funciona el fuzzing?**  
1. **Generación de datos de prueba** → Se crean datos de entrada aleatorios o modificados, a menudo siguiendo un patrón 
que intenta romper el sistema.  
2. **Envío a la aplicación objetivo** → Se envían estos datos a un servicio, protocolo o software que queremos probar.  
3. **Monitoreo de la respuesta** → Se observa si el sistema responde correctamente, se cuelga, se bloquea o presenta 
comportamientos inesperados.  

### 🛠 **Ejemplo de fuzzing en DNS**  
En tu código, cuando usas:  
```python
pkt = IP(dst=target) / UDP(dport=53) / fuzz(DNS())
```
Estás aplicando fuzzing al protocolo **DNS**, lo que significa que se generan paquetes DNS con datos aleatorios o 
inesperados para ver cómo responde el servidor.  

### 🎯 **¿Para qué se usa el fuzzing?**  
- **Pruebas de seguridad**: Detectar vulnerabilidades explotables en aplicaciones.  
- **Evaluación de estabilidad**: Ver si una aplicación puede manejar correctamente datos inesperados.  
- **Investigación de protocolos**: Descubrir cómo reaccionan sistemas que no documentan correctamente sus errores.  

(attendance-system-py3.10) ┌<▸> ~/g/a/scapy 
└➤ sudo poetry run python fuzzing_dns.py 208.67.222.222 --packets 5

Target: 208.67.222.222, Packets: 5
Begin emission
..
Finished sending 1 packets
.*
Received 4 packets, got 1 answers, remaining 0 packets
###[ IP ]###
  version   = 4
  ihl       = 5
  tos       = 0x0
  len       = 72
  id        = 46934
  flags     = 
  frag      = 0
  ttl       = 112
  proto     = udp
  chksum    = 0xc124
  src       = 8.8.8.8
  dst       = 192.168.1.114
  \options   \
###[ UDP ]###
     sport     = domain
     dport     = domain
     len       = 52
     chksum    = 0x8055
###[ DNS ]###
        id        = 0
        qr        = 1
        opcode    = QUERY
        aa        = 0
        tc        = 0
        rd        = 1
        ra        = 1
        z         = 0
        ad        = 0
        cd        = 0
        rcode     = ok
        qdcount   = 1
        ancount   = 1
        nscount   = 0
        arcount   = 0
        \qd        \
         |###[ DNS Question Record ]###
         |  qname     = b'google.com.'
         |  qtype     = A
         |  unicastresponse= 0
         |  qclass    = IN
        \an        \
         |###[ DNS Resource Record ]###
         |  rrname    = b'google.com.'
         |  type      = A
         |  cacheflush= 0
         |  rclass    = IN
         |  ttl       = 198
         |  rdlen     = None
         |  rdata     = 142.250.200.142
        \ns        \
        \ar        \

None
Begin emission
.
Finished sending 1 packets
.....
Received 6 packets, got 0 answers, remaining 1 packets
Begin emission

Finished sending 1 packets
...
Received 3 packets, got 0 answers, remaining 1 packets
Begin emission

Finished sending 1 packets
.......
Received 7 packets, got 0 answers, remaining 1 packets
Begin emission
.
Finished sending 1 packets

Received 1 packets, got 0 answers, remaining 1 packets
Begin emission

Finished sending 1 packets
....
Received 4 packets, got 0 answers, remaining 1 packets
Response 1: IP / UDP / DNS Ans 142.250.200.142
Response 2: No response received.
Response 3: No response received.
Response 4: No response received.
Response 5: No response received.
Response 6: No response received.
(attendance-system-py3.10) ┌<▸> ~/g/a/scapy 
└➤ 

'''
def test_dns_valid():
    target = "8.8.8.8"
    pkt = IP(dst=target) / UDP(dport=53) / DNS(rd=1, qd=DNSQR(qname="google.com"))
    response = sr1(pkt, timeout=2)
    print(response.show())
    return response


def create_and_send_package(target):
    pkt = IP(dst=target) / UDP(dport=53) / fuzz(DNS())
    response = sr1(pkt, timeout=1)
    return response

def create_and_send_package_less_aggresive(target):
    pkt = IP(dst=target) / UDP(dport=53) / DNS(rd=1, qd=DNSQR(qname="example.org"))
    response = sr1(pkt, timeout=1)
    return response


def analyze_responses(responses):
    """Analiza las respuestas recibidas."""
    for i, response in enumerate(responses):  # Cambiado para iterar correctamente
        if response is None:
            print(f"Response {i + 1}: No response received.")
        else:
            print(f"Response {i + 1}: {response.summary()}")



def main(target, num_packages):
    """Función principal que gestiona el envío y análisis de paquetes."""
    responses = []
    response = test_dns_valid()
    responses.append(response)
    for _ in range(num_packages):
        response = create_and_send_package_less_aggresive(target)
        responses.append(response)
        time.sleep(1)  # Añadir pausa entre envíos
    analyze_responses(responses)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fuzzing DNS")
    parser.add_argument('target', type=str, help="Target IP")
    parser.add_argument('--packets', type=int, default=10, help="Number of packets to send")

    args = parser.parse_args()
    print(f"Target: {args.target}, Packets: {args.packets}")

    main(args.target, args.packets)
