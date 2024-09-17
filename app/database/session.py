"""
Este archivo gestiona la configuración y el manejo de la sesión de base de datos. Es donde se define la 
conexión a la base de datos y se crea el objeto db para usar en otras partes del sistema.
"""

from pony.orm import Database

# Crear instancia de la base de datos
db = Database()

def config_database():
    """
    Configura la base de datos y genera las tablas si no existen.
    """
    # Conectar a la base de datos SQLite
    db.bind(provider="sqlite", filename="el_switcher_db.sqlite", create_db=True)
    
    db.generate_mapping(create_tables=True)