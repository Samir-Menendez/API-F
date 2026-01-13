import sqlite3
from contextlib import asynccontextmanager # <--- 1. NUEVO IMPORT
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime

# --- CONFIGURACIÓN ---
MI_TOKEN_SECRETO = "251003"

# --- MODELO DE DATOS ---
class Transaccion(BaseModel):
    monto: float
    categoria: str
    nota: str = None
    tipo: str 

# --- CONEXIÓN A BASE DE DATOS ---
def get_db_connection():
    conn = sqlite3.connect('finanzas.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- 2. NUEVA LÓGICA DE INICIO (Lifespan) ---
# Esta función reemplaza al antiguo @app.on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI):
    # LO QUE PASA AL ARRANCAR (STARTUP):
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
    print("🚀 Base de datos inicializada y lista.")
    
    yield  # <--- Aquí es donde el servidor se queda corriendo
    
    # LO QUE PASA AL APAGAR (SHUTDOWN) - Opcional:
    print("👋 Servidor apagándose...")

# --- 3. INICIALIZAMOS LA APP CON LIFESPAN ---
app = FastAPI(lifespan=lifespan)

# --- ENDPOINTS (Igual que antes) ---
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