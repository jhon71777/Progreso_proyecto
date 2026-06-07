
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(
    title="API PROYECTO E.V CHARGE",
    description="Sistema de cargadores eléctricos en Bogota",
    version="1.0"
)

# ========== MODELO DE CARRO ==========
class Carro(BaseModel):
    id: int = Field(gt=0, description="ID del carro, debe ser mayor a 0")
    placa: str = Field(min_length=5, max_length=10, description="Placa del carro (ej: ABC-123)")
    modelo: str = Field(min_length=1, max_length=50, description="Modelo del carro")
    tipo_cargador: str = Field(min_length=1, description="Tipo de cargador (eléctrico, híbrido, gasolina, diésel)")
    estado: str = Field(min_length=1, description="Estado del carro (cargando, descargando, disponible, mantenimiento)")
    capacidad: float = Field(gt=0, description="Capacidad de carga en kilogramos")

# Base de datos simulada de carros
db_carros = [
    {"id": 1, "placa": "SDF156", "modelo": "Renault Zoe", "tipo_cargador": "eléctrico", "estado": "cargando", "capacidad": 400},
    {"id": 2, "placa": "RGH894", "modelo": "Tesla Model 3", "tipo_cargador": "eléctrico", "estado": "disponible", "capacidad": 500}
]

contador_id = 3  # Para el próximo ID

# ========== ENDPOINTS DEL MÓDULO CARRO ==========

# 1. GET - Obtener todos los carros
@app.get("/carros")
def obtener_carros(
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo de cargador")
):
    resultados = db_carros.copy()
    
    if estado:
        resultados = [c for c in resultados if c["estado"].lower() == estado.lower()]
    
    if tipo:
        resultados = [c for c in resultados if c["tipo_cargador"].lower() == tipo.lower()]
    
    return {
        "total": len(resultados),
        "carros": resultados,
        "status": "success"
    }

# 2. GET - Obtener carro por ID
@app.get("/carros/{id}")
def obtener_carro_por_id(
    id: int = Path(..., gt=0, description="ID del carro")
):
    for carro in db_carros:
        if carro["id"] == id:
            return {
                "carro": carro,
                "status": "success"
            }
    raise HTTPException(status_code=404, detail="Carro no encontrado")

# 3. GET - Obtener carro por placa
@app.get("/carros/placa/{placa}")
def obtener_carro_por_placa(
    placa: str = Path(..., min_length=5, max_length=10, description="Placa del carro")
):
    for carro in db_carros:
        if carro["placa"].upper() == placa.upper():
            return {
                "carro": carro,
                "status": "success"
            }
    raise HTTPException(status_code=404, detail=f"Carro con placa {placa} no encontrado")

# 4. POST - Crear nuevo carro
@app.post("/carros", status_code=201)
def crear_carro(carro: Carro):
    global contador_id
    
    # Verificar que la placa no exista
    for c in db_carros:
        if c["placa"] == carro.placa:
            raise HTTPException(status_code=400, detail="Ya existe un carro con esta placa")
    
    # Crear el nuevo carro con ID automático
    nuevo_carro = carro.dict()
    nuevo_carro["id"] = contador_id
    contador_id += 1
    
    db_carros.append(nuevo_carro)
    
    return {
        "mensaje": "Carro registrado exitosamente",
        "carro": nuevo_carro,
        "status": "success"
    }
