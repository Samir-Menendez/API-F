import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(page_title="Mi Sistema Financiero", layout="wide", page_icon="💰")

# 2. Función para cargar datos
def cargar_datos():
    conn = sqlite3.connect('finanzas.db')
    # Cargamos todo
    df = pd.read_sql_query("SELECT * FROM movimientos", conn)
    conn.close()
    return df

# Título y recarga
st.title("📊 Control de Finanzas Personal")
st.markdown("---")

# 3. Carga y Procesamiento
df = cargar_datos()

if df.empty:
    st.warning("⚠️ No hay datos registrados aún. ¡Usa tu iPhone para agregar movimientos!")
else:
    # Convertir columnas
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['monto'] = pd.to_numeric(df['monto'])
    
    # 4. FILTROS (Barra lateral)
    st.sidebar.header("Filtros")
    # Filtro de Mes
    df['mes'] = df['fecha'].dt.to_period('M')
    meses_disponibles = sorted(df['mes'].unique().astype(str), reverse=True)
    mes_seleccionado = st.sidebar.selectbox("Selecciona Mes", ["Todos"] + list(meses_disponibles))
    
    # Aplicar filtro si no es "Todos"
    df_filtrado = df.copy()
    if mes_seleccionado != "Todos":
        df_filtrado = df[df['fecha'].dt.to_period('M').astype(str) == mes_seleccionado]

    # 5. KPIs (Indicadores Clave)
    # Calculamos totales
    ingresos = df_filtrado[df_filtrado['tipo'] == 'ingreso']['monto'].sum()
    gastos = df_filtrado[df_filtrado['tipo'] == 'gasto']['monto'].sum()
    balance = ingresos - gastos

    # Mostramos las tarjetas de métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("🟢 Ingresos Totales", f"${ingresos:,.2f}")
    col2.metric("🔴 Gastos Totales", f"${gastos:,.2f}")
    col3.metric("💰 Balance Neto", f"${balance:,.2f}", delta_color="normal")

    st.markdown("---")

    # 6. GRÁFICOS
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Distribución de Gastos")
        datos_gastos = df_filtrado[df_filtrado['tipo'] == 'gasto']
        if not datos_gastos.empty:
            # Gráfico de Donut interactivo
            fig_gastos = px.pie(datos_gastos, values='monto', names='categoria', hole=0.4)
            st.plotly_chart(fig_gastos, use_container_width=True)
        else:
            st.info("No hay gastos en este periodo.")

    with c2:
        st.subheader("Ingresos vs Gastos")
        # Agrupar por tipo
        resumen = df_filtrado.groupby('tipo')['monto'].sum().reset_index()
        if not resumen.empty:
            fig_barras = px.bar(resumen, x='tipo', y='monto', color='tipo', 
                                color_discrete_map={'ingreso':'green', 'gasto':'red'})
            st.plotly_chart(fig_barras, use_container_width=True)
        else:
            st.info("No hay movimientos.")

    # 7. TABLA DE DETALLES
    st.subheader("📝 Últimos Movimientos")
    st.dataframe(
        df_filtrado[['fecha', 'tipo', 'categoria', 'monto', 'nota']].sort_values(by='fecha', ascending=False),
        use_container_width=True
    )