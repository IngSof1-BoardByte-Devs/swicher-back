from pydantic import BaseModel


class PlayerRequest(BaseModel):
    player_id: int
    player_name: str

class PlayerOut(BaseModel):
    id: int
    username: str
    turn: int