import sqlite3
from fastapi import FastAPI, HTTPException, Header  ### NUEVO: Agregamos Header
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

### NUEVO: Define tu contraseña 
MI_TOKEN_SECRETO = "251003"

class Transaccion(BaseModel):
    monto: float
    categoria: str
    nota: str = None

def get_db_connection():
    conn = sqlite3.connect('finanzas.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def startup():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            monto REAL NOT NULL,
            categoria TEXT NOT NULL,
            nota TEXT
        )
    ''')
    conn.commit()
    conn.close()

### MODIFICADO: Agregamos la verificación del token aquí
@app.post("/registrar")
async def registrar_gasto(t: Transaccion, x_token: str = Header(None)):
    if x_token != MI_TOKEN_SECRETO:
        raise HTTPException(status_code=401, detail="No autorizado 🚫")
    
    try:
        conn = get_db_connection()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "INSERT INTO movimientos (fecha, monto, categoria, nota) VALUES (?, ?, ?, ?)",
            (fecha_actual, t.monto, t.categoria, t.nota)
        )
        conn.commit()
        conn.close()
        return {"mensaje": "Guardado exitosamente", "monto": t.monto}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ... (El resto sigue igual)

# 5. Endpoint para ver tus gastos (opcional, para probar en el navegador)
@app.get("/ver-gastos")
async def leer_gastos():
    conn = get_db_connection()
    gastos = conn.execute("SELECT * FROM movimientos ORDER BY id DESC LIMIT 10").fetchall()
    conn.close()
    return gastos