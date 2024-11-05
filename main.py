import uvicorn
from fastapi import Response
from prometheus_client import generate_latest

from app.auto_app import create_app
from app.config import settings

app = create_app(settings)


@app.get("/metrics")
async def metrics():
    return Response(generate_latest())


if __name__ == "__main__":
    uvicorn.run(app, port=8080)
