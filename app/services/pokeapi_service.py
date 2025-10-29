# app/services/pokeapi_service.py
import httpx
from typing import Optional, List, Dict
from fastapi import HTTPException
import logging

logger = logging.getLogger("pokedex_api.pokeapi")


class PokeAPIService:
    BASE_URL = "https://pokeapi.co/api/v2"

    def __init__(self):
        # Cliente persistente de httpx con timeout
        self.client = httpx.AsyncClient(base_url=self.BASE_URL, timeout=5.0)

        # --- Método 1: get_pokemon (Implementación asumida) ---

    async def get_pokemon(self, identifier: str | int) -> Dict:
        """
        Obtiene información completa de un Pokémon.
        (Maneja errores 404, 500, timeout y realiza logging)
        """
        endpoint = f"/pokemon/{identifier}"
        logger.info(f"Llamada externa a PokeAPI: GET {self.BASE_URL}{endpoint}")

        try:
            response = await self.client.get(endpoint)
            response.raise_for_status()

            logger.info(f"Respuesta de PokeAPI: {response.status_code} | GET {endpoint}")

            data = response.json()

            # Transformación de datos (extracción de campos relevantes)
            return {
                "id": data.get("id"),
                "name": data.get("name"),
                "base_experience": data.get("base_experience"),
                "types": [t["type"]["name"] for t in data.get("types", [])],
                "sprites": data.get("sprites", {}).get("front_default")
            }

        except httpx.TimeoutException:
            logger.error(f"PokeAPI: Timeout al acceder a {endpoint}")
            raise HTTPException(status_code=504, detail="Error de red (Timeout) al consultar PokeAPI")
        except httpx.ConnectError:
            logger.error(f"PokeAPI: Error de conexión con la API externa en {endpoint}")
            raise HTTPException(status_code=503, detail="Error de conexión con la PokeAPI")
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            if status_code == 404:
                logger.warning(f"Pokémon no encontrado: {identifier}")
                raise HTTPException(status_code=404,
                                    detail=f"Pokémon con identificador '{identifier}' no encontrado en PokeAPI")
            logger.error(f"PokeAPI: Error HTTP {status_code} en {endpoint}")
            raise HTTPException(status_code=502, detail=f"Error en la API externa de Pokémon: código {status_code}")
        except Exception as e:
            logger.error(f"Error inesperado al obtener Pokémon {identifier}: {e}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    # --- Método 2: search_pokemon (Implementación requerida) ---
    async def search_pokemon(self, limit: int = 20, offset: int = 0) -> Dict:
        """
        Lista Pokémon con paginación usando GET /pokemon
        """
        endpoint = "/pokemon"
        params = {"limit": limit, "offset": offset}

        # Validación de parámetros de entrada (Criterio de Evaluación)
        if limit < 1 or offset < 0:
            raise HTTPException(status_code=400, detail="Limit debe ser positivo y offset no puede ser negativo.")

        logger.info(f"Llamada externa a PokeAPI: GET {self.BASE_URL}{endpoint} con {params}")

        try:
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()

            logger.info(f"Respuesta de PokeAPI: {response.status_code} | GET {endpoint}")

            data = response.json()

            # Transformación de datos (extracción de campos relevantes)
            # Solo retornamos la estructura de paginación básica de la PokeAPI
            return {
                "count": data.get("count"),
                "next": data.get("next"),
                "previous": data.get("previous"),
                "results": data.get("results")  # results contiene {name, url}
            }

        except httpx.TimeoutException:
            logger.error(f"PokeAPI: Timeout al buscar Pokémon")
            raise HTTPException(status_code=504, detail="Error de red (Timeout) al consultar PokeAPI")
        except httpx.HTTPStatusError as exc:
            logger.error(f"PokeAPI: Error HTTP {exc.response.status_code} al buscar Pokémon")
            raise HTTPException(status_code=502,
                                detail=f"Error en la API externa de Pokémon: código {exc.response.status_code}")
        except Exception as e:
            logger.error(f"Error inesperado al buscar Pokémon: {e}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    # --- Método 3: get_pokemon_by_type (Implementación requerida) ---
    async def get_pokemon_by_type(self, type_name: str) -> List[Dict]:
        """
        Obtiene todos los Pokémon de un tipo específico usando GET /type/{type}
        """
        endpoint = f"/type/{type_name.lower()}"
        logger.info(f"Llamada externa a PokeAPI: GET {self.BASE_URL}{endpoint}")

        try:
            response = await self.client.get(endpoint)
            response.raise_for_status()

            logger.info(f"Respuesta de PokeAPI: {response.status_code} | GET {endpoint}")

            data = response.json()

            # Transformación de datos: Extraemos solo la lista de Pokémon
            pokemon_list = data.get("pokemon", [])

            # Mapeamos para devolver una lista de objetos Pokémon simplificados
            return [
                {"name": item["pokemon"]["name"], "url": item["pokemon"]["url"]}
                for item in pokemon_list
            ]

        except httpx.TimeoutException:
            logger.error(f"PokeAPI: Timeout al buscar por tipo {type_name}")
            raise HTTPException(status_code=504, detail="Error de red (Timeout) al consultar PokeAPI")
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            if status_code == 404:
                logger.warning(f"Tipo de Pokémon no encontrado: {type_name}")
                raise HTTPException(status_code=404, detail=f"Tipo de Pokémon '{type_name}' no encontrado en PokeAPI")
            logger.error(f"PokeAPI: Error HTTP {status_code} al buscar por tipo {type_name}")
            raise HTTPException(status_code=502, detail=f"Error en la API externa de Pokémon: código {status_code}")
        except Exception as e:
            logger.error(f"Error inesperado al buscar por tipo {type_name}: {e}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")


# Instancia para uso en routers
pokeapi_service = PokeAPIService()