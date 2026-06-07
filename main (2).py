from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field

app = FastAPI(
    title="API PROYECTO E.V CHARGE",
    description="Sistema de cargadores eléctricos en Bogota",
    version="1.0"
)

class Usuario(BaseModel):
    id: int = Field(gt=0, description="ID del usuario")
    nombre: str = Field(min_length=3, max_length=50, description="Nombre del usuario")
    telefono: str = Field(min_length=7, max_length=15, description="Número de teléfono")
    correo: str = Field(min_length=5, max_length=100, description="Correo electrónico")
    ciudad: str = Field(min_length=3, max_length=50, description="Ciudad del usuario")

db_usuarios = [
    {"id": 1, "nombre": "Carlos", "telefono": "3004567891", "correo": "carlos@gmail.com", "ciudad": "Bogota"},
    {"id": 2, "nombre": "Laura", "telefono": "3119876542", "correo": "laura@gmail.com", "ciudad": "Medellin"}
]
class Carga(BaseModel):
    id: int = Field(gt=0, description="ID de la carga")
    energia: float = Field(gt=0, description="Cantidad de energía")
    tiempo: int = Field(gt=0, description="Tiempo de carga")
    costo: float = Field(gt=0, description="Costo de la carga")
    estado: str = Field(min_length=3, max_length=30, description="Estado de la carga")

db_cargas = [
    {"id": 1, "energia": 45.5, "tiempo": 60, "costo": 30000, "estado": "completada"},
    {"id": 2, "energia": 30.0, "tiempo": 40, "costo": 18000, "estado": "cargando"}
]
class Estacion(BaseModel):
    id: int = Field(gt=0, description="ID de la estación")
    nombre: str = Field(min_length=3, max_length=50, description="Nombre de la estación")
    ubicacion: str = Field(min_length=5, max_length=100, description="Ubicación de la estación")
    conectores: int = Field(gt=0, description="Cantidad de conectores")
    estado: str = Field(min_length=3, max_length=30, description="Estado de la estación")

db_estaciones = [
    {"id": 1, "nombre": "Estación Norte", "ubicacion": "Bogota Norte", "conectores": 6, "estado": "activa"},
    {"id": 2, "nombre": "Estación Centro", "ubicacion": "Bogota Centro", "conectores": 4, "estado": "disponible"}
]

class Pago(BaseModel):
    id: int = Field(gt=0, description="ID del pago")
    usuario: str = Field(min_length=3, max_length=50, description="Nombre del usuario")
    monto: float = Field(gt=0, description="Monto del pago")
    metodo: str = Field(min_length=3, max_length=30, description="Método de pago")
    estado: str = Field(min_length=3, max_length=30, description="Estado del pago")

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

db_pagos = [
    {"id": 1, "usuario": "Carlos", "monto": 50000, "metodo": "tarjeta", "estado": "aprobado"},
    {"id": 2, "usuario": "Laura", "monto": 35000, "metodo": "efectivo", "estado": "pendiente"}
]
@app.get("/usuarios")
def obtener_usuarios():
    return {
        "total": len(db_usuarios),
        "usuarios": db_usuarios,
        "status": "success"
    }


@app.get("/usuarios/{id}")
def obtener_usuario_por_id(
    id: int = Path(..., gt=0, description="ID del usuario")
):
    for usuario in db_usuarios:
        if usuario["id"] == id:
            return {
                "usuario": usuario,
                "status": "success"
            }

    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@app.post("/usuarios", status_code=201)
def crear_usuario(usuario: Usuario):
    db_usuarios.append(usuario.dict())

    return {
        "mensaje": "Usuario registrado exitosamente",
        "usuario": usuario,
        "status": "success"
    }


@app.get("/cargas")
def obtener_cargas():
    return {
        "total": len(db_cargas),
        "cargas": db_cargas,
        "status": "success"
    }

@app.get("/cargas/{id}")
def obtener_carga_por_id(
    id: int = Path(..., gt=0, description="ID de la carga")
):
    for carga in db_cargas:
        if carga["id"] == id:
            return {
                "carga": carga,
                "status": "success"
            }

    raise HTTPException(status_code=404, detail="Carga no encontrada")

@app.post("/cargas", status_code=201)
def crear_carga(carga: Carga):
    db_cargas.append(carga.dict())

    return {
        "mensaje": "Carga registrada exitosamente",
        "carga": carga,
        "status": "success"
    }

@app.get("/estaciones")
def obtener_estaciones():
    return {
        "total": len(db_estaciones),
        "estaciones": db_estaciones,
        "status": "success"
    }

@app.get("/estaciones/{id}")
def obtener_estacion_por_id(
    id: int = Path(..., gt=0, description="ID de la estación")
):
    for estacion in db_estaciones:
        if estacion["id"] == id:
            return {
                "estacion": estacion,
                "status": "success"
            }

    raise HTTPException(status_code=404, detail="Estación no encontrada")

@app.post("/estaciones", status_code=201)
def crear_estacion(estacion: Estacion):
    db_estaciones.append(estacion.dict())

    return {
        "mensaje": "Estación registrada exitosamente",
        "estacion": estacion,
        "status": "success"
    }

@app.get("/pagos")
def obtener_pagos():
    return {
        "total": len(db_pagos),
        "pagos": db_pagos,
        "status": "success"
    }

@app.get("/pagos/{id}")
def obtener_pago_por_id(
    id: int = Path(..., gt=0, description="ID del pago")
):
    for pago in db_pagos:
        if pago["id"] == id:
            return {
                "pago": pago,
                "status": "success"
            }

    raise HTTPException(status_code=404, detail="Pago no encontrado")

@app.post("/pagos", status_code=201)
def crear_pago(pago: Pago):
    db_pagos.append(pago.dict())

    return {
        "mensaje": "Pago registrado exitosamente",
        "pago": pago,
        "status": "success"
 }
