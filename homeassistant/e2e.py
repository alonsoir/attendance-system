import requests
import time
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

HA_URL = "http://homeassistant:8123"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJkOTk0YjQxZmY5YzE0NmFlOTA5ZTJlNzQwODNhMDU3NCIsImlhdCI6MTc0MDEzNzM2OCwiZXhwIjoyMDU1NDk3MzY4fQ.6Q_RpDrVgOtFQfWDnU1Kh6TheArxbww4d8qja4g92fU"
HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

def set_state(entity_id, state):
    url = f"{HA_URL}/api/states/{entity_id}"
    data = {
        "state": state,
        "attributes": {
            "friendly_name": entity_id.split(".")[1].replace("_", " ").title()
        }
    }
    logger.debug(f"Enviando solicitud a {url} con datos: {json.dumps(data)}")
    try:
        response = requests.post(url, headers=HEADERS, json=data, timeout=10)
        if response.status_code in (200, 201):
            logger.info(f"Estado de {entity_id} cambiado a {state}")
        else:
            logger.error(f"Error al cambiar estado: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        logger.error(f"Excepción al cambiar estado de {entity_id}: {e}")

def main():
    entity_id = "input_boolean.test_switch"
    logger.info("Iniciando simulación de cambios de estado en Home Assistant...")

    while True:
        # Encender
        set_state(entity_id, "on")
        logger.debug("Esperando 5 segundos tras encender...")
        time.sleep(5)

        # Apagar (para generar un cambio detectable)
        set_state(entity_id, "off")
        logger.debug("Esperando 5 segundos tras apagar...")
        time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Simulación detenida.")