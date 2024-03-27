from typing import Any
import weaviate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Weaviate

from myexpertchat.config import settings


def get_db_connection():
    """Connect to vector database and apply Langchain wrapper

    Returns:
        Langchain vector database connection wrapper.
    """
    client = weaviate.Client(settings.weaviate_url)
    embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
    db = Weaviate(client=client, index_name=settings.weaviate_collection, text_key="text", embedding=embeddings, by_text=False)
    return db