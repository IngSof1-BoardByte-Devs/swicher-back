from pydantic import BaseModel

class FigureOut(BaseModel):
    player_id: int
    id_figure: int
    type_figure: str
