"""
Author: Ashok Kumar B
Date: 2025-10-06
Project: Katonic Platform Portal ChatBot
Module: Text Chunking Utilities
Description: Text splitting and chunking utilities for document processing
"""


from langchain.text_splitter import RecursiveCharacterTextSplitter
from . import settings

def create_text_splitter(
    chunk_size: int = settings.CHUNK_SIZE,
    chunk_overlap: int = settings.CHUNK_OVERLAP
):
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
        keep_separator=True
    )

def split_into_chunks(text, text_splitter=None):
    if text_splitter is None:
        text_splitter = create_text_splitter()
    return text_splitter.split_text(text)