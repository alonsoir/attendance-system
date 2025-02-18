import asyncio
import websockets
import json
import ollama
import sqlite3
from datetime import datetime
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

# Configuración de Home Assistant
HA_URL = "ws://localhost:8123/api/websocket"
HA_TOKEN = "TU_TOKEN_AQUI"

# Inicializar base de datos vectorial
pc = Pinecone(api_key="TU_PINECONE_API_KEY")
index = pc.Index("home-assistant-states")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Base de datos SQLite para estados recientes
conn = sqlite3.connect("home_assistant_states.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS device_states (
        entity_id TEXT PRIMARY KEY,
        state TEXT,
        last_updated TEXT
    )
""")
conn.commit()


async def store_state(entity_id, state):
    timestamp = datetime.utcnow().isoformat()
    cursor.execute("REPLACE INTO device_states VALUES (?, ?, ?)", (entity_id, state, timestamp))
    conn.commit()

    vector = model.encode(f"{entity_id} {state}").tolist()
    index.upsert(vectors=[{"id": entity_id, "values": vector}])


async def send_to_ha(ws, message):
    await ws.send(json.dumps(message))
    response = await ws.recv()
    return json.loads(response)


async def connect_to_ha():
    async with websockets.connect(HA_URL) as ws:
        print("🔗 Conectando a Home Assistant...")
        await send_to_ha(ws, {"type": "auth", "access_token": HA_TOKEN})
        await send_to_ha(ws, {"id": 1, "type": "subscribe_events", "event_type": "state_changed"})
        print("✅ Conectado. Escuchando eventos...")

        while True:
            message = await ws.recv()
            event = json.loads(message)
            entity_id = event.get("event", {}).get("data", {}).get("entity_id", "")
            new_state = event.get("event", {}).get("data", {}).get("new_state", {}).get("state", "")

            if entity_id and new_state:
                print(f"📡 Evento: {entity_id} -> {new_state}")
                await store_state(entity_id, new_state)

                response = ollama.chat(model="mistral", messages=[
                    {"role": "system",
                     "content": "Eres un asistente domótico. Responde con acciones de Home Assistant cuando sea posible."},
                    {"role": "user", "content": f"El estado de {entity_id} cambió a {new_state}. ¿Qué hago?"}
                ])
                action = response["message"]["content"]
                print(f"🤖 Respuesta del LLM: {action}")

                if "enciende" in action.lower():
                    await send_to_ha(ws, {
                        "id": 2, "type": "call_service",
                        "domain": "light", "service": "turn_on",
                        "service_data": {"entity_id": entity_id}
                    })


asyncio.run(connect_to_ha())
