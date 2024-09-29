from pydantic import BaseModel

class MovementOut(BaseModel):
    id_movement : int
    type_movement : str

class MovementRequest(BaseModel):
    player_id: int