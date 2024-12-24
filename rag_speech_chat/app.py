"""This defines a single chat endpoint and the entry point of the service.
"""
import argparse
import logging
import os
from typing import List, Tuple

import uvicorn
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .rag_agent import RagAgent
from .utils import build_llm

llm_type = os.environ["LLM_TYPE"]
embedding_llm_type = os.environ["EMBEDDING_LLM_TYPE"]
persist_directory = os.environ["PERSIST_DIRECTORY"]
llm = build_llm(llm_type)

agent_obj = RagAgent(llm_type, embedding_llm_type)
rag_qa_chain = agent_obj.build_rag_agent(llm, persist_directory)
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
    level=logging.DEBUG,
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("rag-speech-chat-service")
logger.info("Initialization done! Agent is ready!")


class Input(BaseModel):
    """Input class made of current input and history.

    Attributes:
        chat_input: The current chat input.
        chat_history: History used tas memory.
    """

    chat_input: str
    chat_history: List[Tuple[str, str]]


@app.post("/chat")
async def chat(chat_input: Input) -> dict:
    """A chat post endpoint.

    Args:
        chat_input: A structure representing the current input and history.

    Returns:
        A dict of output.
    """
    current_input = chat_input.chat_input
    result = rag_qa_chain({"query": current_input})
    return {"end": True, "output": result["result"]}


@app.get("/status")
def status():
    return Response(
        content="App is up and running!"
    )

def start() -> None:
    """The start/entrypoint of service ."""
    parser = argparse.ArgumentParser(description="Rag Speech Chat Service")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Webservice Host (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Webservice port (default: 8000)",
    )
    args = parser.parse_args()

    uvicorn.run(
        "rag_speech_chat.app:app",
        host=args.host,
        port=args.port,
        log_level="info",
    )
