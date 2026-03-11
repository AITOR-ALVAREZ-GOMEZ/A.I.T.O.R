import streamlit as st
import pandas as pd
import yfinance as yf

# 1. CONFIGURACIÓN
st.set_page_config(page_title="A.I.T.O.R. 4.7 - Ranking Limpio", layout="wide")

# NOMBRES DE COLUMNA DEFINITIVOS (Para evitar los 'None')
COLUMNAS = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto"]

if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=COLUMNAS)

# 2. SIDEBAR
st.sidebar.header("🔍 Buscador")
ticker_input = st.sidebar.text_input("TICKER", "CRDO").upper()

nombre_empresa, precio_mercado = "Buscando...", 0.0
try:
    stock = yf.Ticker(ticker_input)
    nombre_empresa = stock.info.get('longName', 'Ticker no detectado')
    precio_mercado = stock.info.get('regularMarketPrice', stock.info.get('previousClose', 0.0))
except: pass

st.sidebar.subheader(f"🏢 {nombre_empresa}")
st.sidebar.markdown("---")

# CALIDAD (LIBRO BLANCO)
st.sidebar.header("📚 Calidad (Libro Blanco)")
eps_choice = st.sidebar.selectbox("Crecimiento EPS", 
                                 ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"], index=3)

p_eps_idt = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}[eps_choice]
c_inst = st.sidebar.checkbox("Institucional (Smart Money)", value=True)
c_sector = st.sidebar.checkbox("Líder Sector (RS > 90)", value=True)

# Puntos de calidad para IDT y EV
plus_calidad_idt = p_eps_idt + (10 if c_inst else 0) + (10 if c_sector else 0)
plus_ev_final = plus_calidad_idt / 7 

st.sidebar.header("🎯 Control de Entrada")
p_gatillo = st.sidebar.number_input("Precio Gatillo $", value=float(precio_mercado))
p_entrada = st.sidebar.number_input("Precio Compra $", value=float(precio_mercado))

st.sidebar.header("🧬 Sistemas Fractalidad")
s_vals = [st.sidebar.number_input(f"Sistema {i+1}", value=v) for i, v in enumerate([1, 3, 8, 14, 21])]

# 3. INTERFAZ PRINCIPAL
tab1, tab2, tab3 = st.tabs(["🔍 Escáner Integral", "💼 Cartera", "📊 Performance"])

with tab1:
    st.title(f"🚀 Análisis de {ticker_input}")
    
    ev_list, wr_list, estados = [], [], []
    cols = st.columns(5)
    for i, s_val in enumerate(s_vals):
        with cols[i]:
            st.markdown(f"### Sist. {s_val}D")
            wr = st.number_input(f"WR% {s_val}D", 0, 100, 50, key=f"wr_{i}")
            ratio = st.number_input(f"Ratio {s_val}D", 0.0, 100.0, 2.0, key=f"rt_{i}")
            est = st.radio(f"Estado", ["🔴 Venta", "🔵 Compra"], key=f"es_{i}")
            ev_ind = round(((wr/100) * ratio) - ((1 - wr/100) * 1), 2)
            ev_list.append(ev_ind); wr_list.append(wr); estados.append(est)
            st.metric("EV Indiv.", f"{ev_ind}")

    # --- MOTOR DE CÁLCULO ---
    ev_puro = sum(ev_list) / 5
    ev_total = round(ev_puro + plus_ev_final, 2)
    
    if ev_total >= 10.0: tier = "👑 TIER S"
    elif ev_total >= 5.0: tier = "🟢 TIER A"
    else: tier = "🔴 DESCARTE"

    # IDT PUNTOS
    dist = ((p_entrada - p_gatillo) / p_gatillo) * 100 if p_gatillo > 0 else 0
    penal = 30 if dist > 5.0 else 10 if dist >= 2.0 else 0
    p_estruc = sum(1 for e in estados[1:] if "🔵" in e) * 10
    p_senal = 10 if "🔵" in estados[0] else 0
    idt_total = wr_list[0] + plus_calidad_idt + p_estruc + p_senal - penal

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.subheader("🧪 Esperanza Final")
        st.metric("EV TOTAL", f"{ev_total}", f"+{plus_ev_final:.2f} Calidad")
        st.caption("Umbral: Tier S ≥ 10 | Tier A ≥ 5")
        if ev_total < 5: st.error("⚠️ Calidad No Operable")

    with m2:
        st.subheader("🎯 Potencial IDT")
        st.metric("PUNTUACIÓN", f"{idt_total} pts", delta=f"+{plus_calidad_idt} Calidad")
        st.caption("Compra: Obligatoria ≥ 100 | Táctica ≥ 85")

    with m3:
        st.subheader("🛡️ Riesgo ITE")
        p_stop = st.number_input("Precio Stop $", value=float(p_entrada * 0.95))
        ite = round(((p_entrada - p_stop) / p_stop) * 100, 2) if p_stop > 0 else 0
        st.metric("TENSIÓN ITE", f"{ite}%")
        st.caption("Riesgo: Óptimo ≤ 5% | Límite ≤ 8%")
        if ite > 8: st.error("⚠️ Riesgo No Operable")

    # --- VERDICTO ---
    if ev_total < 5: v_txt, v_col = "🚫 NO OPERABLE (Calidad)", "#ff4b4b"
    elif ite > 8: v_txt, v_col = "🚫 NO OPERABLE (Riesgo)", "#ff4b4b"
    elif idt
