ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}-slim-bookworm

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
RUN poetry install --all-extras --with dev --no-root

# copy project source
COPY . .

# install project with poetry
RUN poetry install --all-extras --with dev
