from typing import List, Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.groups: Dict[int, List[List[WebSocket, int]]] = {}

    async def connect(self, websocket: WebSocket, group: int, id: int):
        """
        Añade a un usuario al grupo indicado. Si ya está en otro grupo, lo desconecta de ese grupo.
        """
        print(str(websocket) + " se ha conectado al grupo " + str(group))
        if group not in self.groups:
            self.groups[group] = []
        self.groups[group].append([websocket, id])

    def set_id(self, websocket: WebSocket, id: int):
        """
        Asigna un id a la conexión.
        """
        for group in self.groups:
            for connection in self.groups[group]:
                if connection[0] == websocket:
                    connection[1] = id
                    print(str(websocket) + " se le asignó el id " + str(id))

    def move(self, websocket: WebSocket, old_group: int, new_group: int, id: int):
        """
        Mueve al usuario del grupo antiguo al nuevo grupo.
        """
        if old_group in self.groups:
            for connection in self.groups[old_group]:
                if connection[0] == websocket:
                    self.groups[old_group].remove(connection)
                    break
        if new_group not in self.groups:
            self.groups[new_group] = []
        self.groups[new_group].append([websocket, id])
        print(str(websocket) + " se movió del grupo " + str(old_group) + " al grupo " + str(new_group))

    async def disconnect(self, websocket: WebSocket):
        """
        Marca como None la conexión del websocket. Si no hay más conexiones en el grupo, elimina el grupo.
        """
        for group in list(self.groups.keys()):
            for connection in self.groups[group]:
                if connection[0] == websocket:
                    connection[0] = None
                    break
            
            if all(conn[0] is None for conn in self.groups[group]):
                del self.groups[group]

    async def broadcast(self, message: str, group: int):
        """
        Envía un mensaje a todas las conexiones de un grupo específico.
        """
        connections = self.groups.get(group, [])
        for connection in connections:
            if connection[0] is not None:
                await connection[0].send_text(message)

    async def reconnect(self, websocket: WebSocket, id: int):
        """
        Reconecta a un usuario al grupo indicado.
        """
        for group in self.groups:
            for connection in self.groups[group]:
                if connection[1] == id:
                    connection[0] = websocket
                    print(str(websocket) + " se reconectó al grupo " + str(group))
                    break