from pydantic import BaseModel
from typing import List

class FigureOut(BaseModel):
    player_id: int
    card_id: int
    type: int

class FigUpdate(BaseModel):
    id: int
    id_player: int
    type: int  # Tipo de figura (Type 1, Type 2, ..., Type 25)
    discarded: bool
    blocked: bool

class FigureInBoard(BaseModel):
    type_figure: int
    indexes: List[int]

class FigureDiscard(BaseModel):
    playerId: int