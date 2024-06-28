ARG PYTHON_VERSION
FROM python:${version}-slim-bookworm

WORKDIR /workspace
RUN pip install --upgrade pip \
    && apt-get update \
    && apt-get install -y \
        freetds-dev \
    && rm -rf /var/lib/apt/lists/*

# install requirements we exported from poetry
COPY build/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# copy project source
COPY . .
