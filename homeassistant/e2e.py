import requests
import time
import json

# Configuración
HA_URL = "http://localhost:8123"  # Ajusta si HA está en otro host/puerto
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJkOTk0YjQxZmY5YzE0NmFlOTA5ZTJlNzQwODNhMDU3NCIsImlhdCI6MTc0MDEzNzM2OCwiZXhwIjoyMDU1NDk3MzY4fQ.6Q_RpDrVgOtFQfWDnU1Kh6TheArxbww4d8qja4g92fU"  # Tu token desde .env
HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}


def set_state(entity_id, state):
    """Cambia el estado de una entidad en Home Assistant."""
    url = f"{HA_URL}/api/states/{entity_id}"
    data = {
        "state": state,
        "attributes": {
            "friendly_name": entity_id.split(".")[1].replace("_", " ").title()
        }
    }
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code == 200 or response.status_code == 201:
        print(f"Estado de {entity_id} cambiado a {state}")
    else:
        print(f"Error al cambiar estado: {response.status_code} - {response.text}")


def main():
    entity_id = "input_boolean.test_switch"

    print("Simulando cambios de estado en Home Assistant...")
    while True:
        # Encender
        set_state(entity_id, "on")
        time.sleep(5)  # Espera 5 segundos

        # Apagar
        set_state(entity_id, "off")
        time.sleep(5)  # Espera 5 segundos


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Simulación detenida.")