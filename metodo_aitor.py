import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="A.I.T.O.R. 2.8 - Valoración Dinámica", layout="wide")

# --- BASE DE DATOS ---
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=["Ticker", "Tier", "EV_Pond", "IDT", "ITE", "Verdict"])

# --- SIDEBAR: FUNDAMENTALES (LOS QUE CAMBIAN LA VALORACIÓN) ---
st.sidebar.header("🏢 Filtros de Calidad (Libro Blanco)")
c_eps = st.sidebar.checkbox("Crecimiento EPS > 25%", value=True)
c_inst = st.sidebar.checkbox("Instituciones Comprando", value=True)
c_sector = st.sidebar.checkbox("Líder de Sector", value=True)

# Cálculo de Puntos Fundamentales (0 a 3)
puntos_fund = sum([c_eps, c_inst, c_sector])

ticker_input = st.sidebar.text_input("TICKER", "CRDO").upper()
secuencia = [st.sidebar.number_input(f"Día {i+1}", value=v, key=f"d{i}") for i, v in enumerate([1, 3, 8, 14, 21])]

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["🔍 Escáner Quant & Fund", "💼 Cartera", "📊 Performance"])

with tab1:
    st.title(f"🚀 Análisis de {ticker_input}")
    
    # ENTRADA DE DATOS QUANT
    ev_list, wr_list, estados = [], [], []
    cols = st.columns(5)
    for i, d in enumerate(secuencia):
        with cols[i]:
            st.markdown(f"### {d}D")
            wr = st.number_input(f"WR% {d}D", 0, 100, 50, key=f"w{d}")
            ratio = st.number_input(f"Ratio {d}D", 0.0, 50.0, 2.0, key=f"r{d}")
            estado = st.radio(f"Estado", ["🔴 Venta", "🔵 Compra"], key=f"e{d}")
            ev_ind = ((wr/100) * ratio) - ((1 - wr/100) * 1)
            ev_list.append(ev_ind); wr_list.append(wr); estados.append(estado)

    # --- 🧠 EL NUEVO CEREBRO DE VALORACIÓN (ESTO ES LO QUE BUSCABAS) ---
    ev_pond = round(sum(ev_list) / 5, 2)
    
    # La Valoración cambia según los puntos fundamentales
    if puntos_fund == 3 and ev_pond >= 4.0:
        tier_label = "👑 TIER S (Supremo)"
        bonus_tier = 15
    elif puntos_fund >= 2 and ev_pond >= 3.0:
        tier_label = "🟢 TIER A (Guepardo)"
        bonus_tier = 0
    else:
        tier_label = "🔴 TIER C (Descarte)"
        bonus_tier = -50 # Penalización crítica por falta de calidad

    # CÁLCULO IDT TOTAL
    base_wr = wr_list[0]
    puntos_estructura = sum(1 for e in estados[1:] if "🔵 Compra" in e) * 10
    puntos_señal = 10 if "🔵 Compra" in estados[0] else 0
    
    # AQUÍ SE SUMA TODO
    idt_total = base_wr + bonus_tier + puntos_estructura + puntos_señal

    # --- RESULTADOS EN PANTALLA ---
    st.markdown("---")
    r1, r2, r3 = st.columns(3)
    
    with r1:
        st.metric("TIER / VALORACIÓN", tier_label)
        st.write(f"Puntos Fundamentales: **{puntos_fund}/3**")
        st.write(f"EV Ponderado: **{ev_pond}**")

    with r2:
        # Aquí el usuario verá el cambio real al activar los checks
        st.metric("PUNTUACIÓN IDT", f"{idt_total} pts")
        if bonus_tier == 15:
            st.success("✅ Bonus Tier S aplicado: +15 pts")
        elif bonus_tier == -50:
            st.error("❌ Penalización Tier C: -50 pts")

    with r3:
        p_in = st.number_input("Precio Entrada $", value=100.0)
        p_st = st.number_input("Precio Stop $", value=95.0)
        ite = round(((p_in - p_st) / p_st) * 100, 2)
        st.metric("RIESGO ITE", f"{ite}%")

    # VERDICTO
    if idt_total >= 100 and ite <= 5: v, col = "🔥 DISPARO OBLIGATORIO", "#00ffcc"
    elif idt_total >= 85 and ite <= 8: v, col = "🟡 DISPARO TÁCTICO", "#ffcc00"
    else: v, col = "🚫 ARMA BLOQUEADA", "#ff4b4b"

    st.markdown(f"<h2 style='text-align:center; color:{col};'>{v}</h2>", unsafe_allow_html=True)

    if st.button("💾 Guardar en Ranking"):
        nuevo = {"Ticker": ticker_input, "Tier": tier_label, "EV_Pond": ev_pond, "IDT": idt_total, "ITE": ite, "Verdict": v}
        st.session_state.analisis = pd.concat([st.session_state.analisis, pd.DataFrame([nuevo])]).drop_duplicates('Ticker', keep='last')
