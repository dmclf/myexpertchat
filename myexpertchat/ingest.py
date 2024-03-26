import os
os.environ['HF_HOME'] = '/data/huggingface/'

from langchain_text_splitters import SentenceTransformersTokenTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
import weaviate
import weaviate.classes as wvc
from langchain_community.vectorstores import Weaviate

# embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", model_kwargs = {"device": "cuda"})
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

text_splitter = SentenceTransformersTokenTextSplitter(model_name="all-MiniLM-L6-v2")

split_texts = []
metadata = []
for filename in ["../assets/london.txt", "../assets/hong_kong.txt"]:
    with open(filename) as f:
        text = f.read()
        split_text = text_splitter.split_text(text)
        metadata += [{"filename": filename}] * len(split_text)
        split_texts += split_text


# client = weaviate.connect_to_local()
client = weaviate.Client("http://localhost:8080")
db = Weaviate.from_texts(split_texts, embeddings, metadata, client=client, by_text=False, index_name="Test2")