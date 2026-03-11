import streamlit as st
import pandas as pd

st.set_page_config(page_title="A.I.T.O.R. 3.0 - Profesional", layout="wide")

# --- BASE DE DATOS ---
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=[
        "Ticker", "Tier", "EV Pond.", "IDT Puntos", "ITE %", "EPS", "Distancia Gatillo", "Veredicto"
    ])

# --- SIDEBAR: REFINAMIENTO FUNDAMENTAL ---
st.sidebar.header("🏢 Filtros de Calidad")
eps_level = st.sidebar.selectbox("Nivel de EPS (Crecimiento)", 
                                 ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"], index=3)

# Asignación de puntos por EPS
puntos_eps = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}[eps_level]

c_inst = st.sidebar.checkbox("Instituciones Comprando", value=True)
c_sector = st.sidebar.checkbox("Líder de Sector (RS > 90)", value=True)
puntos_fund = puntos_eps + (10 if c_inst else 0) + (10 if c_sector else 0)

# --- SIDEBAR: PRECIOS Y PENALIZACIÓN ---
st.sidebar.header("🎯 Control de Ejecución")
p_disparo = st.sidebar.number_input("Precio de Disparo (Gatillo) $", value=100.0)
p_actual = st.sidebar.number_input("Precio Actual $", value=102.0)

# Cálculo de Distancia y Penalización
distancia = ((p_actual - p_disparo) / p_disparo) * 100
if distancia < 2.0: penalizacion = 0
elif 2.0 <= distancia <= 5.0: penalizacion = 10
else: penalizacion = 30 # Penalización crítica por "persecución"

ticker_input = st.sidebar.text_input("TICKER", "CRDO").upper()
secuencia = [st.sidebar.number_input(f"Día {i+1}", value=v, key=f"d{i}") for i, v in enumerate([1, 3, 8, 14, 21])]

# --- INTERFAZ ---
tab1, tab2, tab3 = st.tabs(["🔍 Escáner Pro", "💼 Cartera", "📊 Performance"])

with tab1:
    st.title(f"🚀 Análisis de {ticker_input}")
    
    # 1. ENTRADA DE DATOS QUANT
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

    # --- 2. MOTOR DE VALORACIÓN INTEGRAL ---
    ev_pond = round(sum(ev_list) / 5, 2)
    
    # Tier S dinámico (Para el modo parabólico)
    es_tier_s = puntos_fund >= 30 and ev_pond >= 4.0
    tier_label = "👑 TIER S" if es_tier_s else "🟢 TIER A" if ev_pond >= 3.0 else "🔴 DESCARTE"

    # --- 3. CÁLCULO IDT ACTUALIZADO ---
    base_wr = wr_list[0]
    p_estructura = sum(1 for e in estados[1:] if "🔵 Compra" in e) * 10
    p_señal = 10 if "🔵 Compra" in estados[0] else 0
    
    # Suma Total con Penalización
    idt_total = base_wr + (20 if es_tier_s else 0) + p_estructura + p_señal - penalizacion

    # --- 4. RIESGO ITE ---
    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    p_stop = res3.number_input("Precio Stop (Muro) $", value=float(p_actual * 0.95))
    ite = round(((p_actual - p_stop) / p_stop) * 100, 2)

    with res1:
        st.metric("CALIDAD", tier_label, f"EPS: {eps_level}")
        st.write(f"Distancia al Gatillo: **{distancia:.2f}%**")
        if penalizacion > 0:
            st.warning(f"⚠️ Penalización: -{penalizacion} pts")

    with res2:
        st.metric("PUNTUACIÓN IDT", f"{idt_total} pts")
        if idt_total >= 100 and ite <= 5: v_final, v_col = "🔥 COMPRA OBLIGATORIA", "#00ffcc"
        elif idt_total >= 85 and ite <= 8: v_final, v_col = "🟡 COMPRA TÁCTICA", "#ffcc00"
        else: v_final, v_col = "🚫 ARMA BLOQUEADA", "#ff4b4b"
        st.markdown(f"<h3 style='color:{v_col};'>{v_final}</h3>", unsafe_allow_html=True)

    # --- 5. RANKING ---
    if st.button("💾 GUARDAR EN EL RANKING"):
        nuevo = {
            "Ticker": ticker_input, "Tier": tier_label, "EV Pond.": ev_pond,
            "IDT Puntos": idt_total, "ITE %": ite, "EPS": eps_level,
            "Distancia Gatillo": f"{distancia:.1f}%", "Veredicto": v_final
        }
        st.session_state.analisis = pd.concat([st.session_state.analisis, pd.DataFrame([nuevo])]).drop_duplicates('Ticker', keep='last')

    st.subheader("📋 Tu Selección de Guepardos")
    st.dataframe(st.session_state.analisis.sort_values("IDT Puntos", ascending=False), use_container_width=True)
