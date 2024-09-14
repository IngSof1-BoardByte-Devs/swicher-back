from fastapi import FastAPI
from app.routes import game, mensajes, player
from app.core.websocket import websocket_handler
from app.database.session import config_database
from fastapi.websockets import WebSocket

app = FastAPI()

# Inicializando la base de datos
config_database(test=False)

# Incluyendo las rutas
app.include_router(mensajes.router, prefix="")
app.include_router(game.router, prefix="/game")
app.include_router(player.router, prefix="/player")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_handler(websocket)
