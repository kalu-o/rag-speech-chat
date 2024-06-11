from rag_agent import RagAgent

"""Sample script that can be used to generate embeddings.
"""
document_directory = ""
persist_directory = ""
llm_model = "gpt-3.5-turbo"
embeddings_model = "all-MiniLM-L6-v2"

agent_obj = RagAgent(llm_model, embeddings_model)
agent_obj.create_embedding(document_directory, persist_directory)
