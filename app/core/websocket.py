# Lógica de WebSockets
from fastapi import WebSocket
from app.websocket_manager import ConnectionManager

manager = ConnectionManager()

async def websocket_handler(websocket: WebSocket):
    # Conectar al grupo 0 por defecto
    await manager.connect(websocket, 0)
    try:
        while True:
            data = await websocket.receive_text()
            # Si el mensaje es un comando para unirse a una sala
            if data.startswith("/join "):
                # Extraer el game_id del mensaje
                game_id = int(data.split(" ", 1)[1])
                # Desconectar del grupo actual y conectar al nuevo
                await manager.disconnect(websocket, 0)
                await manager.connect(websocket, game_id)
            elif data.startswith("/leave"):
                # Extraer el game_id del mensaje
                game_id = int(data.split(" ", 1)[1])
                # Desconectar del grupo actual y conectar a la sala 0
                await manager.disconnect(websocket, game_id)
                await manager.connect(websocket, 0)
            else:
                # Procesar el mensaje normalmente
                await manager.send_personal_message(f"You wrote: {data}", websocket)
                await manager.broadcast(f"Client says: {data}", 0)
    except Exception as e:
        print(e)
    finally:
        # Desconectar del websocket cuando se cierra la conexión
        await manager.disconnect(websocket, 0)
