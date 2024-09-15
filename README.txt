- Tener instalado python
- Crear un entorno virtual:
    $ python -m venv venv
    $ source venv/bin/activate
- Instalar las dependencias (Pararse en la carpeta swicher-back):
    $ pip install -r requeriments.txt
- Para correr el servidor (Pararse en la carpeta swicher-back):
    $ uvicorn app.main:app --reload


Contrato de la API:

POST /create-game
Crea una nueva partida.
Request Body: {"player_name": "string", "game_name": "string"}
Response:
200 OK: {"status": "OK", "game_id": "int"}
400 ERROR: {"status": "ERROR", "message": "string"}

GET /games
Devuelve una lista de partidas disponibles.
Response:
200 OK: [
{ "game_id": "int", "game_name": "string",
"players": [ { "player_nickname": "string" } ]
}, ... ]

POST /join-game
Permite a un jugador unirse a una partida.
Request Body: {"player_nickname": "string", "game_id": "int"}
Response:
200 OK: {"status": "OK"}
400 ERROR: {"status": "ERROR", "message": "string"}

POST /leave-game
Permite a un jugador abandonar una partida.
Request Body: {"player_id": "int", "game_id": "int"}
Response:
200 OK: {"status": "OK"}
400 ERROR: {"status": "ERROR", "message": "string"}

POST /start-game
Inicia una partida.
Request Body: {"player_id": "int", "game_id": "int"}
Response:
200 OK: {"status": "OK"}
400 ERROR: {"status": "ERROR", "message": "string"}

GET /movement-cards
Devuelve las cartas de movimiento de un jugador.
Request Body: {"player_id": "int"}
Response:
200 OK: [ { "card_id": "int", "movement_type": "string" }, ... ]
400 ERROR: {"status": "ERROR", "message": "string"}

GET /figure-cards
Devuelve las cartas de figura asociadas a una partida.
Request Body: {"player_id": "int"}
Response:
200 OK: [ { "card_id": "int", "figure_type": "string" }, ... ]
400 ERROR: {"status": "ERROR", "message": "string"}

GET /board
Devuelve el estado del tablero de la partida.
Request Body: {"player_id": "int"}
Response:
200 OK: { "game_id": "int", "board_state": [
{ "figure_id": "int", "position": { "x": "int", "y": "int" } }, ... ]
}
400 ERROR: {"status": "ERROR", "message": "string"}

POST /end-turn
Finaliza el turno de un jugador.
Request Body: {"player_id": "int", "game_id": "int"}
Response:
200 OK: {"status": "OK"}
400 ERROR: {"status": "ERROR", "message": "string"}