#!/usr/bin/env python3

import os
import sys  # Añadimos la importación de sys
import json
import logging

from .arp_monitor import ARPMonitor

if __name__ == "__main__":
        try:
            # Verificar permisos de root/administrador
            if os.geteuid() != 0:
                print("[!] Este script requiere permisos de administrador")
                print("[!] Por favor, ejecute con sudo")
                sys.exit(1)

            # Crear directorio para logs si no existe
            os.makedirs('logs', exist_ok=True)

            # Iniciar monitor
            print("[*] Iniciando ARP Monitor...")
            monitor = ARPMonitor()  # Ahora la clase debería estar definida
            monitor.monitor()

        except KeyboardInterrupt:
            print("\n[*] Deteniendo ARP Monitor...")
            logging.info("Monitoreo detenido por usuario")
            try:
                monitor.cleanup()
            except:
                pass
        except Exception as e:
            logging.error(f"Error fatal: {e}")
            print(f"[!] Error fatal: {e}")
            try:
                monitor.cleanup()
            except:
                pass
            sys.exit(1)

