"""
Author: Ashok Kumar B
Date: 2025-10-06
Project: Katonic Platform Portal ChatBot
Module: Embedding Service
Description: OpenAI embedding model service for text vectorization
"""

from langchain_openai import OpenAIEmbeddings
from . import settings

def create_embeddings_model(api_key):
    return OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        openai_api_key=api_key
    )