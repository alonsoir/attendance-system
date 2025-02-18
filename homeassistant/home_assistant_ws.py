import asyncio
import websockets
import json
import ollama

# Configuración de Home Assistant
HA_URL = "ws://localhost:8123/api/websocket"
HA_TOKEN = ""


# Función para enviar un mensaje a Home Assistant
async def send_to_ha(ws, message):
    await ws.send(json.dumps(message))
    response = await ws.recv()
    return json.loads(response)


# Función principal para manejar la conexión con Home Assistant
async def connect_to_ha():
    async with websockets.connect(HA_URL) as ws:
        # Autenticación con Home Assistant
        await send_to_ha(ws, {"type": "auth", "access_token": HA_TOKEN})

        # Suscribirse a eventos de Home Assistant
        await send_to_ha(ws, {"id": 1, "type": "subscribe_events", "event_type": "state_changed"})

        while True:
            message = await ws.recv()
            event = json.loads(message)

            # Extraer información del evento
            entity_id = event.get("event", {}).get("data", {}).get("entity_id", "")
            new_state = event.get("event", {}).get("data", {}).get("new_state", {}).get("state", "")

            if entity_id and new_state:
                print(f"📡 Evento recibido: {entity_id} -> {new_state}")

                # Consultar al modelo LLM para decidir qué hacer
                response = ollama.chat(model="mistral", messages=[
                    {"role": "system", "content": "Eres un asistente de automatización para Home Assistant."},
                    {"role": "user",
                     "content": f"El estado de {entity_id} ha cambiado a {new_state}. ¿Qué debería hacer?"}
                ])

                action = response["message"]["content"]
                print(f"🤖 Respuesta del LLM: {action}")

                # Enviar una acción a Home Assistant si es necesario
                if "enciende" in action.lower():
                    service_data = {
                        "id": 2,
                        "type": "call_service",
                        "domain": "light",
                        "service": "turn_on",
                        "service_data": {"entity_id": entity_id}
                    }
                    await send_to_ha(ws, service_data)


# Ejecutar el cliente WebSocket
asyncio.run(connect_to_ha())
