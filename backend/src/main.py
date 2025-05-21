import asyncio
from uvicorn import Config, Server
from app.app import create_app


async def main():
    app = create_app()
    config = Config(app, host="0.0.0.0", port=8000)
    server = Server(config)
    await server.serve()


if __name__ == '__main__':
    asyncio.run(main())
