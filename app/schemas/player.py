from pydantic import BaseModel


class PlayerName(BaseModel):
    username: str

class PlayerRequest(BaseModel):
    player_id: int