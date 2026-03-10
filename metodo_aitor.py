import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="A.I.T.O.R. 2.2 - Control de Sistemas", layout="wide")

# --- BASE DE DATOS ---
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=["Ticker", "Nombre", "Precio", "Tier", "EV_Pond", "IDT", "ITE", "Verdict"])

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración del Motor")
ticker_input = st.sidebar.text_input("BUSCADOR DE TICKER", "CRDO").upper()

nombre_empresa = "Buscando..."
precio_actual = 0.0
try:
    stock = yf.Ticker(ticker_input)
    info = stock.info
    nombre_empresa = info.get('longName', 'Ticker no detectado')
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

# --- INTERFAZ PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["🔍 Escáner de Sistemas", "💼 Mi Cartera", "📊 Performance"])

with tab1:
    st.title(f"🚀 Análisis de {ticker_input}")
    
    # MATRIZ DE ENTRADA (ESTADÍSTICAS + ESTADO ACTUAL)
    ev_list = []
    wr_list = []
    estados = [] # Aquí guardaremos si están en Compra o Venta
    
    cols_fibo = st.columns(5)
    for i, d in enumerate(secuencia):
        with cols_fibo[i]:
            st.markdown(f"### Sistema {d}D")
            # 1. Datos estadísticos para el EV
            wr = st.number_input(f"WR% {d}D", 0, 100, 50, key=f"wr_{d}") / 100
            ratio = st.number_input(f"Ratio {d}D", 0.0, 50.0, 2.0, key=f"r_{d}")
            
            # 2. ESTADO ACTUAL (¡Lo que faltaba!)
            estado = st.radio(f"Estado {d}D", ["🔴 Venta", "🔵 Compra"], key=f"est_{d}", horizontal=True)
            
            ev_ind = (wr * ratio) - ((1 - wr) * 1)
            ev_list.append(ev_ind)
            wr_list.append(wr)
            estados.append(estado)

    # --- LÓGICA DE CÁLCULO ALGORÍTMICO ---
    
    # A. Calidad del Activo (Tier)
    ev_pond = sum(ev_list) / 5
    tier = "👑 TIER S" if ev_pond >= 10 else "🟢 TIER A" if ev_pond >= 5 else "🔴 DESCARTE"
    
    # B. Puntuación IDT (Suma de puntos real)
    # 1. Puntos por Win Rate del Gatillo
    puntos_wr_gatillo = wr_list[0] * 100
    
    # 2. Puntos por Tier
    puntos_tier = 15 if "TIER S" in tier else 0
    
    # 3. Puntos por Estructura (Sistemas 2, 3, 4 y 5 en Azul)
    sistemas_mayores_en_azul = sum(1 for e in estados[1:] if "🔵 Compra" in e)
    puntos_estructura = sistemas_mayores_en_azul * 10
    
    # 4. Puntos por Señal (Gatillo en Azul)
    gatillo_en_azul = 10 if "🔵 Compra" in estados[0] else 0
    
    idt = puntos_wr_gatillo + puntos_tier + puntos_estructura + gatillo_en_azul
    
    st.markdown("---")
    
    # C. Riesgo (ITE)
    col_a, col_b = st.columns(2)
    with col_a:
        p_entrada = st.number_input("Precio Entrada $", value=float(precio_actual))
    with col_b:
        p_stop = st.number_input("Precio Stop (Muro) $", value=float(precio_actual * 0.95))
    
    ite = ((p_entrada - p_stop) / p_stop) * 100 if p_stop > 0 else 0

    # --- VERDICTO FINAL ---
    if idt >= 100 and ite <= 5: 
        v_text, v_col = "🔥 COMPRA OBLIGATORIA", "#00ffcc"
    elif idt >= 85 and ite <= 8: 
        v_text, v_col = "🟡 COMPRA TÁCTICA", "#ffcc00"
    else: 
        v_text, v_col = "🚫 ARMA BLOQUEADA", "#ff4b4b"

    st.markdown(f"<h2 style='text-align:center; color:{v_col};'>{v_text}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>Puntuación Total: <b>{idt:.1f} Puntos</b> | Riesgo ITE: <b>{ite:.2f}%</b></p>", unsafe_allow_html=True)

    if st.button("💾 Guardar en Ranking"):
        nuevo = {
            "Ticker": ticker_input, "Nombre": nombre_empresa, "Precio": precio_actual,
            "Tier": tier, "EV_Pond": round(ev_pond, 2), "IDT": round(idt, 1), 
            "ITE": round(ite, 2), "Verdict": v_text
        }
        st.session_state.analisis = pd.concat([st.session_state.analisis, pd.DataFrame([nuevo])]).drop_duplicates('Ticker', keep='last')

    st.subheader("📋 Ranking de Oportunidades")
    st.dataframe(st.session_state.analisis.sort_values("IDT", ascending=False), use_container_width=True)
