import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# 1. Conectarse a la base de datos y leer los datos
conn = sqlite3.connect('finanzas.db')
df = pd.read_sql_query("SELECT * FROM movimientos", conn)
conn.close()

# Si no hay datos, avisar
if df.empty:
    print("No hay datos para graficar todavía.")
else:
    # 2. Convertir la columna monto a números
    df['monto'] = pd.to_numeric(df['monto'])

    # 3. Agrupar por categoría y sumar
    resumen = df.groupby('categoria')['monto'].sum()

    # 4. Crear el gráfico de pastel (Pie Chart)
    plt.figure(figsize=(8, 6))
    plt.pie(resumen, labels=resumen.index, autopct='%1.1f%%', startangle=140)
    plt.title('Mis Gastos por Categoría 💰')
    plt.axis('equal')  # Para que salga redondo perfecto
    
    # 5. Mostrar
    print("Generando gráfico...")
    plt.show()