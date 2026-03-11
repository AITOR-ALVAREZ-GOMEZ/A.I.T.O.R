import streamlit as st
import pandas as pd
import yfinance as yf

# 1. CONFIGURACIÓN
st.set_page_config(page_title="A.I.T.O.R. 4.8 - Intelligent Scanner", layout="wide")

COLUMNAS = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto"]
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=COLUMNAS)

# --- 2. EL BUSCADOR INTELIGENTE ---
st.sidebar.header("🔍 Buscador (Usa el Ticker)")
ticker_input = st.sidebar.text_input("TICKER (ej. MSFT, CRDO, AAPL)", "MSFT").upper()

# Variables de auto-detección
auto_eps = "Bajo (<10%)"
auto_inst = False
auto_sector = False
nombre_empresa, precio_mercado = "Buscando...", 0.0

try:
    stock = yf.Ticker(ticker_input)
    info = stock.info
    nombre_empresa = info.get('longName', 'Ticker no detectado')
    precio_mercado = info.get('regularMarketPrice', info.get('previousClose', 0.0))
    
    # AUTO-DETECCIÓN LIBRO BLANCO
    growth = info.get('earningsQuarterlyGrowth', 0) or 0
    if growth > 0.25: auto_eps = "Explosivo (>25%)"
    elif growth > 0.15: auto_eps = "Alto (>15%)"
    elif growth > 0.10: auto_eps = "Medio (>10%)"
    
    inst_percent = info.get('heldPercentInstitutions', 0) or 0
    if inst_percent > 0.30: auto_inst = True # Más del 30% es presencia fuerte
    
    # Estimación de Liderazgo (Simplificada: si sube más que el SPY en 6 meses)
    hist = stock.history(period="6mo")
    if len(hist) > 0:
        rendimiento = (hist['Close'][-1] / hist['Close'][0]) - 1
        if rendimiento > 0.15: auto_sector = True # Umbral de fuerza relativa
        
except:
    st.sidebar.warning("Introduce un Ticker válido (ej: MSFT)")

st.sidebar.subheader(f"🏢 {nombre_empresa}")
st.sidebar.write(f"**Precio:** {precio_mercado} $")
st.sidebar.markdown("---")

# 3. FILTROS LIBRO BLANCO (AHORA AUTO-SUGERIDOS)
st.sidebar.header("📚 Calidad (Libro Blanco)")
st.sidebar.caption("Auto-sugerido por el sistema según datos reales:")

eps_choice = st.sidebar.selectbox("Crecimiento EPS", 
                                 ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"], 
                                 index=["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"].index(auto_eps))

p_eps_idt = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}[eps_choice]
c_inst = st.sidebar.checkbox("Institucional (Smart Money)", value=auto_inst)
c_sector = st.sidebar.checkbox("Líder Sector (Fuerza Relativa)", value=auto_sector)

plus_calidad_idt = p_eps_idt + (10 if c_inst else 0) + (10 if c_sector else 0)
plus_ev_final = plus_calidad_idt / 7 

st.sidebar.header("🎯 Control de Entrada")
p_gatillo = st.sidebar.number_input("Precio Gatillo $", value=float(precio_mercado))
p_entrada = st.sidebar.number_input("Precio Compra $", value=float(precio_mercado))

st.sidebar.header("🧬 Sistemas Fractalidad")
s_vals = [st.sidebar.number_input(f"Sistema {i+1}", value=v) for i, v in enumerate([1, 3, 8, 14, 21])]

# 4. INTERFAZ PRINCIPAL
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

    # MOTOR DE CÁLCULO
    ev_puro = sum(ev_list) / 5
    ev_total = round(ev_puro + plus_ev_final, 2)
    tier = "👑 TIER S" if ev_total >= 10.0 else "🟢 TIER A" if ev_total >= 5.0 else "🔴 DESCARTE"

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
        st.caption("Tier S ≥ 10 | Tier A ≥ 5")

    with m2:
        st.subheader("🎯 Potencial IDT")
        st.metric("PUNTUACIÓN", f"{idt_total} pts", delta=f"+{plus_calidad_idt} Calidad")

    with m3:
        st.subheader("🛡️ Riesgo ITE")
        p_stop = st.number_input("Precio Stop $", value=float(p_entrada * 0.95))
        ite = round(((p_entrada - p_stop) / p_stop) * 100, 2) if p_stop > 0 else 0
        st.metric("TENSIÓN ITE", f"{ite}%")

    # VERDICTO
    if ev_total < 5: v_txt, v_col = "🚫 NO OPERABLE (Calidad)", "#ff4b4b"
    elif ite > 8: v_txt, v_col = "🚫 NO OPERABLE (Riesgo)", "#ff4b4b"
    elif idt_total >= 100 and ite <= 5: v_txt, v_col = "🔥 COMPRA OBLIGATORIA", "#00ffcc"
    elif idt_total >= 85 and ite <= 8: v_txt, v_col = "🟡 COMPRA TÁCTICA", "#ffcc00"
    else: v_txt, v_col = "🚫 ARMA BLOQUEADA (Puntos)", "#ff4b4b"
    
    st.markdown(f"<h2 style='text-align:center; color:{v_col};'>{v_txt}</h2>", unsafe_allow_html=True)

    if st.button("💾 GUARDAR EN RANKING"):
        nuevo = {"Ticker": ticker_input, "Tier": tier, "EV_Total": ev_total,
                 "IDT_Puntos": idt_total, "ITE_Porc": ite, "Veredicto": v_txt}
        st.session_state.analisis = pd.concat([st.session_state.analisis, pd.DataFrame([nuevo])]).drop_duplicates('Ticker', keep='last')

    st.subheader("📋 Tu Ranking de Guepardos")
    if not st.session_state.analisis.empty:
        st.dataframe(st.session_state.analisis[COLUMNAS].sort_values("EV_Total", ascending=False), use_container_width=True)

    if st.button("🗑️ RESETEAR MEMORIA"):
        st.session_state.analisis = pd.DataFrame(columns=COLUMNAS)
        st.rerun()
