from pydantic import BaseModel


class PlayerName(BaseModel):
    username: str

class PlayerRequest(BaseModel):
    player_id: int

class PlayerOut(BaseModel):
    id: int
    username: str
    turn: int

class Message(BaseModel):
    message: str