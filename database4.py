# database.py
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL de conexión a PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres@localhost:5432/ev_charge"

# Creación del motor de la base de datos
# database3.py (Líneas 9-12 corregidas)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"client_encoding": "win1252"})
# Fábrica de sesiones para interactuar con la BD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para mapear los modelos
Base = declarative_base()

# Dependencia para manejar el ciclo de vida de las conexiones
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()