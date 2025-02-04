# app/main.py
import os
import autogen
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar cliente de Qdrant
qdrant_client = QdrantClient(
    url="http://vectordb:6333",
)

# Configurar el config del LLM
config_list = [
    {
        'model': 'gpt-4',  # O el modelo que prefieras usar
        'api_key': os.getenv('OPENAI_API_KEY'),
    }
]

# Configurar los agentes
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={"config_list": config_list},
    system_message="Eres un asistente experto en análisis de datos."
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    system_message="Eres un proxy que ayuda a coordinar tareas de análisis."
)


def store_interaction(query, response, collection_name="interactions"):
    """Almacena las interacciones en la base vectorial para aprendizaje"""
    qdrant_client.upsert(
        collection_name=collection_name,
        points=[
            {
                "id": hash(f"{query}{response}"),
                "payload": {
                    "query": query,
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                },
                "vector": get_embedding(f"{query} {response}")  # Implementar get_embedding
            }
        ]
    )


def process_task(task_description: str):
    """Procesa una tarea usando los agentes"""
    # Iniciar conversación entre agentes
    chat_result = user_proxy.initiate_chat(
        assistant,
        message=task_description
    )

    # Almacenar la interacción para aprendizaje
    store_interaction(task_description, str(chat_result))

    return chat_result


if __name__ == "__main__":
    # Ejemplo de uso
    task = "Analiza los patrones de ventas del último trimestre"
    result = process_task(task)
    print(f"Resultado: {result}")