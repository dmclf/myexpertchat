import logging
from typing import Any

from flask import Flask, request
from langchain_text_splitters import SentenceTransformersTokenTextSplitter

from myexpertchat.config import settings
from myexpertchat.db import get_db_connection

log = logging.getLogger(__name__)


def insert_text(text: str, metadata: dict[str, Any]):
    text_splitter = SentenceTransformersTokenTextSplitter(model_name=settings.embedding_model)

    text_snippets = text_splitter.split_text(text)
    metadata_list = [metadata] * len(text_snippets)

    db = get_db_connection()
    db.add_texts(text_snippets, metadata_list)

app = Flask(__name__)

@app.route("/inserttext", methods=["POST"])
def insert_text_endpoint():
    payload = request.get_json()
    insert_text(payload["text"], payload["metadata"])
    return "Success", 200