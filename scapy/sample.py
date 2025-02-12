from scapy.all import *
from scapy.layers.inet import IP, ICMP

target_ip="8.8.8.8"

icmp = IP(dst=target_ip)/ICMP()

send(icmp)