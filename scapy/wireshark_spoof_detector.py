#!/usr/bin/env python3
"""
Este script sirve para automatizar Wireshark para monitorear el tráfico de red y detectar cambios en las direcciones
MAC que podrían indicar spoofing, aunque Wireshark en sí mismo no tiene funcionalidades de automatización integradas
para este propósito específico.

Herramientas Alternativas
NetworkMiner: Puede analizar flujos de tráfico en tiempo real o capturas de tráfico y tiene características
para detectar cambios en las direcciones MAC.

Bro/Zeek: Un sistema de monitoreo de red que puede ser configurado para detectar y alertar sobre cambios en
las direcciones MAC.

Sistemas de Detección de Intrusos (IDS) como Snort o Suricata:
Pueden ser configurados con reglas que detecten cambios inusuales en las direcciones MAC.

variables de entorno no obligatorias para avisar el administrador de la red.

export SMTP_SERVER=smtp.yourdomain.com
export SMTP_PORT=465
export SMTP_USER=alert@yourdomain.com
export SMTP_PASSWORD=yourpassword
export SMTP_RECEIVER=admin@yourdomain.com

sudo poetry run python wireshark_spoof_detector.py --interface en0 --filter 'ether proto \\ip' --threshold 5 --interval 60 --threads 4

sudo poetry run python wireshark_spoof_detector.py --interface Wi-Fi --filter 'ether proto \\ip' --threshold 5 --interval 60 --threads 4

--filter literalmente espera cualquier tipo de filtro que wireshark acepte, por lo que es amplísimo.
No es lo mismo ejecutar en linux que en osx, mira la documentación específica de los filtros para cada caso.

Capturar todo el tráfico HTTP pero no HTTPS en la red 192.168.1.0/24:
    tcp port 80 and net 192.168.1.0/24 and not port 443

Capturar paquetes ICMP con un tamaño específico:
    icmp and len > 1000

Capturar tráfico de DNS que no sea del servidor DNS local:
    udp port 53 and not src host 192.168.1.100

"""
# !/usr/bin/env python3

import pyshark
import time
from collections import defaultdict
import logging
from email.message import EmailMessage
import smtplib
import argparse
import os
from concurrent.futures import ThreadPoolExecutor

# Configuración de logging con más detalle
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('mac_spoofing.log'), logging.StreamHandler()])


def send_alert_email(macs_detected):
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = os.environ.get('SMTP_PORT', 465)
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASSWORD')

    if not all([smtp_server, smtp_user, smtp_pass]):
        logging.warning("No se pueden enviar correos. Algunas variables de entorno no están definidas.")
        return

    msg = EmailMessage()
    msg.set_content(f"Se han detectado las siguientes nuevas direcciones MAC: {', '.join(macs_detected)}")
    msg['Subject'] = 'Alerta de MAC Spoofing'
    msg['From'] = smtp_user
    msg['To'] = os.environ.get('SMTP_RECEIVER', smtp_user)

    try:
        logging.info("Intentando enviar correo de alerta...")
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)
        logging.info("Correo enviado exitosamente.")
    except Exception as e:
        logging.error(f"Error enviando correo: {e}")


def monitor_network(interface, bpf_filter, alert_threshold=5, check_interval=60):
    logging.info(f"Iniciando captura en {interface} con filtro: {bpf_filter}")
    capture = pyshark.LiveCapture(interface=interface, bpf_filter=bpf_filter)
    capture.set_debug()
    macs_seen = defaultdict(list)
    last_check = time.time()
    packet_count = 0

    try:
        for packet in capture:
            packet_count += 1
            if packet_count % 1000 == 0:  # Cada 1000 paquetes, actualizamos el conteo
                logging.info(f"Paquetes procesados: {packet_count}")

            if 'eth' in packet:
                mac_src = packet.eth.src
                current_time = time.time()

                # Registrar la última aparición de esta MAC
                macs_seen[mac_src].append(current_time)

                # Limpieza de entradas antiguas (por ejemplo, más de 1 hora sin cambios)
                for mac in list(macs_seen.keys()):
                    if current_time - macs_seen[mac][-1] > 3600:  # 1 hour
                        del macs_seen[mac]

                # Comprobación periódica para alertas
                if current_time - last_check > check_interval:
                    new_macs_count = sum(1 for times in macs_seen.values() if current_time - times[0] < check_interval)
                    logging.info(f"MACs nuevas detectadas en el último intervalo: {new_macs_count}")
                    if new_macs_count >= alert_threshold:
                        new_macs = [mac for mac, times in macs_seen.items() if current_time - times[0] < check_interval]
                        logging.warning(f"Potencial MAC spoofing detectado: {new_macs}")
                        send_alert_email(new_macs)
                    last_check = current_time


    except KeyboardInterrupt:
        logging.info("Monitoreo detenido por el usuario")
    except Exception as e:
        logging.error(f"Error en el monitoreo: {e}")
    finally:
        if capture:
            capture.close()  # Asegúrate de cerrar la captura
        logging.info(f"Fin de la captura. Total de paquetes procesados: {packet_count}")

def worker(interface, bpf_filter, threshold, interval):
    logging.info(f"Iniciando hilo para monitoreo en {interface}")
    monitor_network(interface, bpf_filter, threshold, interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Monitor de MAC Spoofing')
    parser.add_argument('--interface', type=str, required=True, help='Interfaz de red para monitorear')
    parser.add_argument('--filter', type=str, default='ether proto \\ip',
                        help='Filtro BPF para el tráfico a monitorear')
    parser.add_argument('--threshold', type=int, default=5, help='Número de nuevas MACs para generar una alerta')
    parser.add_argument('--interval', type=int, default=60, help='Intervalo en segundos para revisar las MACs')
    parser.add_argument('--threads', type=int, default=1, help='Número de hilos para usar')
    args = parser.parse_args()

    logging.info(f"Iniciando monitoreo con {args.threads} hilos en {args.interface} con filtro {args.filter}")

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for i in range(args.threads):
            executor.submit(worker, args.interface, args.filter, args.threshold, args.interval)