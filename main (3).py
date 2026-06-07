from fastapi import FastAPI, HTTPException, Path, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
import time
import logging

# ── Logging básico ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="API PROYECTO E.V CHARGE",
    description="Sistema de cargadores eléctricos en Bogota",
    version="1.0"
)

# ── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Middleware: logger de peticiones ────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    logger.info(f"→ {request.method} {request.url.path}")

    response = await call_next(request)

    duration = round((time.time() - start) * 1000, 2)
    logger.info(f"← {response.status_code} ({duration} ms)")
    return response

# ── Excepciones personalizadas ──────────────────────────────────────────────

class RecursoNoEncontradoException(Exception):
    """Se lanza cuando un recurso buscado por ID o placa no existe en la BD."""
    def __init__(self, recurso: str, identificador):
        self.recurso = recurso
        self.identificador = identificador
        super().__init__(f"{recurso} con identificador '{identificador}' no encontrado")

class RecursoDuplicadoException(Exception):
    """Se lanza al intentar crear un recurso que ya existe (ej: placa repetida)."""
    def __init__(self, recurso: str, campo: str, valor):
        self.recurso = recurso
        self.campo = campo
        self.valor = valor
        super().__init__(f"Ya existe un {recurso} con {campo}='{valor}'")

class EstadoInvalidoException(Exception):
    """Se lanza cuando el estado enviado no pertenece a los valores permitidos."""
    def __init__(self, recurso: str, estado: str, permitidos: list):
        self.recurso = recurso
        self.estado = estado
        self.permitidos = permitidos
        super().__init__(f"Estado '{estado}' no válido para {recurso}. Permitidos: {permitidos}")

# ── Manejo global de errores ────────────────────────────────────────────────
@app.exception_handler(RecursoNoEncontradoException)
async def recurso_no_encontrado_handler(request: Request, exc: RecursoNoEncontradoException):
    # Respuesta JSON ejemplo:
    # {
    #   "status": "error",
    #   "tipo": "RecursoNoEncontrado",
    #   "codigo": 404,
    #   "detalle": "Carro con identificador '99' no encontrado"
    # }
    logger.warning(f"[404] {exc} | path={request.url.path}")
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "tipo": "RecursoNoEncontrado",
            "codigo": 404,
            "detalle": str(exc),
        },
    )

@app.exception_handler(RecursoDuplicadoException)
async def recurso_duplicado_handler(request: Request, exc: RecursoDuplicadoException):
    # Respuesta JSON ejemplo:
    # {
    #   "status": "error",
    #   "tipo": "RecursoDuplicado",
    #   "codigo": 409,
    #   "detalle": "Ya existe un Carro con placa='SDF156'"
    # }
    logger.warning(f"[409] {exc} | path={request.url.path}")
    return JSONResponse(
        status_code=409,
        content={
            "status": "error",
            "tipo": "RecursoDuplicado",
            "codigo": 409,
            "detalle": str(exc),
        },
    )

@app.exception_handler(EstadoInvalidoException)
async def estado_invalido_handler(request: Request, exc: EstadoInvalidoException):
    # Respuesta JSON ejemplo:
    # {
    #   "status": "error",
    #   "tipo": "EstadoInvalido",
    #   "codigo": 422,
    #   "detalle": "Estado 'volando' no válido para Carro. Permitidos: [...]",
    #   "estados_permitidos": ["cargando", "disponible", "mantenimiento", "inactivo"]
    # }
    logger.warning(f"[422] {exc} | path={request.url.path}")
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "tipo": "EstadoInvalido",
            "codigo": 422,
            "detalle": str(exc),
            "estados_permitidos": exc.permitidos,
        },
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Respuesta JSON ejemplo:
    # {
    #   "status": "error",
    #   "codigo": 422,
    #   "detalle": "value is not a valid integer"
    # }
    logger.warning(f"HTTPException {exc.status_code}: {exc.detail} | path={request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "codigo": exc.status_code,
            "detalle": exc.detail,
        },
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Respuesta JSON ejemplo:
    # {
    #   "status": "error",
    #   "codigo": 500,
    #   "detalle": "Error interno del servidor. Intenta de nuevo más tarde."
    # }
    logger.error(f"Error inesperado: {exc} | path={request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "codigo": 500,
            "detalle": "Error interno del servidor. Intenta de nuevo más tarde.",
        },
    )

