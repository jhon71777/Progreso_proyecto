from fastapi import FastAPI

app = FastAPI()

# Base de datos simulada
cargadores = [
    {"id": 1, "Tesla": "TIPO B", "Estado": "Activo", "cantidad de cargadores": 5},
    {"id": 2, "BYD": "TIPO C", "Estado": "fuera de servicio", "cantidad de cargadores": 0}
]
carro = [
    {"placa": "SDF156", "ID": "1001", "estado": "CARGANDO"},
    {"placa": "RGH894", "ID": "1002", "estado": "LIBRE"}
]

usuarios = [
    {"Nombre": "jhonsito", "ID": "12535633", "estado": "Activo"},
    {"Nombre": "juanito", "ID": "1565262", "estado": "inactivo"}
]

Notificaiones =[
    {"ESTADO": "DISPONIBLE", "ID": "12535633", "AVISO": "no tiene notificaciones"},
    {"ESTADO": "OCUPADO", "ID": "1565262", "estado": "tiene notificaciones"}

]




# --- RUTAS GET (Consultar) ---
@app.get("/EMPRESA DE CARGADORES ELECTRICOS")
def home():
    return {"empresa": "EV CHARGE", "ESTADO": "Activo"}

@app.get("/empleados")
def listar_cargadores():
    return {"lista_cargadores": cargadores}

@app.get("/pedidos")
def listar_pedidos():
    return {"lista_carro": carro}

@app.get("/usuarios")
def ver_sucursales():
    return {"lista_usuarios":usuarios}

@app.get("/notificaciones")
def crear_empleado():
    return {"lista_notificaciones":Notificaiones}

# --- RUTAS PUT  ---
@app.post("/actualizacion de cargadores")
def vender():
    cargadores[0]["cantidad de cargadores"] -= 2
    return {"mensaje": "Venta realizada", "inventario": cargadores}


# --- RUTAS PUT  ---
@app.put("/actualizar cargador")
def actualizar():
    cargadores[1]["cantidad de cargadores"] = 8
    return {"mensaje": "Producto actualizado", "inventario": cargadores}
@app.put("/actualizar")

@app.put("/actualizar CARRO")
def actualizar():
    carro[1]["placa"] = "ABC123"
    return {"mensaje": "Producto actualizado", "inventario": carro}
@app.put("/actualizar")


# --- RUTAS DELETE (Eliminar) ---
@app.delete("/eliminar")
def eliminar():
    if len(usuarios) > 1:
        usuarios.pop()
        return {"mensaje": "Producto eliminado", "inventario": usuarios}