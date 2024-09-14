- Tener instalado python
- Crear un entorno virtual:
    $ python -m venv env
    $ source venv/bin/activate
- Instalar las dependencias (Pararse en la carpeta swicher-back):
    $ pip install -r requirements.txt
- Para correr el servidor (Pararse en la carpeta swicher-back):
    $ uvicorn app.main:app --reload




-tener instalado python
-entrar al entorno virtual
-pip install fastapi uvicorn 
-pip freeze > requeriments.txt //sirve para poner las versiones de las cosas en un archivo xd

-Para ejecutar pararse en la carpeta app (o donde se encuentra main)
-Ejecutar $uvicorn main:app  (si se le agrega --reload se recargan los cambios al guardar sin tener que bajar y levatar el server)
-Para ver la documentación ir a http://127.0.0.1:8000/docs (o /redoc) con el server levantado