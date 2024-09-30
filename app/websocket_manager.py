# Gestión de las conexiones de WebSocket si es necesario
from typing import List, Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.groups: Dict[int, List[WebSocket]] = {}  # Diccionario de grupos con el id de la partida (o 0 si no está en ninguna) y las conexiones de los usuarios

    async def connect(self, websocket: WebSocket, group: int):
        """
        Añade a un usuario al grupo indicado. Si ya está en otro grupo, lo desconecta de ese grupo.
        """
        # Aceptar la conexión
        await websocket.accept()
        self.groups[group].append(websocket)

    def move(self, websocket: WebSocket, old_group: int, new_group: int):
        """
        Mueve al usuario del grupo antiguo al nuevo grupo.
        """
        # Desconectar del grupo antiguo
        self.disconnect(websocket, old_group)

        # Conectar al nuevo grupo
        if new_group not in self.groups:
            self.groups[new_group] = []
        self.groups[new_group].append(websocket)

    def disconnect(self, websocket: WebSocket, group: int):
        """
        Elimina al usuario del grupo en el que esté actualmente.
        """
        if group in self.groups:
            self.groups[group].remove(websocket)
            # Si el grupo está vacío, eliminarlo
            if len(self.groups[group]) == 0:
                del self.groups[group]

    async def broadcast(self, message: str, group: int):
        """
        Envía un mensaje a todas las conexiones de un grupo específico.
        """
        connections = self.groups.get(group, [])
        for connection in connections:
            if connection is not None:
                await connection.send('message')
            else:
                print('Acá es donde falla')
