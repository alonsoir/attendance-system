import re

from fpdf import FPDF, XPos, YPos
import asyncio
import os
import aiohttp
import ast
import random
from datetime import datetime

# Configuración de claves de API (asegúrate de configurarlas correctamente)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # Reemplaza con tu clave de API
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")  # Reemplaza con tu clave de API
JINA_API_KEY = os.getenv("JINA_API_KEY")  # Reemplaza con tu clave de API

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
SERPAPI_URL = "https://serpapi.com/search"
DEFAULT_MODELS = ["nvidia/llama-3.1-nemotron-70b-instruct:free",
                  "google/gemini-2.0-flash-thinking-exp:free",
                  "google/gemini-2.0-flash-thinking-exp-1219:free",
                  "google/gemini-2.0-flash-lite-preview-02-05:free",
                  "google/gemini-2.0-flash-exp:free",
                  "microsoft/phi-3-medium-128k-instruct:free",
                  "google/learnlm-1.5-pro-experimental:free",
                  "google/gemini-2.0-pro-exp-02-05:free",
                  "meta-llama/llama-3.2-90b-vision-instruct:free",
                  "meta-llama/llama-3.2-11b-vision-instruct:free",
                  "microsoft/phi-3-mini-128k-instruct:free",
                  "deepseek/deepseek-r1-distill-llama-70b:free",
                  "qwen/qwen2.5-vl-72b-instruct:free",
                  "meta-llama/llama-3.1-405b-instruct:free",
                  "meta-llama/llama-3.1-70b-instruct:free",
                  "mistralai/mistral-7b-instruct:free",
                  "meta-llama/llama-3.2-3b-instruct:free"]

# Función para elegir el modelo LLM
def select_model():
    print("Bienvenido a OpenDeepResearcher! Elige un modelo:")
    for i, model in enumerate(DEFAULT_MODELS):
        print(f"{i + 1}. {model}")

    while True:
        try:
            selection = int(input("Selecciona el número del modelo (o 0 para salir): "))
            if selection == 0:
                print("¡Hasta luego!")
                exit()
            elif 1 <= selection <= len(DEFAULT_MODELS):
                model_index = selection - 1
                print(f"Modelo seleccionado: {DEFAULT_MODELS[model_index]}")
                return model_index
            else:
                print("Selección no válida, intenta de nuevo.")
        except ValueError:
            print("Entrada no válida, por favor introduce un número.")

async def call_openrouter_async(session, messages, model_index, max_tokens=1024):
    if model_index >= len(DEFAULT_MODELS):
        print("No hay más modelos disponibles.")
        return None

    model = DEFAULT_MODELS[model_index]
    print(f"Modelo seleccionado: {model}")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "X-Title": "OpenDeepResearcher, by Matt Shumer, modified by Alonso Isidoro",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens
    }

    try:
        async with session.post(OPENROUTER_URL, headers=headers, json=payload) as resp:
            if resp.status == 200:
                result = await resp.json()
                return result.get('choices', [{}])[0].get('message', {}).get('content', None)
            else:
                print(f"El modelo {model} falló ({resp.status}). Intentando con el siguiente modelo...")
                return await call_openrouter_async(session, messages, model_index + 1, max_tokens)
    except Exception as e:
        print(f"Error al llamar al modelo {model}: {e}. Intentando con el siguiente modelo...")
        return await call_openrouter_async(session, messages, model_index + 1, max_tokens)

def safe_eval(response):
    try:
        return ast.literal_eval(response)
    except (SyntaxError, ValueError):
        print("El LLM no devolvió una lista Python válida. Respuesta:", response)
        return []

async def perform_search_async(session, query, model_index, retries=3):
    for attempt in range(retries):
        try:
            params = {"q": query, "api_key": SERPAPI_API_KEY, "engine": "google"}
            async with session.get(SERPAPI_URL, params=params) as resp:
                if resp.status == 200:
                    results = await resp.json()
                    return [item["link"] for item in results.get("organic_results", []) if "link" in item]
                print(f"Error de SERPAPI {resp.status}: {await resp.text()}")
        except Exception as e:
            print(f"Error al realizar búsqueda en SERPAPI: {e}")

        wait_time = 2 ** attempt + random.uniform(0, 1)
        print(f"Reintentando en {wait_time:.2f} segundos...")
        await asyncio.sleep(wait_time)

    return []

