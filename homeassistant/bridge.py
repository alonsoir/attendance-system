import asyncio
import json
import logging
import os
import time
from datetime import datetime
import websockets
import chromadb
from chromadb.config import Settings
import requests
from dotenv import load_dotenv  # Agrega esta importación

# Cargar variables de entorno desde .env
load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class HALLMBridge:
    def __init__(self, ha_url, ha_token, ollama_url, chromadb_url):
        self.ha_url = ha_url
        self.ha_token = ha_token
        self.ollama_url = ollama_url
        # Trato de usar un modelo local precargado, deshabilitar la descarga.
        chromadb_host = chromadb_url.split(":")[0]
        chromadb_port = int(chromadb_url.split(":")[1])
        self.chromadb_client = chromadb.HttpClient(
            host=chromadb_host,
            port=chromadb_port,
            settings=Settings(allow_reset=True, anonymized_telemetry=False)
        )
        # Intentar conectar con reintentos
        max_retries = 5
        for attempt in range(max_retries):
            try:
                logger.debug("Trying to connect to ChromaDB in Bridge...")
                self.chromadb_client = chromadb.HttpClient(host=chromadb_host, port=chromadb_port)
                break
            except ValueError as e:
                logger.debug("There was an error trying to connect to Chroma. Retrying..")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Espera 2 segundos antes de reintentar
                    continue
                else:
                    raise e

        self.collection = self.chromadb_client.get_or_create_collection(
            name="ha_telemetry",
            metadata={"description": "Home Assistant telemetry data"}
        )

    async def connect_to_ha(self):
        logger.debug("Trying to connect to HA.")
        uri = f"{self.ha_url}/api/websocket"
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    initial_response = json.loads(await websocket.recv())
                    if initial_response.get("type") != "auth_required":
                        logger.error(f"Unexpected initial response: {initial_response}")
                        await asyncio.sleep(5)
                        continue

                    auth_message = {"type": "auth", "access_token": self.ha_token}
                    await websocket.send(json.dumps(auth_message))

                    auth_response = json.loads(await websocket.recv())
                    if auth_response.get("type") != "auth_ok":
                        logger.error(f"Authentication failed: {auth_response}")
                        await asyncio.sleep(5)
                        continue
                    logger.info("Authentication successful")

                    sub_message = {"id": 1, "type": "subscribe_events", "event_type": "state_changed"}
                    await websocket.send(json.dumps(sub_message))
                    sub_response = json.loads(await websocket.recv())
                    if sub_response.get("success") is not True:
                        logger.error(f"Subscription failed: {sub_response}")
                        await asyncio.sleep(5)
                        continue
                    logger.info("Subscribed to state_changed events")

                    while True:
                        message = await websocket.recv()
                        logger.info(f"Raw WebSocket message: {message}")  # Log adicional
                        await self.process_message(json.loads(message))

            except websockets.exceptions.ConnectionClosed as e:
                logger.error(f"WebSocket connection closed: {e}")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Unexpected error in WebSocket connection: {e}")
                await asyncio.sleep(5)

    async def process_message(self, message):
        logger.debug(f"Received message: {json.dumps(message, indent=2)}")
        if message.get("type") == "event" and message["event"]["event_type"] == "state_changed":
            event_data = message["event"]["data"]
            entity_id = event_data["entity_id"]
            new_state = event_data["new_state"]
            old_state = event_data["old_state"]
            logger.info(
                f"Processing state change for {entity_id}: {old_state['state'] if old_state else 'None'} -> {new_state['state']}")
            document = {
                "entity_id": entity_id,
                "state": new_state["state"],
                "last_changed": new_state["last_changed"],
                "attributes": json.dumps(new_state["attributes"])
            }
            logger.debug(f"Storing in ChromaDB: {json.dumps(document, indent=2)}")
            self.collection.add(
                documents=[json.dumps(document)],
                ids=[f"{entity_id}_{datetime.now().isoformat()}"],
                metadatas=[{"entity_id": entity_id, "timestamp": datetime.now().isoformat()}]
            )
            logger.debug("Stored in ChromaDB successfully")
            logger.debug("Calling analyze_with_llm")
            await self.analyze_with_llm(document, old_state)

    async def analyze_with_llm(self, current_state, old_state):
        prompt = self.build_prompt(current_state, old_state)
        logger.debug(f"Sending prompt to Ollama: {prompt}")
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": "mistral", "prompt": prompt, "stream": False},
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"LLM response: {result}")
            await self.execute_llm_suggestion(result["response"])
        except requests.RequestException as e:
            logger.error(f"Error al consultar Ollama: {e}")
            # Acción por defecto si Ollama falla
            if current_state["entity_id"] == "input_boolean.test_switch" and current_state["state"] == "on":
                logger.info("Ollama falló, aplicando acción por defecto para input_boolean.test_switch: apagando")
                await self.websocket.send(json.dumps({
                    "id": self.message_id,
                    "type": "call_service",
                    "domain": "input_boolean",
                    "service": "turn_off",
                    "service_data": {"entity_id": "input_boolean.test_switch"}
                }))
                self.message_id += 1
                logger.info("=====================================")
                logger.info("¡APAGANDO input_boolean.test_switch POR DEFECTO!")
                logger.info("=====================================")

    async def connect_to_ha(self):
        logger.debug("Trying to connect to HA.")
        uri = f"{self.ha_url}/api/websocket"
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    self.websocket = websocket
                    initial_response = json.loads(await websocket.recv())
                    if initial_response.get("type") != "auth_required":
                        logger.error(f"Unexpected initial response: {initial_response}")
                        await asyncio.sleep(5)
                        continue

                    auth_message = {"type": "auth", "access_token": self.ha_token}
                    await websocket.send(json.dumps(auth_message))

                    auth_response = json.loads(await websocket.recv())
                    if auth_response.get("type") != "auth_ok":
                        logger.error(f"Authentication failed: {auth_response}")
                        await asyncio.sleep(5)
                        continue
                    logger.info("Authentication successful")

                    sub_message = {"id": 1, "type": "subscribe_events", "event_type": "state_changed"}
                    await websocket.send(json.dumps(sub_message))
                    sub_response = json.loads(await websocket.recv())
                    if sub_response.get("success") is not True:
                        logger.error(f"Subscription failed: {sub_response}")
                        await asyncio.sleep(5)
                        continue
                    logger.info("Subscribed to state_changed events")

                    while True:
                        try:
                            message = await websocket.recv()
                            logger.info(f"Raw WebSocket message: {message}")
                            await self.process_message(json.loads(message))
                        except websockets.exceptions.ConnectionClosed:
                            logger.error("WebSocket connection closed unexpectedly")
                            break  # Salir del bucle interno para reconectar
            except Exception as e:
                logger.error(f"Unexpected error in WebSocket connection: {e}")
            await asyncio.sleep(5)

    def build_prompt(self, current_state, old_state):
        """Construye el prompt para el LLM."""
        # Obtener contexto histórico de ChromaDB
        results = self.collection.query(
            query_texts=[f"Entity: {current_state['entity_id']}"],
            n_results=5
        )

        return f"""Analiza este cambio de estado en Home Assistant y sugiere acciones:

    Entidad: {current_state['entity_id']}
    Estado anterior: {old_state['state'] if old_state else 'None'}
    Estado actual: {current_state['state']}
    Atributos: {current_state['attributes']}

    Contexto histórico:
    {json.dumps(results, indent=2)}

    Si la entidad es 'input_boolean.test_switch' y el estado actual es 'on', recomienda apagarla inmediatamente ejecutando el servicio 'input_boolean.turn_off'. Para otros casos, analiza y sugiere acciones razonables. Responde en formato JSON con esta estructura:
    {{
        "análisis": "tu análisis del cambio",
        "acciones_recomendadas": [
            {{
                "servicio": "servicio.a_llamar",
                "datos": {{
                    "parámetros": "necesarios"
                }}
            }}
        ]
    }}
    """

    async def execute_llm_suggestion(self, llm_response):
        """Ejecuta las sugerencias del LLM si son apropiadas."""
        try:
            suggestion = json.loads(llm_response)
            for action in suggestion.get("acciones_recomendadas", []):
                # Validar y ejecutar la acción en HA
                if action["servicio"] == "input_boolean.turn_off" and "entity_id" in action["datos"]:
                    logger.info(
                        "\n" +
                        "=====================================\n" +
                        f"¡APAGANDO {action['datos']['entity_id']} COMO SUGIERE EL LLM!\n" +
                        "=====================================\n"
                    )
                else:
                    logger.info(f"Ejecutando acción sugerida: {json.dumps(action, indent=2)}")
                await self.call_ha_service(action["servicio"], action["datos"])
        except json.JSONDecodeError:
            logger.error("Invalid JSON response from LLM")
        except Exception as e:
            logger.error(f"Error executing suggestion: {e}")

    async def call_ha_service(self, service, data):
        """Llama a un servicio de Home Assistant."""
        domain, service_name = service.split(".")
        url = f"{self.ha_url}/api/services/{domain}/{service_name}"
        headers = {
            "Authorization": f"Bearer {self.ha_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            logger.error(f"Error calling HA service: {response.text}")


async def main():
    bridge = HALLMBridge(
        ha_url=os.getenv("HA_URL"),
        ha_token=os.getenv("HA_TOKEN"),
        ollama_url=os.getenv("OLLAMA_URL"),
        chromadb_url=os.getenv("CHROMADB_URL")
    )
    await bridge.connect_to_ha()


if __name__ == "__main__":
    asyncio.run(main())