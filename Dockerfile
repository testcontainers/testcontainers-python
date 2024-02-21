ARG version=3.8
FROM python:${version}

WORKDIR /workspace
RUN pip install --upgrade pip \
    && apt-get update \
    && apt-get install -y \
        freetds-dev \
    && rm -rf /var/lib/apt/lists/*
COPY build/requirements.txt requirements.txt
COPY setup.py README.rst ./
RUN pip install -r requirements.txt
COPY . .
