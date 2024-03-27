import logging

from langchain.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

from myexpertchat.config import settings
from myexpertchat.db import get_db_connection
# from langchain.globals import set_debug

# set_debug(True)
# Lazy load chain
CHAIN = None

log = logging.getLogger(__name__)


def build_llm():
    llm = LlamaCpp(
        model_path=settings.llm_model_file,
        f16_kv=True,  # MUST set to True, otherwise you will run into problem after a couple of calls
        verbose=True,
        n_ctx=1200,  # must be big enough to allow text snippets for context
    )
    return llm


def build_prompt():
    prompt_template = """
    <|system|>
    Using the information contained in the context, 
    give a comprehensive answer to the question.
    If the answer is contained in the context, also report the source URL.
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


def build_rag_chain():
    prompt = build_prompt()
    llm = build_llm()

    db = get_db_connection()
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        # | llm
        | StrOutputParser()
    )
    return chain


def get_answer_from_rag(question: str) -> str:
    global CHAIN
    if CHAIN is None:
        CHAIN = build_rag_chain()
    log.info(f"running query: {question}")
    response = CHAIN.invoke(question)
    return response
