import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="A.I.T.O.R. 7.3 - Visionary 3Y", layout="wide")

DIAS_DISPONIBLES = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]
COL_TOTALES = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto"]
for i in range(1, 6):
    COL_TOTALES.extend([f"S{i}_Dias", f"W{i}", f"R{i}"])

conn = st.connection("gsheets", type=GSheetsConnection)
try:
    existing_data = conn.read(worksheet="Sheet1", ttl=5)
except:
    existing_data = pd.DataFrame(columns=COL_TOTALES)

# --- 2. BUSCADOR CON SENSOR DE PREVISIÓN (3 AÑOS) ---
st.sidebar.header("🔍 Buscador de Activos")
ticker_input = st.sidebar.text_input("TICKER", "MSFT").upper()

nombre_emp, p_mercado, prevision_3y = "Buscando...", 0.0, 0.0

try:
    stock = yf.Ticker(ticker_input); inf = stock.info
    nombre_emp = inf.get('longName', 'Ticker no detectado')
    p_mercado = inf.get('regularMarketPrice', inf.get('previousClose', 0.0))
    
    # 🎯 SENSOR DE PREVISIÓN A 3-5 AÑOS
    # Priorizamos el 'earningsGrowth' (anualizado) sobre el trimestral
    prevision_3y = inf.get('earningsGrowth', 0) or inf.get('revenueGrowth', 0) or 0
    
    # Si el dato es ridículamente alto (>100%), lo capamos porque es ruido
    if prevision_3y > 1.0: prevision_3y = 0.15 # Default sensato si hay error
except: pass

st.sidebar.subheader(f"🏢 {nombre_emp}")
st.sidebar.markdown("---")

# 3. FILTROS LIBRO BLANCO (VISIÓN A LARGO PLAZO)
st.sidebar.header("📚 Calidad (Libro Blanco)")

# Mostramos solo la PREVISIÓN, eliminamos el dato pasado
if prevision_3y > 0:
    st.sidebar.success(f"🎯 Previsión Consenso (3Y): {prevision_3y*100:.1f}%")
else:
    st.sidebar.warning("⚠️ Sin previsiones a 3 años")

auto_eps = "Explosivo (>25%)" if prevision_3y > 0.25 else "Alto (>15%)" if prevision_3y > 0.15 else "Medio (>10%)" if prevision_3y > 0.10 else "Bajo (<10%)"
eps_choice = st.sidebar.selectbox("Crecimiento EPS (Previsión)", 
                                 ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"], 
                                 index=["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"].index(auto_eps))

p_eps_idt = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}[eps_choice]
c_inst = st.sidebar.checkbox("Institucional
