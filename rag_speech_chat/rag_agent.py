"""The RagAgent class that handles creation of embeddings and retrieval.
"""
import os
from dataclasses import dataclass
from typing import List

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

chunk_size = (os.environ["CHUNK_SIZE"],)
chunk_overlap = os.environ["CHUNK_OVERLAP"]
return_source_documents = os.environ["RETURN_SOURCE_DOCUMENTS"]


@dataclass
class RagAgent:
    """For creating chat systems based on retrieval augmented generation.

    Attributes:
        llm_type: A string indicating llm used.
        embedding_llm_type: A string indicating llm used for embedding.
    """

    llm_type: str
    embedding_llm_type: str

    def load_documents(self, document_directory: str) -> List[Document]:
        """Loads the pdf documents.

        Args:
            document_directory: Specifies full path to the document directory.

        Returns:
            A list of Document objects.
        """
        loader = PyPDFDirectoryLoader(document_directory, silent_errors=True)
        documents = loader.load()
        return documents

    def split_documents(self, document_directory: str) -> List[Document]:
        """Recursively splits documents into chunks.

        Args:
            document_directory: Specifies full path to the document directory.

        Returns:
            A list of Document objects.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        documents = self.load_documents(document_directory)
        return text_splitter.split_documents(documents)

    def store_embedding(
        self, split_document: List[Document], persist_directory: str
    ) -> None:
        """Creates embeddings and stores in a vector database.

        Args:
            split_document: List of split documents.
            persist_directory: Directory to store embeddings.
        """
        embeddings = SentenceTransformerEmbeddings(
            model_name=self.embedding_llm_type
        )
        vector_db = Chroma.from_documents(
            documents=split_document,
            embedding=embeddings,
            persist_directory=persist_directory,
        )
        vector_db.persist()

    def create_embedding(
        self, document_directory: str, persist_directory: str
    ) -> None:
        """Creates embeddings from pdfs and stores in a vector database.

        Args:
            document_directory: Full path to the pdf directory.
            persist_directory: Directory to store embeddings.
        """
        split_document = self.split_documents(document_directory)
        self.store_embedding(split_document, persist_directory)

    def load_embedding(self, persist_directory: str) -> Chroma:
        """Loads embeddings a vector database.

        Args:
            persist_directory: Directory containing the embeddings.

        Returns:
            A vector database.
        """
        embeddings = SentenceTransformerEmbeddings(
            model_name=self.embedding_llm_type
        )
        vector_db = Chroma(
            persist_directory=persist_directory, embedding_function=embeddings
        )

        return vector_db

    def build_rag_agent(
        self, llm: ChatOpenAI, persist_directory: str = "/tmp"
    ):
        """Builds a RAG chat agent.

        Args:
            llm: The llm object.
            persist_directory: Directory containing the embeddings.

        Returns:
            A QA chain.
        """
        vector_db = self.load_embedding(persist_directory)

        template = """You are AskFlow, an AI-Powered Knowledge Assistant.
                      When users greet you with phrases like 'Hello,' 'Hi,'
                      'Bye,' or 'Talk to you again,' respond warmly and politely. 
                      Use variations such as:
                      'Hello! How can I assist you today?'
                      'Hi there! What would you like to know?'
                      'Goodbye! Have a wonderful day!'
                      'Talk to you again soon! Take care!'  

                      Use the following context elements to answer the question at
                      the end. Always be polite. If you don't know the answer,
                      just say you don't know and don't try to make up an
                      answer. Use a maximum of three sentences. Keep the
                      answer as concise as possible. 
                    {context}
                    Question: {question}
                    Helpful Answer:"""
        qa_chain_prompt = PromptTemplate.from_template(template)
        qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=vector_db.as_retriever(search_type="mmr"),
            return_source_documents=return_source_documents,
            chain_type_kwargs={"prompt": qa_chain_prompt},
        )
        return qa_chain
