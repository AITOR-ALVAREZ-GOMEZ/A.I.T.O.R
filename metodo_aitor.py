import streamlit as st
import pandas as pd
import yfinance as yf

# 1. CONFIGURACIÓN
st.set_page_config(page_title="A.I.T.O.R. 4.9 - The Ultimate Legend", layout="wide")

COLUMNAS = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto"]
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=COLUMNAS)

# --- 2. BUSCADOR INTELIGENTE ---
st.sidebar.header("🔍 Buscador (Usa el Ticker)")
ticker_input = st.sidebar.text_input("TICKER (ej. MSFT, CRDO, NVDA)", "MSFT").upper()

# Variables de auto-detección
auto_eps, auto_inst, auto_sector = "Bajo (<10%)", False, False
nombre_empresa, precio_mercado = "Buscando...", 0.0

try:
    stock = yf.Ticker(ticker_input)
    info = stock.info
    nombre_empresa = info.get('longName', 'Ticker no detectado')
    precio_mercado = info.get('regularMarketPrice', info.get('previousClose', 0.0))
    
    # Auto-detección Libro Blanco
    growth = info.get('earningsQuarterlyGrowth', 0) or 0
    if growth > 0.25: auto_eps = "Explosivo (>25%)"
    elif growth > 0.15: auto_eps = "Alto (>15%)"
    elif growth > 0.10: auto_eps = "Medio (>10%)"
    
    inst_percent = info.get('heldPercentInstitutions', 0) or 0
    if inst_percent > 0.30: auto_inst = True
    
    hist = stock.history(period="6mo")
    if len(hist) > 0:
        rendimiento = (hist['Close'][-1] / hist['Close'][0]) - 1
        if rendimiento > 0.15: auto_sector = True
except:
    st.sidebar.error("⚠️ TICKER INVÁLIDO. Usa MSFT, no Microsoft.")

st.sidebar.subheader(f"🏢 {nombre_empresa}")
st.sidebar.write(f"**Precio Actual:** {precio_mercado} $")
st.sidebar.markdown("---")

# 3. FILTROS LIBRO BLANCO
st.sidebar.header("📚 Calidad (Libro Blanco)")
eps_choice = st.sidebar.selectbox("Crecimiento EPS", 
                                 ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"], 
                                 index=["Bajo (<10%)", "Medio (>10%)", "
