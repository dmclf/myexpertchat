FROM python:3.10-slim

ARG USERNAME=user
# Hardcoding user 1000:1000 as this is the default WSL UID.
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && mkdir -p /data \
    && chown $USERNAME /data

WORKDIR /app

ENV POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local'

RUN apt-get update && apt-get install -y build-essential cmake curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 -
    

COPY myexpertchat myexpertchat 
COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-cache --without dev
# https://github.com/nicolas-van/multirun
RUN curl -sSL https://github.com/nicolas-van/multirun/releases/download/1.1.3/multirun-x86_64-linux-gnu-1.1.3.tar.gz | tar -xz && \
    mv multirun /bin

EXPOSE 8000 8510

USER $USERNAME
