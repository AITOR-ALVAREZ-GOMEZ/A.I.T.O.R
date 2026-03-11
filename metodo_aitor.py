import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="A.I.T.O.R. 8.1 - Perfect Balance", layout="wide")

# Parámetros Maestros
CAPITAL_INICIAL = 277000.0
DIAS_DISPONIBLES = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]
COL_TOTALES = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto", "Acciones", "Inversion_Total"]
for i in range(1, 6):
    COL_TOTALES.extend([f"S{i}_Dias", f"W{i}", f"R{i}"])

conn = st.connection("gsheets", type=GSheetsConnection)
try:
    existing_data = conn.read(worksheet="Sheet1", ttl=5)
except:
    existing_data = pd.DataFrame(columns=COL_TOTALES)

# --- 2. BUSCADOR CON SENSOR DE PREVISIÓN ---
st.sidebar.header("🔍 Buscador de Activos")
ticker_input = st.sidebar.text_input("TICKER", "MSFT").upper()

nombre_emp, p_mercado, prevision_eps = "Buscando...", 0.0, 0.0
try:
    stock = yf.Ticker(ticker_input)
    inf = stock.info
    nombre_emp = inf.get('longName', 'Ticker no detectado')
    p_mercado = inf.get('regularMarketPrice', inf.get('previousClose', 0.0))
    # Buscamos la previsión de crecimiento (Forward) a largo plazo
    prevision_eps = inf.get('earningsGrowth', 0) or inf.get('revenueGrowth', 0) or 0
    if prevision_eps > 1.0: prevision_eps = 0.15 # Filtro contra ruido de la API
except: pass

st.sidebar.subheader(f"🏢 {nombre_emp}")
st.sidebar.markdown("---")

# 3. FILTROS LIBRO BLANCO (VISIÓN 3 AÑOS)
st.sidebar.header("📚 Calidad (Libro Blanco)")
if prevision_eps > 0:
    st.sidebar.success(f"🎯 Previsión Consenso (3Y): {prevision_eps*100:.1f}%")
else:
    st.sidebar.warning("⚠️ Sin datos de previsión")

opciones_eps = ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"]
auto_eps = "Explosivo (>25%)" if prevision_eps > 0.25 else "Alto (>15%)" if prevision_eps > 0.15 else "Medio (>10%)" if prevision_eps > 0.10 else "Bajo (<10%)"
eps_choice = st.sidebar.selectbox("Expectativa Crecimiento", opciones_eps, index=opciones_eps.index(auto_eps))

p_eps_idt = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}[eps_choice]
c_inst = st.sidebar.checkbox("Institucional (Smart Money)", value=True)
c_sector = st.sidebar.checkbox("Líder (Tendencia)", value=True)

plus_calidad_idt = p_eps_idt + (10 if c_inst else 0) + (10 if c_sector else 0)
plus_ev_final = plus_calidad_idt / 7 

# 4. GESTIÓN DE RIESGO
st.sidebar.header("💰 Gestión de Capital")
riesgo_per = st.sidebar.slider("Riesgo por operación (%)", 0.5, 5.0,
