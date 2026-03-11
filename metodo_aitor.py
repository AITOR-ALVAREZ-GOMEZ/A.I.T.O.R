import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="A.I.T.O.R. 8.3 - Final Solution", layout="wide")

CAPITAL_TOTAL = 277000.0
DIAS_FIB = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]
COL_DATABASE = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto", "Acciones", "Inversion"]
for i in range(1, 6):
    COL_DATABASE.extend([f"S{i}_Dias", f"W{i}", f"R{i}"])

conn = st.connection("gsheets", type=GSheetsConnection)
try:
    existing_data = conn.read(worksheet="Sheet1", ttl=5)
except:
    existing_data = pd.DataFrame(columns=COL_DATABASE)

# --- 2. BUSCADOR ---
st.sidebar.header("🔍 Buscador de Activos")
ticker = st.sidebar.text_input("TICKER", "MSFT").upper()

nombre_emp, p_mercado, prevision_3y = "Buscando...", 0.0, 0.0
try:
    stock = yf.Ticker(ticker); inf = stock.info
    nombre_emp = inf.get('longName', 'Ticker no detectado')
    p_mercado = inf.get('regularMarketPrice', inf.get('previousClose', 0.0))
    prevision_3y = inf.get('earningsGrowth', 0) or inf.get('revenueGrowth', 0) or 0
    if prevision_3y > 1.0: prevision_3y = 0.15 
except: pass

st.sidebar.subheader(f"🏢 {nombre_emp}")
st.sidebar.markdown("---")

# 3. CALIDAD (LIBRO BLANCO)
st.sidebar.header("📚 Calidad (Libro Blanco)")
if prevision_3y > 0:
    st.sidebar.success(f"🎯 Previsión 3Y: {prevision_3y*100:.1f}%")

op_eps = ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"]
idx_auto = 3 if prevision_3y > 0.25 else 2 if prevision_3y > 0.15 else 1 if prevision_3y > 0.10 else 0
eps_val = st.sidebar.selectbox("Expectativa Crecimiento", op_eps, index=idx_auto)

pts_eps = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}[eps_val]
c_inst = st.sidebar.checkbox("Manos Fuertes", value=True)
c_sect = st.sidebar.checkbox("Líder Sector", value=True)

plus_ev = (pts_eps + (10 if c_inst else 0) + (10 if c_sect else 0)) /
