from pydantic import BaseModel
from typing import List

class Color(BaseModel):
    color: int

class Position(BaseModel):
    x: int
    y: int

class Figure(BaseModel):
    color: Color
    position: Position

class BoardState(BaseModel):
    board_state: List[Figure]

class BoardOut(BaseModel):
    board: List[Color]