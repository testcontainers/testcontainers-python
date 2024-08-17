FROM python:3.9

WORKDIR /app

RUN pip install fastapi[standard]

COPY ./app /app

EXPOSE 80

CMD ["fastapi", "run", "main.py", "--port", "80"]
