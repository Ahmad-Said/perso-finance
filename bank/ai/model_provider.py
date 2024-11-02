from langchain_ollama import ChatOllama

from const.const_gl import ConstGl


def get_model():
    return ChatOllama(
        model=ConstGl.AI_OLLAMA_MODEL,
        temperature=0,
        base_url=ConstGl.AI_OLLAMA_BASE_URL
    )