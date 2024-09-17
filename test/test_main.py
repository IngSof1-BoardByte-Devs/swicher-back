from fastapi import FastAPI
from app.database.session import config_database
from app.routes import game, player

app_test = FastAPI()

config_database(test=True)

app_test.include_router(game.router, prefix="/game")
app_test.include_router(player.router, prefix="/player")