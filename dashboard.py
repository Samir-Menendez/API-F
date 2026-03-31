import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv

st.set_page_config(page_title="Mi Sistema Financiero", layout="wide", page_icon="💰")
load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "finanzas.db"))
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", os.getenv("MY_API_TOKEN", "1234"))

def cargar_datos():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM movimientos", conn)
    conn.close()
    return df

st.title("📊 Control de Finanzas Personal")
st.caption(f"Base de datos activa: {DB_PATH}")
st.markdown("---")

# Autenticación del dashboard
if "auth_ok" not in st.session_state:
    st.session_state.auth_ok = False

if not st.session_state.auth_ok:
    st.subheader("🔐 Iniciar sesión")
    password_input = st.text_input("Contraseña", type="password")
    if st.button("Entrar", type="primary"):
        if password_input == DASHBOARD_PASSWORD:
            st.session_state.auth_ok = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")
    st.stop()

df = cargar_datos()

if df.empty:
    st.warning("⚠️ No hay datos registrados aún. ¡Usa tu iPhone para agregar movimientos!")
else:
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['monto'] = pd.to_numeric(df['monto'])
    df['tipo'] = df['tipo'].astype(str).str.strip().str.lower()
    
    # Filtros
    st.sidebar.header("Filtros")
    df['mes'] = df['fecha'].dt.to_period('M')
    meses_disponibles = sorted(df['mes'].unique().astype(str), reverse=True)
    mes_seleccionado = st.sidebar.selectbox("Selecciona Mes", ["Todos"] + list(meses_disponibles))
    tipo_seleccionado = st.sidebar.multiselect(
        "Tipo de movimiento",
        options=sorted(df['tipo'].unique().tolist()),
        default=sorted(df['tipo'].unique().tolist())
    )
    top_n = st.sidebar.slider("Top categorías de gasto", min_value=3, max_value=15, value=7)
    
    df_filtrado = df.copy()
    if mes_seleccionado != "Todos":
        df_filtrado = df[df['fecha'].dt.to_period('M').astype(str) == mes_seleccionado]
    if tipo_seleccionado:
        df_filtrado = df_filtrado[df_filtrado['tipo'].isin(tipo_seleccionado)]

    # Resumen principal
    ingresos = df_filtrado[df_filtrado['tipo'] == 'ingreso']['monto'].sum()
    gastos = df_filtrado[df_filtrado['tipo'] == 'gasto']['monto'].sum()
    balance = ingresos - gastos

    col1, col2, col3 = st.columns(3)
    col1.metric("🟢 Ingresos Totales", f"${ingresos:,.2f}")
    col2.metric("🔴 Gastos Totales", f"${gastos:,.2f}")
    col3.metric("💰 Balance Neto", f"${balance:,.2f}", delta_color="normal")

    # Exportación del periodo filtrado
    csv_data = df_filtrado.sort_values(by='fecha', ascending=False).to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Descargar reporte CSV",
        data=csv_data,
        file_name=f"reporte_finanzas_{mes_seleccionado.lower().replace(' ', '_')}.csv",
        mime="text/csv"
    )

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Top categorías de gasto")
        datos_gastos = df_filtrado[df_filtrado['tipo'] == 'gasto']
        if not datos_gastos.empty:
            gastos_categoria = (
                datos_gastos.groupby('categoria', as_index=False)['monto']
                .sum()
                .sort_values(by='monto', ascending=False)
                .head(top_n)
            )
            fig_gastos = px.bar(
                gastos_categoria,
                x='monto',
                y='categoria',
                orientation='h',
                color='monto',
                color_continuous_scale='Blues'
            )
            fig_gastos.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_gastos, use_container_width=True)
        else:
            st.info("No hay gastos en este periodo.")

    with c2:
        st.subheader("Tendencia diaria (ingresos vs gastos)")
        tendencia = (
            df_filtrado.assign(dia=df_filtrado['fecha'].dt.date)
            .groupby(['dia', 'tipo'], as_index=False)['monto']
            .sum()
        )
        if not tendencia.empty:
            fig_barras = px.line(
                tendencia,
                x='dia',
                y='monto',
                color='tipo',
                markers=True,
                color_discrete_map={'ingreso': 'green', 'gasto': 'red'}
            )
            st.plotly_chart(fig_barras, use_container_width=True)
        else:
            st.info("No hay movimientos.")

    st.subheader("📝 Últimos Movimientos")
    st.dataframe(
        df_filtrado[['fecha', 'tipo', 'categoria', 'monto', 'nota']].sort_values(by='fecha', ascending=False),
        use_container_width=True
    )