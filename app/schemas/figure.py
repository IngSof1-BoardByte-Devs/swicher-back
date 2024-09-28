from pydantic import BaseModel

class FigureOut(BaseModel):
    card_id: int
    figure_type: str
