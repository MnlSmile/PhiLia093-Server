import PhiLia093_Server.h
from PhiLia093_Server.h import *

import remote_copy

import asyncio
import fastapi

app = fastapi.FastAPI()

async def main() -> None:
    server = await remote_copy.start_server()
    try:
        await asyncio.Future()
    finally:
        server.close()
        await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())