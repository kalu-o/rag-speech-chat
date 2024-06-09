from langchain.chat_models import ChatOpenAI

RETURN_SOURCE_DOCUMENTS=True
VECTOR_COUNT=2
CHUNK_SIZE=1500
CHUNK_OVERLAP=150
PERSIST_DIRECTORY='/data/chroma'
LLM_TYPE='gpt-3.5-turbo'
EMBEDDING_LLM_TYPE='all-MiniLM-L6-v2'
TEMPERATURE=0.01

def build_llm(llm_type: str):
    llm = ChatOpenAI(model_name=llm_type, temperature=TEMPERATURE)

    return llm
