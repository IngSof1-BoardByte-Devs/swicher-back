from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# Asegurarse de que el directorio 'app/database' exista
db_folder = 'app/database'

# Creamos el motor, el cual al comienzo de la ruta de la DB
# Se especifica que es sqlite
engine = create_engine('sqlite:///app/database/db.sqlite')

Session = sessionmaker(autocommit=False,
                            autoflush=False,
                            bind=engine)

def get_db():
    db = Session()  # Crear una nueva sesión
    try:
        yield db  # "Retorna" la sesión, pero usando yield para que se mantenga abierta durante la request
    finally:
        db.close()  # Cerrar la sesión cuando la request termine