# ── Modelos ─────────────────────────────────────────────────────────────────
class Usuario(BaseModel):
    id: int = Field(gt=0, description="ID del usuario")
    nombre: str = Field(min_length=3, max_length=50)
    telefono: str = Field(min_length=7, max_length=15)
    correo: str = Field(min_length=5, max_length=100)
    ciudad: str = Field(min_length=3, max_length=50)

class Carga(BaseModel):
    id: int = Field(gt=0)
    energia: float = Field(gt=0)
    tiempo: int = Field(gt=0)
    costo: float = Field(gt=0)
    estado: str = Field(min_length=3, max_length=30)

class Estacion(BaseModel):
    id: int = Field(gt=0)
    nombre: str = Field(min_length=3, max_length=50)
    ubicacion: str = Field(min_length=5, max_length=100)
    conectores: int = Field(gt=0)
    estado: str = Field(min_length=3, max_length=30)

class Pago(BaseModel):
    id: int = Field(gt=0)
    usuario: str = Field(min_length=3, max_length=50)
    monto: float = Field(gt=0)
    metodo: str = Field(min_length=3, max_length=30)
    estado: str = Field(min_length=3, max_length=30)

class Carro(BaseModel):
    id: int = Field(gt=0)
    placa: str = Field(min_length=5, max_length=10)
    modelo: str = Field(min_length=1, max_length=50)
    tipo_cargador: str = Field(min_length=1)
    estado: str = Field(min_length=1)
    capacidad: float = Field(gt=0)

# ── Bases de datos simuladas ────────────────────────────────────────────────
db_usuarios = [
    {"id": 1, "nombre": "Carlos", "telefono": "3004567891", "correo": "carlos@gmail.com", "ciudad": "Bogota"},
    {"id": 2, "nombre": "Laura",  "telefono": "3119876542", "correo": "laura@gmail.com",  "ciudad": "Medellin"},
]

db_cargas = [
    {"id": 1, "energia": 45.5, "tiempo": 60, "costo": 30000, "estado": "completada"},
    {"id": 2, "energia": 30.0, "tiempo": 40, "costo": 18000, "estado": "cargando"},
]

db_estaciones = [
    {"id": 1, "nombre": "Estación Norte",  "ubicacion": "Bogota Norte",  "conectores": 6, "estado": "activa"},
    {"id": 2, "nombre": "Estación Centro", "ubicacion": "Bogota Centro", "conectores": 4, "estado": "disponible"},
]

db_pagos = [
    {"id": 1, "usuario": "Carlos", "monto": 50000, "metodo": "tarjeta",  "estado": "aprobado"},
    {"id": 2, "usuario": "Laura",  "monto": 35000, "metodo": "efectivo", "estado": "pendiente"},
]

db_carros = [
    {"id": 1, "placa": "SDF156", "modelo": "Renault Zoe",   "tipo_cargador": "eléctrico", "estado": "cargando",   "capacidad": 400},
    {"id": 2, "placa": "RGH894", "modelo": "Tesla Model 3", "tipo_cargador": "eléctrico", "estado": "disponible", "capacidad": 500},
]

contador_id = 3

# ── Endpoints: Usuarios ─────────────────────────────────────────────────────
@app.get("/usuarios")
def obtener_usuarios():
    return {"total": len(db_usuarios), "usuarios": db_usuarios, "status": "success"}

@app.get("/usuarios/{id}")
def obtener_usuario_por_id(id: int = Path(..., gt=0)):
    for u in db_usuarios:
        if u["id"] == id:
            return {"usuario": u, "status": "success"}
    raise RecursoNoEncontradoException("Usuario", id)

