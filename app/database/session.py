"""
Este archivo gestiona la configuración y el manejo de la sesión de base de datos. Es donde se define la 
conexión a la base de datos y se crea el objeto db para usar en otras partes del sistema.
"""

from pony.orm import Database

# Crear instancia de la base de datos
db = Database()

# Esta función sirve para diferenciar entre la base de datos de producción y los tests
def config_database(test: bool):
    if test:
        db.bind(provider="sqlite", filename="test_el_switcher_db.sqlite", create_db=True)
    else:
        db.bind(provider="sqlite", filename="el_switcher_db.sqlite", create_db=True)

    db.generate_mapping(create_tables=True)