import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="A.I.T.O.R. 8.2 - Quant Final", layout="wide")

# Parámetros Maestros
CAPITAL_TOTAL = 277000.0
DIAS_FIB = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]
COL_DATABASE = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto", "Acciones", "Inversion"]
for i in range(1, 6):
    COL_DATABASE.extend([f"S{i}_Dias", f"W{i}", f"R{i}"])

# Conexión a Base de Datos (Google Sheets)
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    existing_data = conn.read(worksheet="Sheet1", ttl=5)
except:
    existing_data = pd.DataFrame(columns=COL_DATABASE)

# --- 2. BUSCADOR INTELIGENTE (VISIÓN 3 AÑOS) ---
st.sidebar.header("🔍 Buscador de Activos")
ticker = st.sidebar.text_input("TICKER", "MSFT").upper()

nombre_emp, p_mercado, prevision_3y = "Buscando...", 0.0, 0.0
try:
    stock = yf.Ticker(ticker)
    inf = stock.info
    nombre_emp = inf.get('longName', 'Ticker no detectado')
    p_mercado = inf.get('regularMarketPrice', inf.get('previousClose', 0.0))
    # Extraemos previsión de crecimiento de beneficios (Forward 3-5Y)
    prevision_3y = inf.get('earningsGrowth', 0) or inf.get('revenueGrowth', 0) or 0
    if prevision_3y > 1.0: prevision_3y = 0.15 # Filtro de seguridad
except: pass

st.sidebar.subheader(f"🏢 {nombre_emp}")
st.sidebar.markdown("---")

# 3. LIBRO BLANCO (CALIDAD)
st.sidebar.header("📚 Calidad (Libro Blanco)")
if prevision_3y > 0:
    st.sidebar.success(f"🎯 Previsión 3Y: {prevision_3y*100:.1f}%")

op_eps = ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"]
idx_auto = 3 if prevision_3y > 0.25 else 2 if prevision_3y > 0.15 else 1 if prevision_3y > 0.10 else 0
eps_val = st.sidebar.selectbox("Crecimiento EPS (Previsión)", op_eps, index=idx_auto)

pts_eps = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}[eps_val]
c_inst = st.sidebar.checkbox("Institucional (Smart Money)", value=True)
c_sect = st.sidebar.checkbox("Líder Sector (Fuerza Relativa)", value=True)

bonus_calidad = pts_eps + (10 if c_inst else 0) + (10 if c_sect else 0)
plus_ev = bonus_calidad / 7

# 4. GESTIÓN DE CAPITAL (277.000 €)
st.sidebar.header("💰 Gestión de Capital")
riesgo_pct = st.sidebar.slider("Riesgo por operación (%)", 0.5, 3.0, 1.0, step=0.5)
p_buy = st.sidebar.number_input("Precio de Compra $", value=float(p_mercado))
p_sl = st.sidebar.number_input("Precio Stop Loss $", value=float(p_buy * 0.95))

# --- 5. CUERPO PRINCIPAL ---
tab1, tab2 = st.tabs(["🔍 Escáner Fractal", "📊 Auditoría & Gestión"])

with tab1:
    st.title(f"🚀 Análisis Cuántico: {ticker}")
    
    # Selección de Sistemas
    st.sidebar.header("🧬 Sistemas Fractalidad")
    def_fibs = [1, 3, 8, 14, 21]
    s_dias = []
    for i in range(5):
        d = st.sidebar.selectbox(f"S{i+1}", DIAS_FIB, index=DIAS_FIB.index(def_fibs[i]), key=f"d{i}")
        s_dias.append(d)

    ev_list, wr_list, rat_list, est_list = [], [], [], []
    cols = st.columns(5)
    for i, d in enumerate(s_dias):
