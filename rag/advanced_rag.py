import os
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings  # ← Importaciones actualizadas
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_community.tools import Tool


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
            print(f"Advertencia: No se encontró '{file}', será omitido.")

    documents = [doc for loader in loaders for doc in loader.load()]
    if not documents:
        raise ValueError("No se cargaron documentos. Verifica que los archivos existen.")
    return documents


def create_vectorstore(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Falta la variable de entorno OPENAI_API_KEY.")

    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    return FAISS.from_documents(texts, embeddings)


def create_web_search_tool():
    google_api_key = os.getenv("GOOGLE_API_KEY")
    google_cse_id = os.getenv("GOOGLE_CSE_ID")
    if not google_api_key or not google_cse_id:
        raise ValueError("Faltan GOOGLE_API_KEY o GOOGLE_CSE_ID en las variables de entorno.")

    search = GoogleSearchAPIWrapper(google_api_key=google_api_key, google_cse_id=google_cse_id)
    return Tool(name="Google Search", func=search.run, description="Búsqueda web con Google.")


def setup_rag():
    documents = load_documents()
    vectorstore = create_vectorstore(documents)
    retriever = vectorstore.as_retriever()
    web_search_tool = create_web_search_tool()

    # Usar ChatOpenAI para modelos de chat
    llm = ChatOpenAI(model_name="gpt-3.5-turbo")

    # Prompt optimizado para chat models
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
        chain_type_kwargs={"prompt": prompt_template}
    )

    return qa, web_search_tool


def answer_question(query, qa, web_search_tool):
    try:
        # Respuesta desde documentos locales
        local_response = qa.invoke({"query": query})
        document_answer = local_response["result"]

        # Respuesta desde búsqueda web
        web_answer = web_search_tool.run(query)

    except Exception as e:
        return f"Error al procesar la pregunta: {str(e)}"

    return (
        f"Respuesta basada en documentos:\n{document_answer}\n\n"
        f"Respuesta basada en web:\n{web_answer}"
    )


if __name__ == "__main__":
    try:
        qa, web_search_tool = setup_rag()
    except ValueError as e:
        print(f"Error en la configuración: {e}")
        exit(1)

    while True:
        query = input("\nPregunta: ")
        if query.lower() in ["salir", "exit", "quit"]:
            print("Saliendo...")
            break
        print("\n" + answer_question(query, qa, web_search_tool))