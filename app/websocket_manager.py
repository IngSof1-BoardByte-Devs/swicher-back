from typing import List, Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.groups: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, group: int):
        """
        Añade a un usuario al grupo indicado. Si ya está en otro grupo, lo desconecta de ese grupo.
        """
        # Aceptar la conexión
        if group not in self.groups:
            self.groups[group] = []
        self.groups[group].append(websocket)

    def move(self, websocket: WebSocket, old_group: int, new_group: int):
        """
        Mueve al usuario del grupo antiguo al nuevo grupo.
        """
        if old_group in self.groups:
            self.groups[old_group].remove(websocket)
        if new_group not in self.groups:
            self.groups[new_group] = []
            
        self.groups[new_group].append(websocket)

    async def disconnect(self, websocket: WebSocket, group: int):
        """
        Elimina al usuario del grupo en el que esté actualmente.
        """
        if group in self.groups:
            print("Se ha desconectado del grupo" + str(group))
            # Si el grupo está vacío, eliminarlo
            if len(self.groups[group]) == 0:
                del self.groups[group]
                print("Se ha eliminado el grupo" + str(group))

    async def broadcast(self, message: str, group: int):
        """
        Envía un mensaje a todas las conexiones de un grupo específico.
        """
        connections = self.groups.get(group, [])
        for connection in connections:
            if connection is not None:
                await connection.send_text(message)