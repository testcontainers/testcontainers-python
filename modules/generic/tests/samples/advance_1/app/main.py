# This app will use redis to store given key-value pairs.

import os
import redis

from fastapi import FastAPI


app = FastAPI()

redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_client = redis.Redis(host=redis_host, port=redis_port)
redis_client.ping()


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.get("/get/{key}")
def read_item(key: str):
    return {key: redis_client.get(key)}


@app.post("/set")
def create_item(key: str, value: str):
    redis_client.set(key, value)
    return {key: value}
