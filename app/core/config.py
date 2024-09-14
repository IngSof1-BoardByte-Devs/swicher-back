# Configuración general (variables de entorno)
# No funciona todavía (en mantenimiento...)
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = None
    debug: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
