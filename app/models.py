# app/models.py

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from pydantic import EmailStr, conint # conint para validación de posición

# --- 1. Modelos SQLModel (Base de Datos) ---

class User(SQLModel, table=True):
    """Usuario del sistema"""
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, min_length=3, max_length=50)
    email: EmailStr = Field(unique=True, index=True) # Usamos EmailStr para mejor validación
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relaciones
    pokedex_entries: List["PokedexEntry"] = Relationship(back_populates="owner") #
    teams: List["Team"] = Relationship(back_populates="trainer") #

class PokedexEntry(SQLModel, table=True):
    """Entrada en la Pokédex de un usuario"""
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id") #
    # Datos del Pokémon (de PokeAPI)
    pokemon_id: int = Field(index=True) # ID en PokeAPI
    pokemon_name: str #
    pokemon_sprite: str # URL de la imagen
    # Datos del usuario
    is_captured: bool = Field(default=False) #
    capture_date: Optional[datetime] = None #
    nickname: Optional[str] = Field(default=None, max_length=50) #
    notes: Optional[str] = Field(default=None, max_length=500) #
    favorite: bool = Field(default=False) #
    created_at: datetime = Field(default_factory=datetime.utcnow) #

    # Relaciones
    owner: User = Relationship(back_populates="pokedex_entries") #
    # ⬅️ CORRECCIÓN: Relación Many-to-Many
    team_members: List["TeamMember"] = Relationship(back_populates="pokedex_entry") 

class Team(SQLModel, table=True):
    """Equipo de batalla (máximo 6 Pokémon)"""
    id: Optional[int] = Field(default=None, primary_key=True)
    trainer_id: int = Field(foreign_key="user.id") #
    name: str = Field(max_length=100) #
    description: Optional[str] = None #
    created_at: datetime = Field(default_factory=datetime.utcnow) #

    # Relaciones
    trainer: User = Relationship(back_populates="teams") #
    members: List["TeamMember"] = Relationship(back_populates="team") #