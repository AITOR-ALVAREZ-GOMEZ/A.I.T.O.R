import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="A.I.T.O.R. 3.8 - Esperanza Integral", layout="wide")

# Inicializar Base de Datos
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=[
        "Ticker", "Tier", "Esperanza Final", "IDT Puntos", "ITE %", "Veredicto"
    ])

# --- 1. BARRA LATERAL (FILTROS QUE AHORA SÍ SUMAN) ---
st.sidebar.header("🔍 Buscador")
ticker_input = st.sidebar.text_input("TICKER", "CRDO").upper()

nombre_empresa = "Cargando..."
precio_mercado = 0.0
try:
    stock_data = yf.Ticker(ticker_input)
    nombre_empresa = stock_data.info.get('longName', 'Ticker no detectado')
    precio_mercado = stock_data.info.get('regularMarketPrice', stock_data.info.get('previousClose', 0.0))
except: pass

st.sidebar.subheader(f"🏢 {nombre_empresa}")
st.sidebar.markdown("---")

st.sidebar.header("📚 Calidad (Libro Blanco)")
# Los puntos del libro blanco ahora se dividen por 5 para sumarse al EV
eps_choice = st.sidebar.selectbox("Crecimiento EPS", 
                                 ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"], index=3)
puntos_eps = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}[eps_choice]

c_inst = st.sidebar.checkbox("Institucional (Smart Money)", value=True)
c_sector = st.sidebar.checkbox("Líder Sector (RS > 90)", value=True)

# Puntos totales de calidad (Máximo 35)
puntos_libro = puntos_eps + (10 if c_inst else 0) + (10 if c_sector else 0)
# Multiplicador de Esperanza: Cada 5 puntos de calidad suman 1 punto a la Esperanza Final
plus_esperanza = puntos_libro / 5

st.sidebar.header("🎯 Control de Entrada")
p_gatillo = st.sidebar.number_input("Precio Señal $", value=float(precio_mercado))
p_entrada = st.sidebar.number_input("Precio Compra $", value=float(precio_mercado))

st.sidebar.header("🧬 Sistemas Fractalidad")
secuencia = [st.sidebar.number_input(f"Sistema {i+1}", value=v, key=f"s{i}") for i, v in enumerate([1, 3, 8, 14, 21])]

# --- 2. INTERFAZ PRINCIPAL ---
tab_esc, tab_car, tab_per = st.tabs(["🔍 Escáner Integral", "💼 Cartera", "📊 Performance"])

with tab_esc:
    st.title(f"🚀 Análisis de {ticker_input}")
    
    ev_list, wr_list, estados = [], [], []
    cols = st.columns(5)
    
    for i, s_val in enumerate(secuencia):
        with cols[i]:
            st.markdown(f"### Sist. {s_val}D")
            wr = st.number_input(f"WR% {s_val}D", 0, 100, 50, key=f"w{i}")
            ratio = st.number_input(f"Ratio {s_val}D", 0.0, 100.0, 2.0, key=f"r{i}")
            estado = st.radio(f"Estado {s_val}D", ["🔴 Venta", "🔵 Compra"], key=f"e{i}")
            
            wr_f = wr / 100
            ev_ind = round((wr_f * ratio) - ((1 - wr_f) * 1), 2)
            ev_list.append(ev_ind); wr_list.append(wr); estados.append(estado)
            st.metric("EV Matemático", f"{ev_ind}")

    # --- CÁLCULO DE ESPERANZA FINAL (EL CORAZÓN DEL MÉTODO) ---
    ev_matematico = sum(ev_list) / 5
    # La Esperanza Final es la Matemática + el Plus por Calidad del Libro Blanco
    esperanza_final = round(ev_matematico + plus_esperanza, 2)
    
    # Clasificación Tier basada en la Esperanza FINAL (Ajustada por calidad)
    tier_label = "👑 TIER S" if esperanza_final >= 10.0 else "🟢 TIER A" if esperanza_final >= 5.0 else "🔴 DESCARTE"

    # Puntos IDT
    dist_gat = ((p_entrada - p_gatillo) / p_gatillo) * 100 if p_gatillo > 0 else 0
    penalizacion = 30 if dist_gat > 5.0 else 10 if dist_gat >= 2.0 else 0
    p_estruc = sum(1 for e in estados[1:] if "🔵" in e) * 10
    p_senal = 10 if "🔵" in estados[0] else 0
    
    # El IDT ahora premia la calidad a través del Tier S
    idt_total = wr_list[0] + (15 if "TIER S" in tier_label else 0) + p_estruc + p_senal - penalizacion

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.subheader("🧪 Esperanza Final")
        st.metric("A.I.T.O.R. SCORE", f"{esperanza_final}", f"+{plus_esperanza} por Calidad")
        st.caption(f"EV Matemático: {ev_matematico:.2f}")
    
    with m2:
        st.subheader("🎯 Potencial IDT")
        st.metric("PUNTUACIÓN", f"{idt_total} pts", f"-{penalizacion} Distancia" if penalizacion > 0 else None)
        
    with m3:
        st.subheader("🛡️ Riesgo")
        p_stop = st.
