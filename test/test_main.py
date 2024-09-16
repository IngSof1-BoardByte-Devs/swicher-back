from fastapi import FastAPI
from app.routes import game, player

app_test = FastAPI()

app_test.include_router(game.router, prefix="/game")
app_test.include_router(player.router, prefix="/player")