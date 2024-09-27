from pydantic import BaseModel
from typing import List

class Position(BaseModel):
    x: int
    y: int

class Figure(BaseModel):
    figure_id: int
    position: Position

class BoardState(BaseModel):
    board_state: List[Figure]