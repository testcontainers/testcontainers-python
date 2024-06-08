from fastapi import FastAPI

app = FastAPI()


@app.get("/api/v1/")
def read_root():
    return {"Status": "Working"}
