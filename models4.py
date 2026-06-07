# models4.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database4 import Base

# 1. Tabla de Empresas 
class empresas(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    nombre_cargador = Column(String(100))

    
    puntos = relationship("puntos_carga", back_populates="empresa", cascade="all, delete-orphan")


# 2. Tabla de Usuarios
class usuarios(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    celular = Column(String(20))

    
    vehiculos = relationship("vehiculos", back_populates="dueno", cascade="all, delete-orphan")


# 3. Tabla de Vehículos 
class vehiculos(Base):
    __tablename__ = "vehiculos"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(15), unique=True, nullable=False)
    tipo_cargador = Column(String(50), nullable=False)
    marca = Column(String(50), nullable=False)
    
    
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)

    
    dueno = relationship("usuarios", back_populates="vehiculos")


# 4. Tabla de Puntos de Carga 
class puntos_carga(Base):
    __tablename__ = "puntos_carga"

    id = Column(Integer, primary_key=True, index=True)
    direccion = Column(String(150), nullable=False)
    cantidad_cargadores = Column(Integer, default=1, nullable=False)
    
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)

    
    empresa = relationship("empresas", back_populates="puntos")