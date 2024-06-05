from langchain.tools import BaseTool
from langchain.chat_models import ChatOpenAI
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dataclasses import dataclass

@dataclass
class RagAgent:
    llm_model: str
    embedding_model: str 
    
    def load_documents(self, document_directory:str):
        loader = PyPDFDirectoryLoader(document_directory, silent_errors=True)
        documents = loader.load()
        return documents
        
     # Split documents
    def split_documents(self, document_directory: str):
        text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1500,
        chunk_overlap = 150
            )
        documents = self.load_documents(document_directory)
        return text_splitter.split_documents(documents)
    
    # Create Embeddings and store in vector db
    def store_embedding(self, split_documents, persist_directory: str)-> None:
        embeddings = SentenceTransformerEmbeddings(model_name=self.embedding_model)
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
        embeddings = SentenceTransformerEmbeddings(model_name=self.embedding_model)
        vector_db = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
        
        return vector_db
    
    def build_rag_agent(self, persist_directory: str='docs/chroma/'):
        vector_db = self.load_embedding(persist_directory)
        llm = ChatOpenAI(model_name=self.llm_model, temperature=0)

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
                    return_source_documents=True,
                    chain_type_kwargs={"prompt": qa_chain_prompt}
                )
        return qa_chain
    
    
    


        
    
    

