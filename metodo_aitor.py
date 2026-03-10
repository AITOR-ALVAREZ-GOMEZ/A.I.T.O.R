import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf  # Importamos el buscador de Wall Street
from datetime import datetime

st.set_page_config(page_title="A.I.T.O.R. 2.1 - Searcher Edition", layout="wide")

# --- BASE DE DATOS TEMPORAL ---
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=["Ticker", "Nombre", "Precio", "Tier", "EV_Pond", "IDT", "ITE", "Verdict"])

st.sidebar.header("⚙️ Configuración del Motor")
ticker_input = st.sidebar.text_input("BUSCADOR DE TICKER", "CRDO").upper()

# --- BUSCADOR AUTOMÁTICO ---
nombre_empresa = "Desconocido"
precio_actual = 0.0
try:
    stock = yf.Ticker(ticker_input)
    info = stock.info
    nombre_empresa = info.get('longName', 'Ticker no encontrado')
    precio_actual = info.get('regularMarketPrice', info.get('previousClose', 0.0))
except:
    st.sidebar.warning("No se pudo conectar con el buscador para este Ticker.")

st.sidebar.markdown(f"**Empresa:** {nombre_empresa}")
st.sidebar.markdown(f"**Precio Actual:** {precio_actual} $")

# --- DEFINICIÓN DE SECUENCIA ---
st.sidebar.markdown("### 🧬 Define tu Secuencia Fractal")
d1 = st.sidebar.number_input("Gatillo (Día X)", value=1)
d2 = st.sidebar.number_input("Escudo (Día Y)", value=3)
d3 = st.sidebar.number_input("Muro (Día Z)", value=8)
d4 = st.sidebar.number_input("Ancla 1 (Día W)", value=13)
d5 = st.sidebar.number_input("Ancla 2 (Día K)", value=21)
secuencia_elegida = [d1, d2, d3, d4, d5]

# --- INTERFAZ PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["🔍 Escáner Dinámico", "💼 Cartera", "📊 Performance"])

with tab1:
    st.title(f"🚀 Análisis de {nombre_empresa} ({ticker_input})")
    
    # MATRIZ DE ENTRADA
    ev_list = []
    data_points = {}
    cols_fibo = st.columns(5)
    
    for i, d in enumerate(secuencia_elegida):
        with cols_fibo[i]:
            st.markdown(f"**Sistema {d}D**")
            wr = st.number_input(f"WR% {d}D", 0, 100, 50, key=f"wr_{d}") / 100
            ratio = st.number_input(f"Ratio {d}D", 0.0, 50.0, 2.0, key=f"r_{d}")
            ev_ind = (wr * ratio) - ((1 - wr) * 1)
            ev_list.append(ev_ind)
            data_points[d] = wr

    # CÁLCULOS
    ev
