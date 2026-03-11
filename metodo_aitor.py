import streamlit as st
import pandas as pd
import yfinance as yf

# Configuración de página
st.set_page_config(page_title="A.I.T.O.R. 4.0 - Master Score", layout="wide")

# Inicializar Base de Datos
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=[
        "Ticker", "Tier", "Esperanza Final", "IDT Puntos", "ITE %", "Veredicto"
    ])

# --- 1. BARRA LATERAL (BUSCADOR Y CALIDAD) ---
st.sidebar.header("🔍 Buscador de Activos")
ticker_input = st.sidebar.text_input("TICKER", "CRDO").upper()

nombre_empresa = "Cargando..."
precio_mercado = 0.0
try:
    stock_data = yf.Ticker(ticker_input)
    info_json = stock_data.info
    nombre_empresa = info_json.get('longName', 'Ticker no detectado')
    precio_mercado = info_json.get('regularMarketPrice', info_json.get('previousClose', 0.0))
except:
    pass

st.sidebar.subheader(f"🏢 {nombre_empresa}")
st.sidebar.markdown("---")

st.sidebar.header("📚 Calidad (Libro Blanco)")
# Puntos de Libro Blanco: Influyen en la Esperanza Final y en el IDT
eps_choice = st.sidebar.selectbox("Crecimiento EPS", 
                                 ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"], index=3)

# Puntos IDT (Escala Aitor)
pts_eps_idt = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}[eps_choice]
# Peso en EV (Para no desvirtuar la estadística, cada 10 pts IDT = 1.0 punto de EV extra)
plus_ev_eps = pts_eps_idt / 10

c_inst = st.sidebar.checkbox("Institucional (Smart Money)", value=True)
c_sector = st.sidebar.checkbox("Líder Sector (RS > 90)", value=True)

# Plus total de Esperanza (Máximo +3.5 si todo es perfecto)
plus_ev_total = plus_ev_eps + (1.0 if c_inst else 0) + (1.0 if c_sector else 0)

st.sidebar.header("🎯 Control de Entrada")
p_gatillo = st.sidebar.number_input("Precio Señal Gatillo $", value=float(precio_mercado))
p_entrada = st.sidebar.number_input("Precio Compra Deseado $", value=float(precio_mercado))

st.sidebar.header("🧬 Sistemas Fractalidad")
secuencia = [st.sidebar.number_input(f"Sistema {i+1}", value=v, key=f"s{i}") for i, v in enumerate([1, 3, 8, 14, 21])]

# --- 2. INTERFAZ PRINCIPAL ---
tab_esc, tab_car, tab_per = st.tabs(["🔍 Escáner Integral", "💼 Cartera", "📊 Performance"])

with tab_esc:
    st.title(f"🚀 Análisis de Esperanza: {ticker_input}")
    
    ev_list, wr_list, estados = [], [], []
