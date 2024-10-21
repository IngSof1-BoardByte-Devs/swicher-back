from pydantic import BaseModel
from typing import List

class FigureOut(BaseModel):
    player_id: int
    id_figure: int
    type_figure: str

class FigureInBoard(BaseModel):
    type_figure: str
    indexes: List[int]