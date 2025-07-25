# app/AI/ai.py

import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.runnables import RunnableMap

# Global LLMs
llm = ChatOllama(model="llama3:8b")
embedding_model = OllamaEmbeddings(model="llama3:8b")

# Helper: create retriever from PDF
def create_retriever_from_pdf(pdf_path, pdf_id):
    persist_path = f"vector_db/pdf_{pdf_id}"

    if os.path.exists(persist_path):
        vector_db = Chroma(
            persist_directory=persist_path,
            embedding_function=embedding_model
        )
    else:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(documents)

        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_model,
            persist_directory=persist_path
        )
        # ❌ لا تستخدم vector_db.persist() هنا — لأنه مش لازم
        # لو محتاج تعمل persist، استخدم vector_db._collection.persist() ← لكن الأفضل تسيبه لأن Chroma بتعمل persist تلقائيًا
    return vector_db.as_retriever(search_kwargs={"k": 3})


# Helper: build prompt and memory-wrapped chain
def build_chain_with_memory(retriever):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that answers questions based on the provided context."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "Context:\n{context}\n\nQuestion:\n{input}")
    ])

    memory = ConversationSummaryBufferMemory(
        memory_key="chat_history",
        max_token_limit=1000,
        llm=llm
    )

    retrieval_chain = RunnableMap({
        "context": lambda x: retriever.invoke(x["input"]),
        "input": lambda x: x["input"],
        "chat_history": lambda x: x["chat_history"],  # ✅ مهم جدًا
    })

    chain = RunnableWithMessageHistory(
        retrieval_chain | prompt | llm,
        get_session_history=lambda session_id: memory.chat_memory,
        history_messages_key="chat_history",
        input_messages_key="input",
    )

    return chain


# Main: initialize chat with specific PDF
def initialize_pdf_chat(pdf_path, session_id, pdf_id):
    retriever = create_retriever_from_pdf(pdf_path, pdf_id)
    chain = build_chain_with_memory(retriever)
    return chain
