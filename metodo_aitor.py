import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="A.I.T.O.R. 8.0 - Money Manager", layout="wide")

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
    stock = yf.Ticker(ticker_input); inf = stock.info
    nombre_emp = inf.get('longName', 'Ticker no detectado')
    p_mercado = inf.get('regularMarketPrice', inf.get('previousClose', 0.0))
    # Buscamos la previsión de crecimiento (Forward)
    prevision_eps = inf.get('earningsGrowth', 0) or inf.get('revenueGrowth', 0) or 0
    if prevision_eps > 1.0: prevision_eps = 0.15 # Filtro de seguridad contra errores de API
except: pass

st.sidebar.subheader(f"🏢 {nombre_emp}")
st.sidebar.markdown("---")

# 3. FILTROS LIBRO BLANCO (VISIÓN 3 AÑOS)
st.sidebar.header("📚 Calidad (Libro
