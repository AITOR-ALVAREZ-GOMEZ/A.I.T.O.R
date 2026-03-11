import streamlit as st
import pandas as pd
import yfinance as yf

# 1. CONFIGURACIÓN
st.set_page_config(page_title="A.I.T.O.R. 4.3 - Full Fusion", layout="wide")

# Inicializamos la tabla con nombres de columna definitivos para evitar el KeyError
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=[
        "Ticker", "Tier", "AITOR_Score", "IDT_Puntos", "ITE_Porcentaje", "Veredicto"
    ])

# 2. SIDEBAR (CONTROLES)
st.sidebar.header("🔍 Buscador")
ticker_input = st.sidebar.text_input("TICKER", "CRDO").upper()

# Datos de Yahoo Finance
nombre_empresa, precio_mercado = "Buscando...", 0.0
try:
    stock = yf.Ticker(ticker_input)
    info = stock.info
    nombre_empresa = info.get('longName', 'Ticker no detectado')
    precio_mercado = info.get('regularMarketPrice', info.get('previousClose', 0.0))
except: pass

st.sidebar.subheader(f"🏢 {nombre_empresa}")
st.sidebar.markdown("---")

# --- PILAR 1: CALIDAD (AHORA SUMA A TODO) ---
st.sidebar.header("📚 Calidad (Libro Blanco)")
eps_choice = st.sidebar.selectbox("Crecimiento EPS", 
                                 ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"], index=3)

# Puntos para el IDT (Potencial de disparo)
p_eps_idt = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}[eps_choice]
c_inst = st.sidebar.checkbox("Institucional (Smart Money)", value=True)
c_sector = st.sidebar.checkbox("Líder Sector (RS > 90)", value=True)

# Suma de calidad para el IDT (Máximo +35 pts)
plus_calidad_idt = p_eps_idt + (10 if c_inst else 0) + (10 if c_sector else 0)

# Plus para la Esperanza (AITOR SCORE)
plus_ev = plus_calidad_idt / 7 # Escala para no desvirtuar la estadística

st.sidebar.header("🎯 Control de Entrada")
p_gatillo = st.sidebar.number_input("Precio Gatillo $", value=float(precio_mercado))
p_entrada = st.sidebar.number_input("Precio Compra $", value=float(precio_mercado))

st.sidebar.header("🧬 Sistemas (Fibonacci)")
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
            st.metric("EV Individual", f"{ev_ind}")

    # --- MOTOR DE CÁLCULO ---
    ev_puro = sum(ev_list) / 5
    aitor_score = round(ev_puro + plus_ev, 2)
    
    # Tier Label
    tier = "👑 TIER S" if aitor_score >= 10.0 else "🟢 TIER A" if aitor_score >= 5.0 else "🔴 DESCARTE"

    # IDT PUNTOS (FÓRMULA CORREGIDA)
    dist = ((p_entrada - p_gatillo) / p_gatillo) * 100 if p_gatillo > 0 else 0
    penal = 30 if dist > 5.0 else 10 if dist >= 2.0 else 0
    p_estruc = sum(1 for e in estados[1:] if "🔵" in e) * 10
    p_senal = 10 if "🔵" in estados[0] else 0
    
    # LA SUMA DEFINITIVA: Base + Calidad + Estructura + Señal - Penalización
    idt_total = wr_list[0] + plus_calidad_idt + p_estruc + p_senal - penal

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.subheader("🧪 Esperanza Final")
        st.metric("A.I.T.O.R. SCORE", f"{aitor_score}", f"+{plus_ev:.2f} Calidad")
    with m2:
        st.subheader("🎯 Potencial IDT")
        delta_idt = f"+{plus_calidad_idt} por Calidad" if plus_calidad_idt > 0 else None
        st.metric("PUNTUACIÓN", f"{idt_total} pts", delta=delta_idt)
    with m3:
        st.subheader("🛡️ Riesgo ITE")
        p_stop = st.number_input("Precio Stop $", value=float(p_entrada * 0.95))
        ite = round(((p_entrada - p_stop) / p_stop) * 100, 2) if p_stop > 0 else 0
        st.metric("TENSIÓN GOMA", f"{ite}%")

    # VERDICTO
    if idt_total >= 100 and ite <= 5: v_txt, v_col = "🔥 COMPRA OBLIGATORIA", "#00ffcc"
    elif idt_total >= 85 and ite <= 8: v_txt, v_col = "🟡 COMPRA TÁCTICA", "#ffcc00"
    else: v_txt, v_col = "🚫 ARMA BLOQUEADA", "#ff4b4b"
    st.markdown(f"<h2 style='text-align:center; color:{v_col};'>{v_txt}</h2>", unsafe_allow_html=True)

    if st.button("💾 GUARDAR EN RANKING"):
        nuevo = {"Ticker": ticker_input, "Tier": tier, "AITOR_Score": aitor_score,
                 "IDT_Puntos": idt_total, "ITE_Porcentaje": ite, "Veredicto": v_txt}
        st.session_state.analisis = pd.concat([st.session_state.analisis, pd.DataFrame([nuevo])]).drop_duplicates('Ticker', keep='last')
        st.success("Guepardo guardado.")

    st.subheader("📋 Tu Ranking de Élite (Ordenado por Esperanza)")
    if not st.session_state.analisis.empty:
        # Ordenamos por AITOR_Score para ver la calidad arriba
        df_rank = st.session_state.analisis.sort_values("AITOR_Score", ascending=False)
        st.dataframe(df_rank, use_container_width=True)
