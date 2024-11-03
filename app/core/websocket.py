from fastapi import WebSocket
from app.websocket_manager import ConnectionManager
from app.services.websocket import handle_event

manager = ConnectionManager()

async def websocket_handler(websocket: WebSocket):
    # Conectar al grupo 0 por defecto
    await websocket.accept()
    await manager.connect(websocket, 0)
    print("Se entró por primera vez al websocket_handler la conexión " + str(websocket))
    try:
        while True:
            data = await websocket.receive_text()

            if data.startswith("games.join"):
                print("Se recibió un mensaje de unirse a la partida de " + str(websocket))
                # Desconectar del grupo actual y conectar al nuevo
                game_id = int(data.split(" ", 1)[1])
                manager.move(websocket, 0, game_id)

            elif data.startswith("games.leave"):
                print("Se recibió un mensaje para volver al home de " + str(websocket))
                # Desconectar del grupo actual y conectar a la sala 0
                game_id = int(data.split(" ", 1)[1])
                manager.move(websocket, game_id, 0)

            else:
                await handle_event(websocket, data)
                websocket.send_text
    except Exception as e:
        print(e)
    finally:
        print("Entró al bloque finally y salió del websocket_handler la conexión " + str(websocket))
        # Desconectar del websocket cuando se cierra la conexión
        await manager.disconnect(websocket)
