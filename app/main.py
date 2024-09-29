from fastapi import FastAPI
from app.routes import game, player
from app.core.websocket import websocket_handler
from fastapi.websockets import WebSocket
from fastapi.middleware.cors import CORSMiddleware
import app.database.models as model # importamos todos los modelos dentro del archivo
from app.database.session import engine

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
model.Base.metadata.create_all(bind=engine)

# Incluyendo las rutas
app.include_router(game.router, prefix="/games")
app.include_router(player.router, prefix="/players")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket_handler(websocket)
    except Exception as e:
        print(f"Error handling websocket: {e}")
