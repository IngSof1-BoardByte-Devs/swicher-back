from fastapi import APIRouter
from app.database.models import Player, Mensaje
from pony.orm import db_session, select, commit

router = APIRouter()

@router.get("/traerMensajes")
async def mensajes():
    # Crear un objeto en la base de datos
    with db_session():
        mensajes = select(m for m in Mensaje)[:]
        mensajes = [{"id": m.id, "mensaje": m.mensaje, "player": m.player.username, "id_player": m.player.id } for m in mensajes]
    return {"mensajes": mensajes}


@router.post("/postear")
async def publicar_mensaje(username: str, mensaje: str):
    with db_session():
        player = select(p for p in Player if p.username == username).first()
        if not player:
            player = Player(username=username)
        Mensaje(mensaje=mensaje, player=player)
    return {"mensaje": mensaje, "player": username}


@router.delete("/eliminarMensaje")
async def borrar_mensajes(id: int, username: str):
    with db_session():
        player = select(p for p in Player if p.username == username).first()
        if player:
            mensajes = select(m for m in Mensaje if m.id == id and m.player == player)[:]
            for mensaje in mensajes:
                mensaje.delete()
                commit()
                return {"mensaje": "Mensaje eliminado"}
            return {"mensaje": "Mensaje no encontrado"}
    return {"error": "Jugador no encontrado"}