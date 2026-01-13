import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Trading vs Vida", layout="wide")

st.title("⚖️ Balance: Trading vs Vida Real")

# --- CONEXIÓN BD ---
def get_data():
    conn = sqlite3.connect('finanzas.db')
    # Traemos gastos
    gastos = pd.read_sql_query("SELECT * FROM movimientos WHERE tipo='gasto'", conn)
    # Traemos historial de trading (si existe, sino creamos tabla al vuelo)
    conn.execute('''CREATE TABLE IF NOT EXISTS trading_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT,
                    resultado REAL,
                    nota TEXT)''')
    trading = pd.read_sql_query("SELECT * FROM trading_results", conn)
    conn.close()
    return gastos, trading

# --- BARRA LATERAL: REGISTRAR RESULTADO (Día/Semana) ---
st.sidebar.header("📝 Cierre de Sesión")
with st.sidebar.form("trading_form"):
    fecha_t = st.date_input("Fecha")
    resultado = st.number_input("Profit/Loss del día ($)", step=10.0)
    nota = st.text_input("Nota (Ej: NFP, XAUUSD)")
    
    submit = st.form_submit_button("Registrar Resultado")
    if submit:
        conn = sqlite3.connect('finanzas.db')
        conn.execute("INSERT INTO trading_results (fecha, resultado, nota) VALUES (?, ?, ?)", 
                     (fecha_t, resultado, nota))
        conn.commit()
        conn.close()
        st.success("Guardado")
        st.rerun()

# --- LÓGICA DEL DASHBOARD ---
gastos_df, trading_df = get_data()

# Filtro de Mes Actual (Simple)
fecha_actual = pd.Timestamp.now()
mes_actual = fecha_actual.strftime('%Y-%m')

# Procesar Gastos
if not gastos_df.empty:
    gastos_df['fecha'] = pd.to_datetime(gastos_df['fecha'])
    gastos_mes = gastos_df[gastos_df['fecha'].dt.strftime('%Y-%m') == mes_actual]
    total_gastos = gastos_mes['monto'].sum()
else:
    total_gastos = 0

# Procesar Trading
total_profit = 0
if not trading_df.empty:
    trading_df['fecha'] = pd.to_datetime(trading_df['fecha'])
    trading_mes = trading_df[trading_df['fecha'].dt.strftime('%Y-%m') == mes_actual]
    total_profit = trading_mes['resultado'].sum()

# --- VISUALIZACIÓN ---

# 1. TARJETAS PRINCIPALES
c1, c2, c3 = st.columns(3)
c1.metric("📉 Gastos de Este Mes", f"${total_gastos:,.2f}")
c2.metric("📈 Profit Trading Mes", f"${total_profit:,.2f}", 
          delta_color="normal", delta=f"{total_profit - total_gastos:,.2f} Netos")

# Cálculo de Cobertura
cobertura = 0
if total_gastos > 0:
    cobertura = (total_profit / total_gastos) * 100
    # Tope visual para el gráfico (max 100 o un poco más)
    val_grafico = min(cobertura, 200) 

# 2. EL VELOCÍMETRO DE LIBERTAD FINANCIERA
st.subheader(f"Nivel de Libertad Financiera ({mes_actual})")

fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = cobertura,
    title = {'text': "% de Gastos Cubiertos por Trading"},
    gauge = {
        'axis': {'range': [None, 150]},
        'bar': {'color': "darkblue"},
        'steps' : [
            {'range': [0, 50], 'color': "red"},
            {'range': [50, 99], 'color': "orange"},
            {'range': [100, 150], 'color': "green"}],
        'threshold' : {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': 100}
    }
))
st.plotly_chart(fig, use_container_width=True)

# 3. MENSAJE INTELIGENTE
if cobertura >= 100:
    st.balloons()
    st.success(f"🚀 ¡FELICIDADES! Tu trading ha pagado tu vida este mes. Te sobran ${total_profit - total_gastos:,.2f} para reinvertir o darte un gusto.")
elif cobertura > 0:
    st.warning(f"⚠️ Vas bien. Tu trading ha pagado el {cobertura:.1f}% de tus facturas. Te faltan ${total_gastos - total_profit:,.2f} para cubrir el mes.")
else:
    st.error("📉 Estás en negativo este mes. Cuidado con la gestión de riesgo.")

# 4. TABLA DE RESULTADOS
st.markdown("---")
st.subheader("Historial de Operativa")
if not trading_df.empty:
    st.dataframe(trading_df.sort_values(by='fecha', ascending=False), use_container_width=True)