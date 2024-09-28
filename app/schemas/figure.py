from pydantic import BaseModel

class FigureOut(BaseModel):
    player_id: int
    card_id: int
    figure_type: str
