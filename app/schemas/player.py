from pydantic import BaseModel


class PlayerName(BaseModel):
    username: str