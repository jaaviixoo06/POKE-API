# main.py
from fastapi import FastAPI
from fastapi import FastAPI # ⬅️ CORRECCIÓN 1: Importar la clase FastAPI
from app.services.pokeapi_service import PokeAPIService

app = FastAPI()

pokeapi_service = PokeAPIService()
@app.get("/pokemon/")
def read_root():
    # Nota: Esta función deberá ser 'async def' y usar 'await' más adelante
    pokeapi_service.search_pokemon()
    return {"mensaje": "Estamos en linea! "}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)