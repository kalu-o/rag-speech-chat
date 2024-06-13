"""This module handles creation of llm object from type.
"""
import os

from langchain_community.chat_models import ChatOpenAI

temperature = os.environ["TEMPERATURE"]


def build_llm(llm_type: str) -> ChatOpenAI:
    """Builds an llm object from an llm type.

    This is not limited to Openai but to other open source llms.
    Args:
        llm_type: A string indicating the llm used.

    Returns:
        An llm object.
    """
    llm = ChatOpenAI(model_name=llm_type, temperature=temperature)

    return llm
