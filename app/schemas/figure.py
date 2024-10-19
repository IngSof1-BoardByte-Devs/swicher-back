from pydantic import BaseModel

class FigureOut(BaseModel):
    player_id: int
    id_figure: int
    type_figure: str

class FigUpdate(BaseModel):
    id: int
    id_player: int
    type: str  # Tipo de figura (Type 1, Type 2, ..., Type 25)
    discarded: bool
    blocked: bool
