from fastapi import WebSocket
from app.websocket_manager import ConnectionManager

manager = ConnectionManager()

async def websocket_handler(websocket: WebSocket):
    # Conectar al grupo 0 por defecto
    await websocket.accept()
    await manager.connect(websocket, 0, 0)
    print("Se entró por primera vez al websocket_handler la conexión " + str(websocket))
    try:
        while True:
            data = await websocket.receive_text()

            if data.startswith("/join "):
                print("Se recibió un mensaje de unirse a la partida de " + str(websocket))
                try:
                    parts = data.split(" ")
                    if len(parts) >= 3:
                        game_id = int(parts[1])
                        player_id = int(parts[2])
                        manager.move(websocket, 0, game_id, player_id)
                    else:
                        print("Error: mensaje de unirse a la partida no tiene suficientes partes")
                except ValueError as e:
                    print(f"Error al convertir el mensaje a entero: {data}")
                    print(e)

            elif data.startswith("/leave"):
                print("Se recibió un mensaje para volver al home de " + str(websocket))
                try:
                    parts = data.split(" ")
                    if len(parts) >= 2:
                        game_id = int(parts[1])
                        manager.move(websocket, game_id, 0, None)
                    else:
                        print("Error: mensaje de dejar la partida no tiene suficientes partes")
                except ValueError as e:
                    print(f"Error al convertir el mensaje a entero: {data}")
                    print(e)

            elif data.startswith("/rejoin"):
                print("Se recibió un mensaje para volver a unirse a la partida de " + str(websocket))
                # Buscar el grupo al que pertenecía y volver a unirse
                player_id = int(data.split(" ", 1)[1])
                await manager.reconnect(websocket, player_id)

            else:
                await websocket.send_text(data)
    except Exception as e:
        print(e)
    finally:
        print("Entró al bloque finally y salió del websocket_handler la conexión " + str(websocket))
        # Desconectar del websocket cuando se cierra la conexión
        await manager.disconnect(websocket)
