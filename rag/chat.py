import os

from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
# Importaciones actualizadas a la nueva ubicación en langchain_community
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAI
from langchain_openai import OpenAIEmbeddings

# Configura tu clave de API para OpenAI
os.environ["OPENAI_API_KEY"] = "USE_YOUR_OWN_API_KEY"


# Función para cargar documentos PDF y Markdown
def cargar_documentos(pdf_paths=[], md_paths=[]):
    documentos = []

    # Cargar PDFs
    for pdf_path in pdf_paths:
        try:
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            documentos.extend(docs)
            print(f"Cargado PDF: {pdf_path}")
        except Exception as e:
            print(f"Error cargando {pdf_path}: {e}")

    # Cargar archivos Markdown
    for md_path in md_paths:
        try:
            loader = TextLoader(md_path, encoding="utf-8")
            docs = loader.load()
            documentos.extend(docs)
            print(f"Cargado Markdown: {md_path}")
        except Exception as e:
            print(f"Error cargando {md_path}: {e}")

    return documentos


# Especifica las rutas de tus ficheros
rutas_pdf = ["AWS_Secure_Account_Setup.pdf", "ciberseguridad avanzado.pdf"]
rutas_md = ["cheatsheet.md"]

# Cargar documentos
docs = cargar_documentos(pdf_paths=rutas_pdf, md_paths=rutas_md)

# Dividir los documentos en fragmentos para mejorar la búsqueda
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
fragmentos = text_splitter.split_documents(docs)

# Crear embeddings y construir el índice vectorial (utilizando FAISS)
embeddings = OpenAIEmbeddings()
vector_store = FAISS.from_documents(fragmentos, embeddings)

# Crear un retriever a partir del índice
retriever = vector_store.as_retriever()

# Configurar el LLM y el pipeline de RetrievalQA
llm = OpenAI(temperature=0)
qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)
# Bucle de interacción para hacer preguntas y mostrar los orígenes
print("Sistema RAG iniciado. Escribe 'salir' para terminar.")
while True:
    consulta = input("\nPregunta: ")
    if consulta.lower() in ["salir", "exit", "quit"]:
        break

    # Usar el método invoke para evitar la deprecación
    resultado = qa.invoke({"query": consulta})
    respuesta = resultado["result"]
    docs_fuente = resultado["source_documents"]

    print("Respuesta:", respuesta)
    print("\nOrígenes utilizados:")
    for doc in docs_fuente:
        metadatos = doc.metadata if hasattr(doc, "metadata") else {}
        contenido_resumen = doc.page_content[:200]  # Un resumen del contenido
        print("-" * 40)
        print("Metadatos:", metadatos)
        print("Fragmento:", contenido_resumen)
