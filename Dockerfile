ARG version=3.8
FROM python:${version}

WORKDIR /workspace
ARG version=3.8
RUN apt-get update && apt-get install -y --no-install-recommends unixodbc-dev \
  && rm -rf /var/lib/apt/lists/*
COPY requirements/${version}.txt requirements.txt
COPY setup.py README.rst ./
RUN pip install -r requirements.txt
COPY . .
