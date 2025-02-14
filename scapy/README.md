1) DNS Spoofing: Manipulación de respuestas DNS para redirigir tráfico a sitios controlados por un atacante. OK

2) ARP Spoofing: Envío de paquetes ARP falsos para asociar la MAC del atacante con la IP de un dispositivo legítimo en la 
red, permitiendo interceptar o desviar tráfico. OK

3) IP Spoofing: Consiste en falsificar la dirección IP de origen en los paquetes de red para hacerse pasar por otro sistema 
o evadir filtros basados en IP.

4) MAC Spoofing: Similar al ARP spoofing, pero se centra en modificar la dirección MAC del dispositivo para eludir 
controles de acceso basados en dirección física.

5) Email Spoofing: Falsificación de los campos del remitente en correos electrónicos para que parezcan provenir de una 
fuente legítima. Es común en ataques de phishing.

6) Caller ID Spoofing: En telefonía, consiste en modificar el número que aparece en el identificador de llamadas para 
engañar al receptor.

7) Website/URL Spoofing: Creación de sitios web falsos que imitan a otros legítimos para robar información 
(también conocido como phishing).

8) SMS Spoofing: Alteración del número de origen en mensajes de texto para hacerse pasar por una entidad confiable.

9) DHCP Spoofing: Un atacante configura un servidor DHCP falso para distribuir información de red maliciosa, 
como puertas de enlace o servidores DNS manipulados.

10) BGP Spoofing: Manipulación de protocolos de enrutamiento para redirigir tráfico a través de redes controladas por el 
atacante.

11) GPS Spoofing: Emisión de señales falsas de GPS para engañar a dispositivos sobre su ubicación real.




# IP Spoofing

    Definición:
    El IP spoofing consiste en crear paquetes de Internet Protocol (IP) con una dirección de origen falsificada, 
    lo que hace parecer que los paquetes provienen de otra fuente.
    
    Demostración de IP Spoofing (Para Propósitos Educativos)
    Para entender cómo se realiza un ataque de IP spoofing, aquí hay un ejemplo simplificado:
    
    Herramientas Necesarias: 
    Herramientas como hping3 en línea de comandos o scapy en Python pueden ser usadas para este tipo de ataques.
    
    Ejemplo con Scapy:

        from scapy.all import IP, ICMP, send
        
        # Configuración del paquete con una IP de origen falsificada
        spoofed_packet = IP(src="192.168.1.100", dst="192.168.1.1")/ICMP()/"¡Hola desde el atacante!"
        # Envío del paquete
        send(spoofed_packet)

En este ejemplo, estamos enviando un paquete ICMP (ping) desde una dirección IP que no es la real del atacante 
(192.168.1.100) hacia otra dirección dentro de la misma red (192.168.1.1).

Protección contra el IP Spoofing
1. Filtrado de Paquetes en Redes:
Listas de Control de Acceso (ACLs): Configura tus routers para filtrar paquetes con direcciones IP internas 
provenientes desde fuera de tu red.

    access-list 100 deny ip any 192.168.1.0 0.0.0.255
    access-list 100 permit ip any any

   Este ejemplo de ACL evitará que paquetes con direcciones IP de tu red local sean aceptados si provienen de fuera de tu red.

   2. Ingreso y Egreso de Filtrado:
   Implementa filtrado en los puntos de entrada y salida de tu red para asegurarte de que los paquetes entrantes o 
   salientes desde direcciones no autorizadas sean bloqueados.

   3. Sistemas de Detección y Prevención de Intrusos (IDS/IPS):
   Herramientas como Snort pueden ser configuradas para detectar anomalías en el tráfico que puedan sugerir spoofing.

   4. Configuración de Routers:
   Desactivar la respuesta a pings desde fuera de la red interna puede reducir los vectores de ataque.

   5. Uso de Protocolos de Enrutamiento Seguros:
   Asegurar que los protocolos de enrutamiento usen autenticación (como BGP con autenticación MD5) para evitar la 
   manipulación de rutas.

   6. Monitoreo Activo:
   Usar herramientas de monitoreo de red para detectar y responder a cualquier tráfico inusual que podría ser indicativo 
   de un ataque de spoofing.

   7. Educación y Políticas:
   Asegurar que los usuarios entiendan los riesgos y no respondan a comunicaciones sospechosas que podrían ser parte de un 
   ataque más amplio.

La protección contra el IP spoofing es multi-facética y requiere una combinación de medidas técnicas y de políticas de 
seguridad para ser efectiva.


# MAC Spoofing
    Definición:
    El MAC spoofing es una técnica donde se cambia la dirección MAC (Media Access Control) de una tarjeta de red para imitar
    la de otra, permitiendo que un dispositivo se haga pasar por otro en la red local.
    
    Demostración de MAC Spoofing (Para Propósitos Educativos)
    En Sistemas Operativos:
    En Windows:
    Usar el comando netsh para cambiar la MAC:
    cmd
        netsh interface set interface "Nombre de la Interfaz" adminstate=disable
        netsh interface set interface "Nombre de la Interfaz" adminstate=enable newmac=XX-XX-XX-XX-XX-XX
    En Linux:
    Cambiar la MAC con ifconfig o ip:
    bash
        sudo ifconfig eth0 down
        sudo ifconfig eth0 hw ether 00:11:22:33:44:55
        sudo ifconfig eth0 up
    En macOS:
    Usar la herramienta networksetup:
    bash
        sudo networksetup -setairportpower en0 off
        sudo networksetup -setairportpower en0 on
        sudo networksetup -setmacaddress en0 00:11:22:33:44:55
    
    Protección contra el MAC Spoofing
    1. Port Security en Switches:
    
    Configura la seguridad de puerto en los switches de red para limitar la cantidad de direcciones MAC permitidas en cada puerto físico:
    Ejemplo en un switch Cisco:
    plaintext
        switchport mode access
        switchport port-security
        switchport port-security maximum 1
        switchport port-security violation shutdown
        
       Esto asegura que solo un dispositivo con una MAC conocida pueda usar ese puerto.
    
    2. Filtrado de MAC:
    
    Implementar listas de control de acceso basadas en MAC (MAC ACLs) para permitir o denegar tráfico basado en 
    direcciones MAC específicas.
    
    3. Monitorización de la Red:
    
    Usar herramientas como Wireshark para monitorear el tráfico de red y detectar cambios en las direcciones MAC que 
    podrían indicar spoofing.
    
    4. DHCP Snooping:
    
    Configurar DHCP Snooping en los switches para evitar que dispositivos no autorizados actúen como servidores DHCP, 
    lo cual puede ser usado en ataques de MAC spoofing para asignar direcciones IP fraudulentas.
    
    5. Uso de 802.1X:
    
    Implementar el estándar de autenticación de puertos 802.1X, donde los dispositivos deben autenticarse antes de 
    obtener acceso a la red.
    
    6. Políticas de Seguridad:
    
    Asegurarse de que las políticas de red incluyan revisiones periódicas de las direcciones MAC conectadas a la red 
    para detectar dispositivos no autorizados.
    
    7. Educación de Usuarios:
    
    Educar a los usuarios sobre las prácticas seguras de red y ser cautelosos con los dispositivos conectados a la red.
    
    La protección contra el MAC spoofing requiere una combinación de medidas de hardware, software y políticas para 
    garantizar que solo los dispositivos autorizados puedan acceder y operar dentro de la red.