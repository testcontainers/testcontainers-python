FROM python:3.6

COPY ./Pipfile* /workspace/
WORKDIR /workspace

RUN pip install pipenv && \
    pipenv install --system --dev --deploy

COPY . /workspace