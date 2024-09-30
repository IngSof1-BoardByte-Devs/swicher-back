# Lógica de WebSockets
from fastapi import WebSocket
from app.websocket_manager import ConnectionManager

manager = ConnectionManager()

async def websocket_handler(websocket: WebSocket):
    # Conectar al grupo 0 por defecto
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Si el mensaje es un comando para unirse a una sala
            if data.startswith("/join "):
                # Extraer el game_id del mensaje
                game_id = int(data.split(" ", 1)[1])
                # Desconectar del grupo actual y conectar al nuevo
                await manager.move(websocket, 0, game_id)
            elif data.startswith("/leave"):
                # Extraer el game_id del mensaje
                game_id = int(data.split(" ", 1)[1])
                # Desconectar del grupo actual y conectar a la sala 0
                await manager.move(websocket, game_id, 0)
            else:
                await manager.broadcast(data, 0)
    except Exception as e:
        print(e)
    finally:
        # Desconectar del websocket cuando se cierra la conexión
        await manager.disconnect(websocket, 0)
