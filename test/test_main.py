from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.session import config_database
from app.routes import game, player

app_test = FastAPI()

config_database(test=True)

app_test.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app_test.include_router(game.router, prefix="/game")
app_test.include_router(player.router, prefix="/player")