import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf  # El buscador de Wall Street
from datetime import datetime

st.set_page_config(page_title="A.I.T.O.R. 2.1 - Buscador Pro", layout="wide")

# --- BASE DE DATOS TEMPORAL ---
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=["Ticker", "Nombre", "Precio", "Tier", "EV_Pond", "IDT", "ITE", "Verdict"])

# --- BARRA LATERAL: BUSCADOR Y CONFIGURACIÓN ---
st.sidebar.header("⚙️ Configuración del Motor")
ticker_input = st.sidebar.text_input("BUSCADOR DE TICKER", "CRDO").upper()

# Motor de búsqueda en tiempo real
nombre_empresa = "Buscando..."
precio_actual = 0.0
try:
    stock = yf.Ticker(ticker_input)
    info = stock.info
    nombre_empresa = info.get('longName', 'Ticker no detectado')
    # Intentamos obtener el precio actual o el de cierre anterior
    precio_actual = info.get('regularMarketPrice', info.get('previousClose', 0.0))
except:
    st.sidebar.warning("Conexión limitada con Wall Street.")

st.sidebar.subheader(f"🏢 {nombre_empresa}")
st.sidebar.write(f"**Precio Actual:** {precio_actual} $")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧬 Secuencia Fractal")
d1 = st.sidebar.number_input("Gatillo (Día X)", value=1)
d2 = st.sidebar.number_input("Escudo (Día Y)", value=3)
d3 = st.sidebar.number_input("Muro (Día Z)", value=8)
d4 = st.sidebar.number_input("Ancla 1 (Día W)", value=13)
d5 = st.sidebar.number_input("Ancla 2 (Día K)", value=21)
secuencia = [d1, d2, d3, d4, d5]

# --- PANELES PRINCIPALES ---
tab1, tab2, tab3 = st.tabs(["🔍 Escáner Dinámico", "💼 Mi Cartera", "📊 Performance"])

with tab1:
    st.title(f"🚀 Análisis de {ticker_input}")
    st.caption(f"Configuración de Fibonacci: {secuencia}")

    # MATRIZ DE ENTRADA EN 5 COLUMNAS
    ev_list = []
    wr_list = []
    cols_fibo = st.columns(5)
    for i, d in enumerate(secuencia):
        with cols_fibo[i]:
            st.markdown(f"**Sistema {d}D**")
            wr = st.number_input(f"WR% {d}D", 0, 100, 50, key=f"wr_{d}") / 100
            ratio = st.number_input(f"Ratio {d}D", 0.0, 50.0, 2.0, key=f"r_{d}")
            # Fórmula LaTeX: $EV = (WR \cdot Ratio) - ((1-WR) \cdot 1)$
            ev_ind = (wr * ratio) - ((1 - wr) * 1)
            ev_list.append(ev_ind)
            wr_list.append(wr)

    # CÁLCULOS ALGORÍTMICOS
    ev_pond = sum(ev_list) / 5
    tier = "👑 TIER S" if ev_pond >= 10 else "🟢 TIER A" if ev_pond >= 5 else "🔴 DESCARTE"
    
    st.markdown("---")
    
    # CORRECCIÓN DE ERROR: Definición segura de columnas para estado de disparo
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        gat_azul = st.checkbox("Gatillo AZUL", value=True)
    with col_b:
        sistemas_azul = st.slider("Sistemas >1D en AZUL", 0, 4, 3)
    with col_c:
        p_entrada = st.number_input("Precio Entrada $", value=float(precio_actual))
    with col_d:
        p_stop = st.number_input("Precio Stop $", value=float(precio_actual * 0.95))

    # Algoritmo IDT e ITE
    wr_gatillo = wr_list[0] * 100
    idt = wr_gatillo + (15 if "TIER S" in tier else 0) + (sistemas_azul * 10) + (10 if gat_azul else 0)
    ite = ((p_entrada - p_stop) / p_stop) * 100 if p_stop > 0 else 0

    # VERDICTO VISUAL
    if idt >= 100 and ite <= 5: 
        v_text, v_col = "🔥 COMPRA OBLIGATORIA", "#00ffcc"
    elif idt >= 85 and ite <= 8: 
        v_text, v_col = "🟡 COMPRA TÁCTICA", "#ffcc00"
    else: 
        v_text, v_col = "🚫 ARMA BLOQUEADA", "#ff4b4b"

    st.markdown(f"<h2 style='text-align:center; color:{v_col};'>{v_text}</h2>", unsafe_allow_html=True)

    if st.button("💾 Guardar en Ranking"):
        nuevo = {
            "Ticker": ticker_input, "Nombre": nombre_empresa, "Precio": precio_actual,
            "Tier": tier, "EV_Pond": round(ev_pond, 2), "IDT": round(idt, 1), 
            "ITE": round(ite, 2), "Verdict": v_text
        }
        st.session_state.analisis = pd.concat([st.session_state.analisis, pd.DataFrame([nuevo])]).drop_duplicates('Ticker', keep='last')

    st.subheader("📋 Ranking de Oportunidades")
    st.dataframe(st.session_state.analisis.sort_values("IDT", ascending=False), use_container_width=True)
