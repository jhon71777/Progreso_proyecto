# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List

# ==========================================
# SCHEMAS DE EMPRESAS
# ==========================================
class EmpresaBase(BaseModel):
    nombre: str
    correo: EmailStr
    nombre_cargador: Optional[str] = None

class EmpresaCreate(EmpresaBase):
    pass

class EmpresaOut(EmpresaBase):
    id: int

    class ConfigDict:
        from_attributes = True


# ==========================================
# SCHEMAS DE USUARIOS
# ==========================================
class UsuarioBase(BaseModel):
    nombre: str
    correo: EmailStr
    celular: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioOut(UsuarioBase):
    id: int

    class ConfigDict:
        from_attributes = True


# ==========================================
# SCHEMAS DE VEHÍCULOS
# ==========================================
class VehiculoBase(BaseModel):
    placa: str
    tipo_cargador: str
    marca: str

class VehiculoCreate(VehiculoBase):
    usuario_id: int

class VehiculoOut(VehiculoBase):
    id: int
    usuario_id: int

    class ConfigDict:
        from_attributes = True


# ==========================================
# SCHEMAS DE PUNTOS DE CARGA
# ==========================================
class PuntoCargaBase(BaseModel):
    direccion: str
    cantidad_cargadores: int = 1

class PuntoCargaCreate(PuntoCargaBase):
    empresa_id: int

class PuntoCargaOut(PuntoCargaBase):
    id: int
    empresa_id: int

    class ConfigDict:
        from_attributes = True