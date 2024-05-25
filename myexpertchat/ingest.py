"""
This module is intended to be run as a standalone server. The server provides an endpoint for submitting text, which
will be processed and snippets stored in a vector db.

The development server can be started with:
    flask --app ingest.py run

This provides an endpoint at localhost:5000/inserttext/ that receives POST requests with a
payload like:
{
    "text": "Some long text, e.g. a wiki page"
    "metadata": {"URL": "https://..."}
}

The dict provided for metadata can have any key/value pairs, which then get stored in the vector DB.
"""

import logging
from typing import Any

from flask import Flask, request
from langchain_text_splitters import SentenceTransformersTokenTextSplitter

from myexpertchat.config import settings
from myexpertchat.db import get_db_connection

log = logging.getLogger(__name__)


def insert_text(text: str, metadata: dict[str, str]):
    """Process text by cutting it into snippets and attach metadata to each snippet.

    Args:
        text: Any long text that should be inserted into the database. 
        metadata: A dict of strings like {"URL": "https://..."}.
    """
    text_splitter = SentenceTransformersTokenTextSplitter(model_name=settings.embedding_model)

    text_snippets = text_splitter.split_text(text)
    metadata_list = [metadata] * len(text_snippets)

    db = get_db_connection()
    db.add_texts(text_snippets, metadata_list)


app = Flask(__name__)


@app.route("/inserttext", methods=["POST"])
def insert_text_endpoint():
    """Flask wrapper that unpacks request and processes data."""
    payload = request.get_json()
    insert_text(payload["text"], payload["metadata"])
    return "Success", 200
