from pydantic import BaseModel
from typing import List

class FigureOut(BaseModel):
    player_id: int
    id_figure: int
    type_figure: str
    locked: bool

class FigUpdate(BaseModel):
    id: int
    id_player: int
    type: str  # Tipo de figura (Type 1, Type 2, ..., Type 25)
    discarded: bool
    blocked: bool

class FigureInBoard(BaseModel):
    type_figure: str
    indexes: List[int]

class FigureDiscard(BaseModel):
    playerId: int
    color: int