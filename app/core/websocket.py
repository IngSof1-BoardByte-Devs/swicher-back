# Lógica de WebSockets
from fastapi import WebSocket
from app.websocket_manager import ConnectionManager

manager = ConnectionManager()

async def websocket_handler(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client says: {data}")
    except Exception as e:
        print(e)
    finally:
        await manager.disconnect(websocket)
