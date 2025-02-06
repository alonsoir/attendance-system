import asyncio
import os

import aiohttp
import ast
import random

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")# Replace with your OpenRouter API key
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY") # Replace with your SERPAPI API key
JINA_API_KEY = os.getenv("JINA_API_KEY") # Replace with your JINA API key

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
SERPAPI_URL = "https://serpapi.com/search"
DEFAULT_MODELS = ["nvidia/llama-3.1-nemotron-70b-instruct:free", "google/gemini-2.0-flash-thinking-exp:free"]


async def call_openrouter_async(session, messages, model_index=0, max_tokens=1024):
    if model_index >= len(DEFAULT_MODELS):
        print("❌ No more models to try.")
        return None

    model = DEFAULT_MODELS[model_index]
    print(f"✅ Model {model} selected.")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "X-Title": "OpenDeepResearcher, by Matt Shumer",
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
                print(f"⚠️ Model {model} failed ({resp.status}). Trying next model...")
                return await call_openrouter_async(session, messages, model_index + 1)
    except Exception as e:
        print(f"❌ Error calling model {model}: {e}. Trying next model...")
        return await call_openrouter_async(session, messages, model_index + 1)


def safe_eval(response):
    try:
        return ast.literal_eval(response)
    except (SyntaxError, ValueError):
        print("⚠️ LLM did not return a valid Python list. Response:", response)
        return []


async def perform_search_async(session, query, retries=3):
    for attempt in range(retries):
        try:
            params = {"q": query, "api_key": SERPAPI_API_KEY, "engine": "google"}
            async with session.get(SERPAPI_URL, params=params) as resp:
                if resp.status == 200:
                    results = await resp.json()
                    return [item["link"] for item in results.get("organic_results", []) if "link" in item]
                print(f"⚠️ SERPAPI error {resp.status}: {await resp.text()}")
        except Exception as e:
            print(f"❌ Error performing SERPAPI search: {e}")

        wait_time = 2 ** attempt + random.uniform(0, 1)
        print(f"🔄 Retrying in {wait_time:.2f} seconds...")
        await asyncio.sleep(wait_time)

    return []


async def generate_final_report_async(session, user_query, all_contexts):
    context_combined = "\n".join(all_contexts)
    prompt = (
        "You are an expert researcher. Based on the contexts provided, write a well-structured, detailed report."
        "\n\nFormat it with:"
        "\n- Title"
        "\n- Introduction"
        "\n- Key Findings (bullet points)"
        "\n- Conclusion"
    )
    messages = [
        {"role": "system", "content": "You are a skilled report writer."},
        {"role": "user", "content": f"User Query: {user_query}\n\nContexts:\n{context_combined}\n\n{prompt}"}
    ]
    return await call_openrouter_async(session, messages)


async def process_research_query(user_query):
    async with aiohttp.ClientSession() as session:
        search_queries = safe_eval(await call_openrouter_async(session, [
            {"role": "user", "content": f"Generate search queries for: {user_query}"}]))
        tasks = {query: asyncio.create_task(perform_search_async(session, query)) for query in search_queries}

        all_contexts = []
        for query, task in tasks.items():
            try:
                search_results = await task
                print(f"✅ Results for {query}: {len(search_results)} links")
                contexts = await asyncio.gather(
                    *(call_openrouter_async(session, [{"role": "user", "content": f"Summarize: {link}"}]) for link in
                      search_results))
                all_contexts.extend(contexts)
            except Exception as e:
                print(f"❌ Error fetching results for {query}: {e}")

        report = await generate_final_report_async(session, user_query, all_contexts)
        return report


if __name__ == "__main__":
    user_query = "What is the impact of AI in healthcare?"
    result = asyncio.run(process_research_query(user_query))
    print("\n📝 Final Report:\n", result)
