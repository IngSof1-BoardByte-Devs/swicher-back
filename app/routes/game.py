"""
Los archivos de rutas son los encargados de manejar las peticiones HTTP que llegan al servidor.
Es donde se definen los endpoints y se especifica qué funciones se ejecutarán al recibir una 
petición en un endpoint específico.
"""


from fastapi import APIRouter

router = APIRouter()

@router.get("/game/status")
async def game_status():
    return {"status": "El juego está en curso"}
