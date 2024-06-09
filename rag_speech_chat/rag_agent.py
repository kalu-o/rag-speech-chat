from langchain.tools import BaseTool
from langchain.chat_models import ChatOpenAI
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dataclasses import dataclass
import os

chunk_size = os.environ['CHUNK_SIZE'],
chunk_overlap = os.environ['CHUNK_OVERLAP']
return_source_documents = os.environ['RETURN_SOURCE_DOCUMENTS']

@dataclass
class RagAgent:
    llm_type: str
    embedding_llm_type: str 
    
    def load_documents(self, document_directory:str):
        loader = PyPDFDirectoryLoader(document_directory, silent_errors=True)
        documents = loader.load()
        return documents
        
     # Split documents
    def split_documents(self, document_directory: str):
        text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap
            )
        documents = self.load_documents(document_directory)
        return text_splitter.split_documents(documents)
    
    # Create Embeddings and store in vector db
    def store_embedding(self, split_documents, persist_directory: str)-> None:
        embeddings = SentenceTransformerEmbeddings(model_name=self.embedding_llm_type)
        vector_db = Chroma.from_documents(
            documents = split_documents,
            embedding=embeddings,
            persist_directory=persist_directory
            )
        vector_db.persist()

    
    def create_embedding(self, document_directory: str, persist_directory: str)->None:
        split_documents = self.split_documents(document_directory)
        self.store_embedding(split_documents, persist_directory)


    # Create Embeddings and store in vector db
    def load_embedding(self, persist_directory: str)->None:
        embeddings = SentenceTransformerEmbeddings(model_name=self.embedding_llm_type)
        vector_db = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
        
        return vector_db
    
    def build_rag_agent(self, llm, persist_directory: str='docs/chroma/'):
        vector_db = self.load_embedding(persist_directory)

        template = """Use the following context elements to answer the question at the end.
                        If you don't know the answer, just say you don't know and don't try to make up an answer.
                        Use a maximum of three sentences. Keep the answer as concise as possible. Always be polite. 
                    {context}
                    Question: {question}
                    Helpful Answer:"""
        qa_chain_prompt = PromptTemplate.from_template(template)
        qa_chain = RetrievalQA.from_chain_type(
                    llm,
                    retriever=vector_db.as_retriever(search_type = "mmr"),
                    return_source_documents=return_source_documents,
                    chain_type_kwargs={"prompt": qa_chain_prompt}
                )
        return qa_chain
    
    
    


        
    
    

