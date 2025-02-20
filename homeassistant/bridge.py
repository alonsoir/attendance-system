import asyncio
import json
import logging
import os
from datetime import datetime
import websockets
import chromadb
from chromadb.config import Settings
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HALLMBridge:
    def __init__(self, ha_url, ha_token, ollama_url, chromadb_url):
        self.ha_url = ha_url
        self.ha_token = ha_token
        self.ollama_url = ollama_url
        self.chromadb_client = chromadb.HttpClient(host=chromadb_url)

        # Crear o obtener la colección para telemetría
        self.collection = self.chromadb_client.get_or_create_collection(
            name="ha_telemetry",
            metadata={"description": "Home Assistant telemetry data"}
        )

    async def connect_to_ha(self):
        """Conecta al WebSocket de Home Assistant."""
        uri = f"{self.ha_url}/api/websocket"
        async with websockets.connect(uri) as websocket:
            # Autenticación
            auth_message = {
                "type": "auth",
                "access_token": self.ha_token
            }
            await websocket.send(json.dumps(auth_message))
            auth_response = await websocket.recv()
            logger.info(f"Auth response: {auth_response}")

            # Suscribirse a eventos de estado
            sub_message = {
                "id": 1,
                "type": "subscribe_events",
                "event_type": "state_changed"
            }
            await websocket.send(json.dumps(sub_message))

            while True:
                try:
                    message = await websocket.recv()
                    await self.process_message(json.loads(message))
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

    async def process_message(self, message):
        """Procesa los mensajes recibidos de HA."""
        if message.get("type") == "event" and message["event"]["event_type"] == "state_changed":
            # Extraer datos relevantes
            event_data = message["event"]["data"]
            entity_id = event_data["entity_id"]
            new_state = event_data["new_state"]
            old_state = event_data["old_state"]

            # Crear documento para la base de datos vectorial
            document = {
                "entity_id": entity_id,
                "state": new_state["state"],
                "last_changed": new_state["last_changed"],
                "attributes": json.dumps(new_state["attributes"])
            }

            # Guardar en ChromaDB
            self.collection.add(
                documents=[json.dumps(document)],
                ids=[f"{entity_id}_{datetime.now().isoformat()}"],
                metadatas=[{"entity_id": entity_id, "timestamp": datetime.now().isoformat()}]
            )

            # Analizar con LLM si es necesario
            await self.analyze_with_llm(document, old_state)

    async def analyze_with_llm(self, current_state, old_state):
        """Analiza los cambios de estado con el LLM."""
        # Construir el prompt
        prompt = self.build_prompt(current_state, old_state)

        # Consultar Ollama
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            }
        )

        if response.status_code == 200:
            result = response.json()
            await self.execute_llm_suggestion(result["response"])

    def build_prompt(self, current_state, old_state):
        """Construye el prompt para el LLM."""
        # Obtener contexto histórico de ChromaDB
        results = self.collection.query(
            query_texts=[f"Entity: {current_state['entity_id']}"],
            n_results=5
        )

        return f"""Analiza el siguiente cambio de estado en Home Assistant y sugiere acciones basadas en el contexto histórico:

Entidad: {current_state['entity_id']}
Estado anterior: {old_state['state'] if old_state else 'None'}
Estado actual: {current_state['state']}
Atributos: {current_state['attributes']}

Contexto histórico:
{json.dumps(results, indent=2)}

Basado en estos datos, ¿qué acciones recomiendas? Responde en formato JSON con la siguiente estructura:
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