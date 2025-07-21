# app/AI/ai.py

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain.memory import ConversationSummaryBufferMemory

# Global LLMs
llm = ChatOllama(model="llama3:8b")
embedding_model = OllamaEmbeddings(model="llama3:8b")

# Helper: create retriever from PDF
def create_retriever_from_pdf(pdf_path):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory="vector_db/cv_db"
    )

    return vector_db.as_retriever(search_kwargs={"k": 3})

# Helper: build prompt and memory-wrapped chain
def build_chain_with_memory(retriever):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that answers questions based on the provided context."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])

    memory = ConversationSummaryBufferMemory(
        memory_key="chat_history",
        max_token_limit=1000,
        llm=llm
    )

    chain = RunnableWithMessageHistory(
        prompt | llm,
        get_session_history=lambda session_id: memory.chat_memory,
        history_messages_key="chat_history",
        input_messages_key="input",
    )

    return chain

# Main: initialize chat with specific PDF
def initialize_pdf_chat(pdf_path, session_id):
    retriever = create_retriever_from_pdf(pdf_path)
    chain = build_chain_with_memory(retriever)
    return chain
