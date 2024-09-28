from pydantic import BaseModel

class MovementOut(BaseModel):
    card_id : int
    movement_type : str

class MovementRequest(BaseModel):
    player_id: int