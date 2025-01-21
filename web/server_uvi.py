import uvicorn

from .main import app


def start_server(host: str = "127.0.0.1", port: int = 2380):
    uvicorn.run(app=app, host=host, port=port)
