import time

from fastapi import FastAPI

app = FastAPI()


@app.get("/order")
def order():
    time.sleep(3)
    return {"order_id": "12345", "status": "confirmed"}


@app.get("/health")
def health():
    return {"status": "healthy"}