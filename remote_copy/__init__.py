from PhiLia093_Server.h import *

clients:set[websockets.ServerConnection] = set()

# 看上去消息处理函数是一个生命周期等同于ws连接的异步函数
async def wsrequest_handler(ws:websockets.ServerConnection, path:str = "/") -> None:
    #if 'remote_copy' in path:
        clients.add(ws)
        try:
            async for msg in ws:
                print(msg)
                if re.search(r'/report [a-zA-Z]{4}', str(msg)):
                    for client in list(clients):
                        code = str(msg[-4:])
                        if client is not ws:
                            await client.send(f"/join {code}")
        except Exception:
            pass
        finally:
            clients.remove(ws)
        return

async def start_server():
    return await websockets.serve(wsrequest_handler, "0.0.0.0", 52520)