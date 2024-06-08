import argparse
from typing import List, Tuple
import uvicorn
from fastapi import FastAPI, Response, Request, HTTPException
from pydantic import BaseModel
import sys, os
import logging
from fastapi.middleware.cors import CORSMiddleware
from .rag_agent import RagAgent

llm_type = 'gpt-3.5-turbo'
embedding_llm_type = 'all-MiniLM-L6-v2'

agent_obj = RagAgent(llm_type, embedding_llm_type)
rag_qa_chain =  agent_obj.build_rag_agent()
app = FastAPI()

origins = [
    "*"
]

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
    chat_input: str
    chat_history: List[Tuple[str, str]]

@app.post("/chat")
async def chat(chat_input: Input)->dict:
    current_input = chat_input.chat_input
    result = rag_qa_chain({"query": current_input})
    return {"end": True, "output": result["result"]}

    
def start() -> None:
    parser = argparse.ArgumentParser(description="Rag Speech Chat Service")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Webservice Host (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Webservice port (default: 8000)"
    )
    args = parser.parse_args()

    uvicorn.run(
        "rag_speech_chat.app:app",
        host=args.host,
        port=args.port,
        log_level="info",
    )