async def generate_final_report_async(session, user_query, all_contexts, model_index):
    context_combined = "\n".join(all_contexts)
    prompt = (
        "Eres un experto investigador. Basado en los contextos proporcionados, escribe un informe bien estructurado y detallado."
        "\n\nFormato: "
        "\n- Título"
        "\n- Introducción"
        "\n- Hallazgos clave (en puntos)"
        "\n- Conclusión"
    )
    messages = [
        {"role": "system", "content": "Eres un escritor de informes habilidoso."},
        {"role": "user", "content": f"Consulta del usuario: {user_query}\n\nContextos:\n{context_combined}\n\n{prompt}"}
    ]
    return await call_openrouter_async(session, messages, model_index)


# Función para crear el PDF con la consulta de investigación
def create_pdf(report, user_query, filename=None):
    pdf = FPDF()
    pdf.add_page()

    # Usamos una fuente TrueType (DejaVuSans) para soportar caracteres Unicode
    pdf.add_font("DejaVuSans", "", "DejaVuSans.ttf")
    pdf.set_font("DejaVuSans", size=12)

    # Si el reporte es None, lo reemplazamos por una cadena vacía
    if report is None:
        report = ""

    # Reemplazar guion largo y otros caracteres problemáticos
    report = report.replace("—", "-")  # Reemplaza guion largo por guion normal
    report = report.replace("“", '"').replace("”", '"')  # Reemplaza comillas
    report = report.replace("’", "'")  # Reemplaza comillas simples

    # Si no se proporciona un filename, generar uno automáticamente
    if filename is None:
        # Limpiar la consulta para usarla en el nombre del archivo
        clean_query = re.sub(r'\W+', '_', user_query)  # Reemplazar caracteres no alfanuméricos por guion bajo
        filename = f"Research_Report_{clean_query[:50]}.pdf"  # Limitar el nombre a los primeros 50 caracteres

    # Título del informe
    pdf.set_font("DejaVuSans", style='', size=16)
    pdf.cell(200, 10, text="Informe de Investigación", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    # Subtítulo con la consulta de investigación
    pdf.set_font("DejaVuSans", style='', size=12)
    pdf.cell(200, 10, text=f"Consulta: {user_query}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    # Fecha de creación del informe
    creation_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    pdf.cell(200, 10, text=f"Fecha de creación: {creation_date}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    # Deja una línea en blanco antes de mostrar el contenido del informe
    pdf.ln(10)

    # Contenido del informe
    pdf.set_font("DejaVuSans", size=12)
    pdf.multi_cell(0, 10, text=report)  # Soporta caracteres UTF-8

    # Guardar el PDF
    pdf.output(filename)
    print(f"Informe generado y guardado como {filename}.")

# Función para manejar el proceso de consulta y generación de informes
async def process_research_query(user_query, model_index):
    async with aiohttp.ClientSession() as session:
        # Llamada para obtener consultas de búsqueda
        search_queries = safe_eval(await call_openrouter_async(session, [
            {"role": "user", "content": f"Genera consultas de búsqueda para: {user_query}"}], model_index))
        tasks = {query: asyncio.create_task(perform_search_async(session, query, model_index)) for query in search_queries}

        all_contexts = []
        for query, task in tasks.items():
            try:
                search_results = await task
                print(f"Resultados para {query}: {len(search_results)} enlaces")
                contexts = await asyncio.gather(
                    *(call_openrouter_async(session, [{"role": "user", "content": f"Resume: {link}"}], model_index) for link in search_results))
                all_contexts.extend(contexts)
            except Exception as e:
                print(f"Error al obtener resultados para {query}: {e}")

        # Generar el informe final
        report = await generate_final_report_async(session, user_query, all_contexts, model_index)
        create_pdf(report, user_query)  # Pasar la consulta al PDF

if __name__ == "__main__":
    while True:
        model_index = select_model()

        user_query = input("Introduce tu consulta de investigación (o 'salir' para terminar): ")
        if user_query.lower() in ["salir", "exit"]:
            print("¡Hasta luego!")
            break

        asyncio.run(process_research_query(user_query, model_index))