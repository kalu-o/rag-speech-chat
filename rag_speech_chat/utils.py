from langchain_community.chat_models import ChatOpenAI
import os

temperature = os.environ['TEMPERATURE']

def build_llm(llm_type: str):
    llm = ChatOpenAI(model_name=llm_type, temperature=temperature)

    return llm
