from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.routes import game, player, movement_card, figure_card
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
app.include_router(movement_card.router, prefix="/movement-cards") 
app.include_router(figure_card.router, prefix="/figure-cards")


# Código para la página de debugging de WebSockets -----------------------
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket Debugging Messages</title>
    </head>
    <body>
        <h1>WebSocket Debugging Messages</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

# -------------------------------------------------------------------------

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        if websocket is not None:
            await websocket_handler(websocket)
    except Exception as e:
        print(f"Error handling websocket: {e}")
