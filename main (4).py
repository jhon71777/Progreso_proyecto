# main4.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database4 import Base, engine, get_db

from models4 import empresas, usuarios, vehiculos, puntos_carga


app = FastAPI()


Base.metadata.create_all(bind=engine)




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



@app.post("/usuario")
def crear_usuario(nombre: str, correo: str, celular: str = None, db: Session = Depends(get_db)):
    nuevo_usuario = usuarios(nombre=nombre, correo=correo, celular=celular)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return {"mensaje": "Usuario registrado ✅", "usuario": nuevo_usuario}

@app.get("/usuario")
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(usuarios).all()




@app.post("/vehiculo")
def crear_vehiculo(placa: str, tipo_cargador: str, marca: str, usuario_id: int, db: Session = Depends(get_db)):
    # Verificación: Comprobar si el usuario (dueño) realmente existe antes de registrar el vehículo
    existe_usuario = db.query(usuarios).filter(usuarios.id == usuario_id).first()
    if not existe_usuario:
        raise HTTPException(status_code=404, detail="El ID del usuario especificado no existe.")

    nuevo_vehiculo = vehiculos(
        placa=placa, 
        tipo_cargador=tipo_cargador, 
        marca=marca, 
        usuario_id=usuario_id
    )
    db.add(nuevo_vehiculo)
    db.commit()
    db.refresh(nuevo_vehiculo)
    return {"mensaje": "Vehículo registrado ✅", "vehiculo": nuevo_vehiculo}

@app.get("/vehiculo")
def listar_vehiculos(db: Session = Depends(get_db)):
    return db.query(vehiculos).all()




@app.post("/punto-carga")
def crear_punto_carga(direccion: str, empresa_id: int, cantidad_cargadores: int = 1, db: Session = Depends(get_db)):
    # Verificación: Comprobar si la empresa existe antes de registrar el punto de carga
    existe_empresa = db.query(empresas).filter(empresas.id == empresa_id).first()
    if not existe_empresa:
        raise HTTPException(status_code=404, detail="El ID de la empresa especificado no existe.")

    nuevo_punto = puntos_carga(
        direccion=direccion, 
        cantidad_cargadores=cantidad_cargadores, 
        empresa_id=empresa_id
    )
    db.add(nuevo_punto)
    db.commit()
    db.refresh(nuevo_punto)
    return {"mensaje": "Punto de carga registrado ✅", "punto_carga": nuevo_punto}

@app.get("/punto-carga")
def listar_puntos_carga(db: Session = Depends(get_db)):
    return db.query(puntos_carga).all()