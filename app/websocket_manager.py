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
        print(str(websocket) + "Se ha conectado al grupo " + str(group))
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
        print(str(websocket) + "se movió del grupo " + str(old_group) + " al grupo " + str(new_group))

    async def disconnect(self, websocket: WebSocket):
        """
        Elimina al usuario del grupo en el que esté actualmente.
        """
        for group in self.groups:
            if websocket in self.groups[group]:
                self.groups[group].remove(websocket)
                print(str(websocket) + "se borró del grupo " + str(group))
                # Si el grupo está vacío, eliminarlo
                if len(self.groups[group]) == 0:
                    del self.groups[group]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """
        Envía un mensaje personal a un usuario específico.
        """
        await websocket.send_text(message)

    async def broadcast(self, message: str, group: int):
        """
        Envía un mensaje a todas las conexiones de un grupo específico.
        """
        connections = self.groups.get(group, [])
        for connection in connections:
            if connection is not None:
                await connection.send_text(message)