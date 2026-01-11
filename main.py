import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# 1. Definimos la estructura de los datos que vendrán del iPhone
class Transaccion(BaseModel):
    monto: float
    categoria: str
    nota: str = None  # Opcional

# 2. Función para conectar a la Base de Datos
def get_db_connection():
    conn = sqlite3.connect('finanzas.db')
    conn.row_factory = sqlite3.Row
    return conn

# 3. Inicializar la tabla si no existe (se ejecuta al arrancar)
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

# 4. El Endpoint (Donde el iPhone enviará los datos)
@app.post("/registrar")
async def registrar_gasto(t: Transaccion):
    try:
        conn = get_db_connection()
        # Guardamos la fecha actual automáticamente
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

# 5. Endpoint para ver tus gastos (opcional, para probar en el navegador)
@app.get("/ver-gastos")
async def leer_gastos():
    conn = get_db_connection()
    gastos = conn.execute("SELECT * FROM movimientos ORDER BY id DESC LIMIT 10").fetchall()
    conn.close()
    return gastos