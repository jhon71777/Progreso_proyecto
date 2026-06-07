# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import Base, engine, get_db

from models import empresas, usuarios, vehiculos, puntos_carga

# 1. Crear una única instancia de FastAPI
app = FastAPI()

# 2. Configurar el middleware de CORS correctamente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite peticiones desde la interfaz local o cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permite POST, GET, OPTIONS, etc.
    allow_headers=["*"],  # Permite todos los encabezados HTTP
)

# 3. Crear las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)


# ==========================================
#          ENDPOINT DE INICIO DE SESIÓN
# ==========================================
@app.post("/login")
def login_usuario(correo: str, contrasena: str, db: Session = Depends(get_db)):
    """
    Ruta para validar las credenciales de un usuario.
    Busca en la tabla de usuarios por su correo electrónico.
    """
    # Buscamos si el correo existe en la base de datos
    usuario_existente = db.query(usuarios).filter(usuarios.correo == correo).first()
    
    if not usuario_existente:
        raise HTTPException(status_code=404, detail="El correo electrónico no está registrado.")
    
    # IMPORTANTE: Como en tu tabla 'usuarios' no agregamos una columna de contraseña en el script inicial,
    # para no romper tu base de datos actual, aquí permitiremos ingresar temporalmente usando una validación.
    # Si agregaste el campo 'contrasena' a tu base de datos y a models.py, cambia esta línea por:
    # if usuario_existente.contrasena != contrasena:
    
    # Validación por defecto si aún no manejas contraseñas dinámicas en el backend
    if contrasena != "admin123" and contrasena != "12345678":
        raise HTTPException(status_code=401, detail="Contraseña incorrecta.")
        
    return {
        "mensaje": "¡Acceso concedido! ⚡",
        "usuario": {
            "id": usuario_existente.id,
            "nombre": usuario_existente.nombre,
            "correo": usuario_existente.correo
        }
    }


# ==========================================
#             RUTAS DE USUARIOS
# ==========================================
@app.post("/usuario")
def crear_usuario(nombre: str, correo: str, celular: str = None, db: Session = Depends(get_db)):
    # Comprobar si el correo ya está registrado para evitar errores de restricción UNIQUE en PostgreSQL
    existe = db.query(usuarios).filter(usuarios.correo == correo).first()
    if existe:
        raise HTTPException(status_code=400, detail="Este correo electrónico ya está registrado.")

    nuevo_usuario = usuarios(nombre=nombre, correo=correo, celular=celular)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return {"mensaje": "Usuario registrado ✅", "usuario": nuevo_usuario}

@app.get("/usuario")
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(usuarios).all()


# ==========================================
#             RUTAS DE EMPRESAS
# ==========================================
@app.post("/empresa")
def crear_empresa(nombre: str, correo: str, nombre_cargador: str, db: Session = Depends(get_db)):
    nueva_empresa = empresas(nombre=nombre, correo=correo, nombre_cargador=nombre_cargador)
    db.add(nueva_empresa)
    db.commit()
    db.refresh(nueva_empresa)
    return {"mensaje": "Empresa registrada ✅", "empresa": nueva_empresa}

@app.get("/empresa")
def listar_empresas(db: Session = Depends(get_db)):
    return db.query(empresas).all()


# ==========================================
#             RUTAS DE VEH