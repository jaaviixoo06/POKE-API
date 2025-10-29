# app/database.py - CORREGIDO

from sqlmodel import create_engine, Session, SQLModel
from typing import Generator

# Usamos SQLite para desarrollo, como permite la práctica
SQLITE_FILE_NAME = "database.db"
sqlite_url = f"sqlite:///{SQLITE_FILE_NAME}"

# Crear el motor de la base de datos
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    """
    Crea las tablas en la base de datos basadas en los modelos SQLModel.
    NO importa los modelos explícitamente para evitar el error de importación.
    """
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Dependencia para obtener una sesión de base de datos."""
    with Session(engine) as session:
        yield session