@app.post("/usuarios", status_code=201)
def crear_usuario(usuario: Usuario):
    db_usuarios.append(usuario.dict())
    return {"mensaje": "Usuario registrado exitosamente", "usuario": usuario, "status": "success"}

# ── Endpoints: Cargas ───────────────────────────────────────────────────────
@app.get("/cargas")
def obtener_cargas():
    return {"total": len(db_cargas), "cargas": db_cargas, "status": "success"}

@app.get("/cargas/{id}")
def obtener_carga_por_id(id: int = Path(..., gt=0)):
    for c in db_cargas:
        if c["id"] == id:
            return {"carga": c, "status": "success"}
    raise RecursoNoEncontradoException("Carga", id)

@app.post("/cargas", status_code=201)
def crear_carga(carga: Carga):
    db_cargas.append(carga.dict())
    return {"mensaje": "Carga registrada exitosamente", "carga": carga, "status": "success"}

# ── Endpoints: Estaciones ───────────────────────────────────────────────────
@app.get("/estaciones")
def obtener_estaciones():
    return {"total": len(db_estaciones), "estaciones": db_estaciones, "status": "success"}

@app.get("/estaciones/{id}")
def obtener_estacion_por_id(id: int = Path(..., gt=0)):
    for e in db_estaciones:
        if e["id"] == id:
            return {"estacion": e, "status": "success"}
    raise RecursoNoEncontradoException("Estacion", id)

@app.post("/estaciones", status_code=201)
def crear_estacion(estacion: Estacion):
    db_estaciones.append(estacion.dict())
    return {"mensaje": "Estación registrada exitosamente", "estacion": estacion, "status": "success"}

# ── Endpoints: Pagos ────────────────────────────────────────────────────────
@app.get("/pagos")
def obtener_pagos():
    return {"total": len(db_pagos), "pagos": db_pagos, "status": "success"}

@app.get("/pagos/{id}")
def obtener_pago_por_id(id: int = Path(..., gt=0)):
    for p in db_pagos:
        if p["id"] == id:
            return {"pago": p, "status": "success"}
    raise RecursoNoEncontradoException("Pago", id)

@app.post("/pagos", status_code=201)
def crear_pago(pago: Pago):
    db_pagos.append(pago.dict())
    return {"mensaje": "Pago registrado exitosamente", "pago": pago, "status": "success"}

# ── Endpoints: Carros ───────────────────────────────────────────────────────
@app.get("/carros")
def obtener_carros(
    estado: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
):
    resultados = db_carros.copy()
    if estado:
        resultados = [c for c in resultados if c["estado"].lower() == estado.lower()]
    if tipo:
        resultados = [c for c in resultados if c["tipo_cargador"].lower() == tipo.lower()]
    return {"total": len(resultados), "carros": resultados, "status": "success"}

@app.get("/carros/{id}")
def obtener_carro_por_id(id: int = Path(..., gt=0)):
    for c in db_carros:
        if c["id"] == id:
            return {"carro": c, "status": "success"}
    raise RecursoNoEncontradoException("Carro", id)

@app.get("/carros/placa/{placa}")
def obtener_carro_por_placa(placa: str = Path(..., min_length=5, max_length=10)):
    for c in db_carros:
        if c["placa"].upper() == placa.upper():
            return {"carro": c, "status": "success"}
    raise RecursoNoEncontradoException("Carro", placa)

ESTADOS_CARRO = ["cargando", "disponible", "mantenimiento", "inactivo"]

@app.post("/carros", status_code=201)
def crear_carro(carro: Carro):
    global contador_id

    if carro.estado.lower() not in ESTADOS_CARRO:
        raise EstadoInvalidoException("Carro", carro.estado, ESTADOS_CARRO)

    for c in db_carros:
        if c["placa"] == carro.placa:
            raise RecursoDuplicadoException("Carro", "placa", carro.placa)

    nuevo = carro.dict()
    nuevo["id"] = contador_id
    contador_id += 1
    db_carros.append(nuevo)
    return {"mensaje": "Carro registrado exitosamente", "carro": nuevo, "status": "success"}
