"""
Author: Ashok Kumar B
Date: 2025-10-06
Project: Katonic Platform Portal ChatBot
Module: Configuration Settings
Description: Global configuration settings for the RAG system
"""

DATABASE_NAME = "vectordb"
CONTAINER_NAME = "documents"
METADATA_CONTAINER_NAME = "metadata"


CHUNK_SIZE = 1024
CHUNK_OVERLAP = 180

EMBEDDING_MODEL = "text-embedding-ada-002" 
LLM_MODEL = "gpt-4-turbo-preview"
TEMPERATURE = 0.0

TOP_K_CHUNKS = 7

RAG_TEMPLATE = """You are a helpful assistant for the Katonic AI platform. Use the provided context to answer questions accurately and comprehensively.

Instructions:
- Answer based ONLY on the provided context
- Be specific and detailed when possible
- If the context contains version numbers, specifications, or technical details, include them
- If you don't find the answer in the context, say "I don't have enough information to answer that question"
- Provide relevant technical details and requirements when available

Context: {context}

Question: {question}

Answer:"""