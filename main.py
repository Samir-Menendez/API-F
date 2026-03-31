import sqlite3
import os
from contextlib import asynccontextmanager 
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuración principal
MI_TOKEN_SECRETO = os.getenv("MY_API_TOKEN", "TOKEN_NO_CONFIGURADO")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "finanzas.db"))

class Transaccion(BaseModel):
    monto: float
    categoria: str
    nota: str = None
    tipo: str 

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa la tabla al arrancar
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            monto REAL NOT NULL,
            categoria TEXT NOT NULL,
            nota TEXT,
            tipo TEXT DEFAULT 'gasto'
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Base de datos inicializada y lista en: {DB_PATH}")
    
    yield  
    
    print("👋 Servidor apagándose...")

app = FastAPI(lifespan=lifespan)

@app.post("/registrar")
async def registrar_transaccion(t: Transaccion, x_token: str = Header(None)):
    if x_token != MI_TOKEN_SECRETO:
        raise HTTPException(status_code=401, detail="No autorizado 🚫. Clave incorrecta.")
    
    try:
        conn = get_db_connection()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "INSERT INTO movimientos (fecha, monto, categoria, nota, tipo) VALUES (?, ?, ?, ?, ?)",
            (fecha_actual, t.monto, t.categoria, t.nota, t.tipo)
        )
        conn.commit()
        conn.close()
        return {
            "mensaje": f"✅ {t.tipo.capitalize()} de ${t.monto} guardado",
            "categoria": t.categoria
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ver-movimientos")
async def ver_movimientos():
    conn = get_db_connection()
    movimientos = conn.execute("SELECT * FROM movimientos ORDER BY id DESC LIMIT 20").fetchall()
    conn.close()
    return movimientos