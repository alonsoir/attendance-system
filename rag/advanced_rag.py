import os
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_community.tools import Tool

# Configurar consola bonita
from rich.console import Console
from rich.markdown import Markdown

console = Console()


def load_documents():
    files = ["AWS_Secure_Account_Setup.pdf", "ciberseguridad avanzado.pdf", "cheatsheet.md"]
    loaders = []
    for file in files:
        if os.path.exists(file):
            if file.endswith(".pdf"):
                loaders.append(PyPDFLoader(file))
            elif file.endswith(".md") or file.endswith(".txt"):
                loaders.append(TextLoader(file))
        else:
            console.print(f"[yellow]Advertencia:[/yellow] No se encontró '[bold]{file}[/bold]', será omitido.")

    documents = [doc for loader in loaders for doc in loader.load()]
    if not documents:
        raise ValueError("[red]Error crítico:[/red] No se cargaron documentos. Verifica que los archivos existen.")
    return documents


def create_vectorstore(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)

    if not (api_key := os.getenv("OPENAI_API_KEY")):
        raise ValueError("[red]Error:[/red] Faltan la variable de entorno OPENAI_API_KEY.")

    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    return FAISS.from_documents(texts, embeddings)


def create_web_search_tool():
    if not (google_api_key := os.getenv("GOOGLE_API_KEY")) or not (google_cse_id := os.getenv("GOOGLE_CSE_ID")):
        raise ValueError("[red]Error:[/red] Faltan GOOGLE_API_KEY o GOOGLE_CSE_ID en las variables de entorno.")

    search = GoogleSearchAPIWrapper(google_api_key=google_api_key, google_cse_id=google_cse_id)
    return Tool(name="Google Search", func=search.run, description="Búsqueda web con Google.")


def setup_rag():
    try:
        documents = load_documents()
        vectorstore = create_vectorstore(documents)
        retriever = vectorstore.as_retriever()
        web_search_tool = create_web_search_tool()

        llm = ChatOpenAI(model_name="gpt-3.5-turbo")

        prompt_template = PromptTemplate(
            template=(
                "Contexto:\n{context}\n\n"
                "Basado en el contexto anterior, responde esta pregunta:\n"
                "Pregunta: {question}\n\n"
                "Respuesta detallada:"
            ),
            input_variables=["context", "question"]
        )

        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            input_key="question",  # ← Define explícitamente la clave de entrada
            chain_type_kwargs={"prompt": prompt_template}
        )

        return qa, web_search_tool

    except Exception as e:
        console.print(f"\n[red]Error durante la configuración inicial:[/red]\n{str(e)}")
        exit(1)


def format_web_results(raw_results: str) -> str:
    """Formatea los resultados web crudos en una lista ordenada."""
    cleaned_entries = []
    for entry in raw_results.split("..."):
        entry = entry.strip()
        if entry and len(entry) > 40:  # Filtrar entradas muy cortas
            # Remover fechas falsas como "Dec 24, 2015"
            if any(mes in entry[:6] for mes in
                   ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
                entry = entry[13:].strip()
            cleaned_entries.append(entry)

    # Limitar a 5 resultados y formatear
    return "\n".join([f"• {entry}" for entry in cleaned_entries[:5]])


def answer_question(query: str, qa, web_search_tool):
    try:
        # Respuesta desde documentos locales
        console.print("\n[cyan]🔍 Procesando pregunta...[/cyan]")
        local_response = qa.invoke({"question": query})  # ← Usar invoke en lugar de __call__
        document_answer = local_response["result"]

        # Respuesta desde búsqueda web
        console.print("[green]🌐 Buscando en la web...[/green]")
        web_raw = web_search_tool.run(query)
        web_answer = format_web_results(web_raw)

        # Mostrar resultados formateados
        console.print("\n[bold blue]📄 Respuesta basada en documentos:[/bold blue]")
        console.print(Markdown(document_answer))

        console.print("\n[bold green]🌍 Resultados relevantes de la web:[/bold green]")
        console.print(Markdown(web_answer))
        console.print("\n" + "─" * 50)

    except Exception as e:
        console.print(f"\n[red]⛔ Error procesando la pregunta:[/red]\n{str(e)}")


if __name__ == "__main__":
    console.print("\n[bold magenta]🤖 Asistente de Seguridad Cibernética[/bold magenta]", justify="center")
    console.print("Escribe 'salir', 'exit' o 'quit' para terminar\n", justify="center")

    try:
        qa, web_search_tool = setup_rag()
    except Exception as e:
        console.print(f"\n[red]Error inicial:[/red] {str(e)}")
        exit(1)

    while True:
        try:
            query = console.input("\n[bold yellow]❓ Tu pregunta: [/bold yellow]")
            if query.lower() in {"salir", "exit", "quit"}:
                console.print("\n[bold magenta]👋 Sesión terminada. ¡Hasta pronto![/bold magenta]")
                break

            answer_question(query, qa, web_search_tool)

        except KeyboardInterrupt:
            console.print("\n[bold magenta]👋 Sesión interrumpida. ¡Hasta pronto![/bold magenta]")
            break