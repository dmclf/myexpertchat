import os
os.environ['HF_HOME'] = '/data/huggingface/'
from langchain_community.llms import LlamaCpp
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate

import weaviate
import weaviate.classes as wvc
from langchain_community.vectorstores import Weaviate
from langchain_community.embeddings import HuggingFaceEmbeddings

client = weaviate.Client("http://localhost:8080")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = Weaviate(client=client, index_name="Test2", text_key="text", embedding=embeddings, by_text=False)

llm = LlamaCpp(

    # model_path="/data/llm/zephyr-7b-beta.Q4_K_M.gguf",
    # model_path="/data/llm/zephyr-7b-beta.Q8_0.gguf",
    model_path="/data/llm/tinyllama-1.1b-chat-v0.3.Q8_0.gguf",
    f16_kv=True,  # MUST set to True, otherwise you will run into problem after a couple of calls
    verbose=True,
    n_ctx=1200,
)
# llm.invoke("What is Hong Kong?")
prompt_template = """
<|system|>
Answer the question based only on the following context to help:

{context}

</s>
<|user|>
{question}
</s>
<|assistant|>

"""
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=prompt_template,
)
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
chain.invoke("When was Hong Kong founded?")
