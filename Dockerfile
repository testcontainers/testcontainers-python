ARG version=3.8
FROM python:${version}

WORKDIR /workspace
ARG version=3.8
COPY requirements/${version}.txt requirements.txt
COPY setup.py README.rst ./
RUN pip install -r requirements.txt
COPY . .
