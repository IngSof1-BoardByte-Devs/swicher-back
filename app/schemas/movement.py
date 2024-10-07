from pydantic import BaseModel

class MovementOut(BaseModel):
    id_movement : int
    type_movement : str

class MovementRequest(BaseModel):
    player_id: int

class Movement(BaseModel):
    card_id: int
    id_player: int
    type: int

class MovementPartial(BaseModel):
    playerId: int
    index1: int
    index2: int