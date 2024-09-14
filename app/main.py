from fastapi import FastAPI
from app.routes import game, mensajes, player
from app.core.websocket import websocket_handler
from app.database.session import config_database
from fastapi.websockets import WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurando CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializando la base de datos
config_database(test=False)

# Incluyendo las rutas
""" app.include_router(mensajes.router, prefix="") """
app.include_router(game.router, prefix="/game")
app.include_router(player.router, prefix="/player")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_handler(websocket)
