ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}-slim-bookworm
ARG POETRY_EXTRAS

ENV PYTHONPATH=/workspace

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /workspace
RUN pip install --upgrade pip \
    && apt-get update \
    && apt-get install -y freetds-dev \
    && apt-get install -y make \
    # no real need for keeping this image small at the moment
    && :; # rm -rf /var/lib/apt/lists/*

# install poetry
RUN bash -c 'python -m venv /opt/poetry-venv && source $_/bin/activate && pip install poetry && ln -s $(which poetry) /usr/bin'

# install dependencies with poetry
COPY pyproject.toml .
COPY poetry.lock .
RUN if [ "$POETRY_EXTRAS" = "" ]; then \
        poetry install --all-extras --with dev --no-root; \
    else \
        poetry install --extras "$POETRY_EXTRAS" --with dev --no-root; \
    fi

# copy project source
COPY . .

# install project with poetry
RUN if [ "$POETRY_EXTRAS" = "" ]; then \
        poetry install --all-extras --with dev; \
    else \
        poetry install --extras "$POETRY_EXTRAS" --with dev; \
    fi
