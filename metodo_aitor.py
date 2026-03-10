import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="A.I.T.O.R. 2.6 - Fundamental & Quant", layout="wide")

# --- BASE DE DATOS ---
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=["Ticker", "Tier", "EV_Pond", "EPS_G", "Inst", "IDT", "Verdict"])

st.sidebar.header("⚙️ Configuración del Guepardo")
ticker_input = st.sidebar.text_input("TICKER", "CRDO").upper()

# --- BLOQUE 1: VALIDACIÓN FUNDAMENTAL (LIBRO BLANCO) ---
st.sidebar.markdown("### 📊 Filtros del Libro Blanco")
eps_growth = st.sidebar.checkbox("Crecimiento EPS > 25% (Esperado)", value=True)
inst_pos = st.sidebar.checkbox("Posicionamiento Institucional (Smart Money)", value=True)
fuerte_sector = st.sidebar.checkbox("Líder de Sector / RS Relativa Alta", value=True)

secuencia = [st.sidebar.number_input(f"Día {i+1}", value=v, key=f"d{i}") for i, v in enumerate([1, 3, 8, 13, 21])]

# --- INTERFAZ PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["🔍 Escáner Quant & Fund", "💼 Cartera", "📊 Performance"])

with tab1:
    st.title(f"🚀 Análisis Integral: {ticker_input}")
    
    # ENTRADA DE DATOS QUANT
    ev_list, wr_list, estados = [], [], []
    cols = st.columns(5)
    for i, d in enumerate(secuencia):
        with cols[i]:
            st.markdown(f"### {d}D")
            wr_val = st.number_input(f"WR% {d}D", 0, 100, 50, key=f"w{d}")
            ratio_val = st.number_input(f"Ratio {d}D", 0.0, 100.0, 2.0, key=f"r{d}")
            est_val = st.radio(f"Estado", ["🔴 Venta", "🔵 Compra"], key=f"e{d}")
            ev_calc = ((wr_val/100) * ratio_val) - ((1 - wr_val/100) * 1)
            ev_list.append(ev_calc); wr_list.append(wr_val); estados.append(est_val)
            st.caption(f"EV: {ev_calc:.2f}")

    # --- EL NUEVO MOTOR DE TIER (CROSS-OVER) ---
    ev_ponderado = round(sum(ev_list) / 5, 2)
    
    # Lógica de Tier: Cruce de Quant + Fund
    # Para ser Tier S: Necesita EV > 5 Y cumplir los 3 filtros fundamentales
    if ev_ponderado >= 5.0 and eps_growth and inst_pos and fuerte_sector:
        tier_label = "👑 TIER S"
        bonus_tier = 15
    elif ev_ponderado >= 3.0 and (eps_growth or inst_pos):
        tier_label = "🟢 TIER A"
        bonus_tier = 0
    else:
        tier_label = "🔴 TIER C (Descarte)"
        bonus_tier = -50 # Penalización por falta de fundamentales

    # SUMA IDT
    base_wr = wr_list[0]
    puntos_estructura = sum(1 for e in estados[1:] if "🔵 Compra" in e) * 10
    puntos_señal = 10 if "🔵 Compra" in estados[0] else 0
    idt_total = base_wr + bonus_tier + puntos_estructura + puntos_señal

    # --- VISUALIZACIÓN ---
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("CALIDAD INTEGRAL", tier_label, f"EV Pond: {ev_ponderado}")
        st.write(f"EPS >25%: {'✅' if eps_growth else '❌'}")
        st.write(f"Inst: {'✅' if inst_pos else '❌'}")
    with c2:
        st.metric("PUNTUACIÓN IDT", f"{idt_total} pts")
        st.info(f"Bonus Tier S (+15): {'Activado' if bonus_tier == 15 else 'No'}")
    with c3:
        p_in = st.number_input("Entrada $", value=100.0)
        p_st = st.number_input("Stop $", value=95.0)
        ite = round(((p_in - p_st) / p_st) * 100, 2)
        st.metric("RIESGO ITE", f"{ite}%")

    if st.button("💾 Guardar en Ranking"):
        nuevo = {"Ticker": ticker_input, "Tier": tier_label, "EV_Pond": ev_ponderado, "EPS_G": eps_growth, "Inst": inst_pos, "IDT": idt_total, "Verdict": tier_label}
        st.session_state.analisis = pd.concat([st.session_state.analisis, pd.DataFrame([nuevo])]).drop_duplicates('Ticker', keep='last')
    
    st.dataframe(st.session_state.analisis.sort_values("IDT", ascending=False), use_container_width=True)
