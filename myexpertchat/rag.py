import logging
import os

from langchain.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from myexpertchat.config import settings
from myexpertchat.db import get_db_connection

# Lazy load chain, initialize to None.
CHAIN = None

log = logging.getLogger(__name__)


def build_llm():
    """Wrpper function that creates a LLM step that can be used in chain.
    
    Lazy load model file if URL is given in settings and file is missing. Otherwise fail. 

    Returns:
        TODO: Add type. Fully initialised LLM model.
    """
    model_file = settings.llm_model_file

    if not os.path.isfile(model_file):
        model_url = settings.llm_model_url
        if settings.llm_model_url is None:
            raise ValueError(f"LLM model file missing in {model_file} and no URL to download from given in {model_url}")
        else:
            log.info("Downloading LLM model from {model_url} to {model_file}")
            raise NotImplementedError()

    llm = LlamaCpp(
        model_path=model_file,
        f16_kv=True,  # MUST set to True, otherwise you will run into problem after a couple of calls
        verbose=True,
        n_ctx=1200,  # must be big enough to allow text snippets for context
        n_threads=settings.llm_n_threads,
    )
    return llm


def build_prompt():
    """Create prompt step from generic template.

    Returns:
        TODO: Add type, that can be used directly as step in chain.

    TODO: Include the prompt part below once we retrieve metadata.
    Take note of the sources and include them in the answer in the format: "SOURCES: source1 source2", use "SOURCES" in 
    capital letters regardless of the number of sources.
    """

    prompt_template = """
    <|system|>
    You are a service agent who aggregates knowledge coming from a large number of text sources. 
    Using the information contained in the context, give a concise answer to the question.
    If the answer cannot be deduced from the context, do not give an answer.

    </s>

    <|user|>
    Context: 
    {context}

    Question:
    {question}
    </s>

    <|assistant|>

    """
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=prompt_template,
    )
    return prompt


def build_rag_chain() -> str:
    """Create chain that converts question, looks up context and passes it to LLM to sommarize.

    Returns:
        String output from LLM.
    """
    prompt = build_prompt()
    llm = build_llm()

    db = get_db_connection()
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
    return chain


def get_answer_from_rag(question: str) -> str:
    """End-to-end wrapper to initialise and run RAG chain.

    Please note: RAG chain is initialised lazily at runtime.

    Args:
        question: User question.

    Returns:
        String with answer to question from RAG chain.
    """
    global CHAIN
    if CHAIN is None:
        CHAIN = build_rag_chain()
    log.info(f"running query: {question}")
    response = CHAIN.invoke(question)
    return response