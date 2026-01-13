import sqlite3

# Conectamos a tu base de datos existente
conn = sqlite3.connect('finanzas.db')
cursor = conn.cursor()

try:
    # Agregamos la columna 'tipo'. 
    # Por defecto, todo lo viejo será considerado 'gasto' para no romper nada.
    cursor.execute("ALTER TABLE movimientos ADD COLUMN tipo TEXT DEFAULT 'gasto'")
    conn.commit()
    print("✅ ÉXITO: Columna 'tipo' agregada correctamente.")
except Exception as e:
    print(f"⚠️ AVISO: {e} (Probablemente ya la habías agregado antes).")

conn.close()