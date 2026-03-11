import streamlit as st
import pandas as pd

st.set_page_config(page_title="A.I.T.O.R. 3.1 - Quant Core", layout="wide")

# --- BASE DE DATOS ---
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=[
        "Ticker", "Tier", "EV Total", "IDT Puntos", "WR Gatillo", "ITE %", "Veredicto"
    ])

# --- SIDEBAR: CONFIGURACIÓN ---
st.sidebar.header("🏢 Filtros de Calidad")
eps_level = st.sidebar.selectbox("Nivel de EPS", 
                                 ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"], index=3)

puntos_eps = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}[eps_level]
c_inst = st.sidebar.checkbox("Instituciones Comprando", value=True)
c_sector = st.sidebar.checkbox("Líder de Sector (RS > 90)", value=True)
puntos_fund = puntos_eps + (10 if c_inst else 0) + (10 if c_sector else 0)

st.sidebar.header("🎯 Control de Ejecución")
p_disparo = st.sidebar.number_input("Precio Disparo (Gatillo) $", value=100.0)
p_actual = st.sidebar.number_input("Precio Actual $", value=102.0)

# Espacios Temporales (FRACTALIDAD)
st.sidebar.header("🧬 Sistemas (Fibonacci)")
# CAMBIO DE ETIQUETA: "Sistema" en lugar de "Día"
secuencia = [st.sidebar.number_input(f"Sistema {i+1}", value=v, key=f"s{i}") for i, v in enumerate([1, 3, 8, 14, 21])]

ticker_input = st.sidebar.text_input("TICKER", "CRDO").upper()

# --- INTERFAZ PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["🔍 Análisis Cuantitativo", "💼 Cartera", "📊 Performance"])

with tab1:
    st.title(f"🚀 Escáner de Esperanza Matemática: {ticker_input}")
    
    # 1. ENTRADA DE DATOS Y CÁLCULO DE EV INDIVIDUAL
    ev_list, wr_list, estados = [], [], []
    cols = st.columns(5)
    
    for i, s in enumerate(secuencia):
        with cols[i]:
            st.markdown(f"### Sist. {s}D")
            wr = st.number_input(f"WR% {s}D", 0, 100, 50, key=f"w{i}")
            ratio = st.number_input(f"Ratio {s}D", 0.0, 100.0, 2.0, key=f"r{i}")
            estado = st.radio(f"Estado {s}D", ["🔴 Venta", "🔵 Compra"], key=f"e{i}")
            
            # Cálculo EV Individual: $EV = (WR * Ratio) - ((1-WR) * 1)$
            wr_f = wr / 100
            ev_ind = round((wr_f * ratio) - ((1 - wr_f) * 1), 2)
            
            ev_list.append(ev_ind)
            wr_list.append(wr)
            estados.append(estado)
            
            # MOSTRAR EV INDIVIDUAL DE FORMA PREFERENTE
            st.metric(f"EV Sist. {s}D", f"{ev_ind}")

    # --- 2. CÁLCULO DE ESPERANZA TOTAL Y TIER ---
    ev_total = round(sum(ev_list) / 5, 2)
    es_tier_s = puntos_fund >= 30 and ev_total >= 4.0
    tier_label = "👑 TIER S" if es_tier_s else "🟢 TIER A" if ev_total >= 3.0 else "🔴 DESCARTE"

    # --- 3. CÁLCULO IDT CON PENALIZACIÓN ---
    distancia = ((p_actual - p_disparo) / p_disparo) * 100
    penalizacion = 30 if distancia > 5.0 else 10 if distancia >= 2.0 else 0
    
    base_wr = wr_list[0]
    p_estructura = sum(1 for e in estados[1:] if "🔵 Compra" in e) * 10
    p_señal = 10 if "🔵 Compra" in estados[0] else 0
    idt_total = base_wr + (20 if es_tier_s else 0) + p_estructura + p_señal - penalizacion

    # --- 4. PANEL PREFERENTE (ESPERANZA MATEMÁTICA TOTAL) ---
    st.markdown("---")
    main_col1, main_col2, main_col3 = st.columns(3)
    
    with main_col1:
        st.subheader("📊 Esperanza Matemática")
        st.metric("EV TOTAL DEL VALOR", f"{ev_total}", delta=tier_label)
        st.caption("Media de los 5 sistemas Fibonacci")

    with main_col2:
        st.subheader("🎯 Potencial de Disparo")
        st.metric("IDT PUNTOS", f"{idt_total} pts", f"-{penalizacion} por distancia" if penalizacion > 0 else None)
        
    with main_col3:
        st.subheader("🛡️ Gestión de Riesgo")
        p_stop = st.number_input("Precio Stop Loss $", value=float(p_actual * 0.95))
        ite = round(((p_actual - p_stop) / p_stop) * 100, 2)
        st.metric("RIESGO ITE", f"{ite}%")

    # --- 5. VERDICTO Y GUARDADO ---
    if idt_total >= 100 and ite <= 5: verdict, col = "🔥 COMPRA OBLIGATORIA", "#00ffcc"
    elif idt_total >= 85 and ite <= 8: verdict, col = "🟡 COMPRA TÁCTICA", "#ffcc00"
    else: verdict, col = "🚫 ARMA BLOQUEADA", "#ff4b4b"

    st.markdown(f"<h2 style='text-align:center; color:{col};'>{verdict}</h2>", unsafe_allow_html=True)

    if st.button("💾 GUARDAR EN RANKING CUANTITATIVO"):
        nuevo = {
            "Ticker": ticker_input, "Tier": tier_label, "EV Total": ev_total,
            "IDT Puntos": idt_total, "WR Gatillo": f"{base_wr}%", "ITE %": ite,
            "Veredicto": verdict
        }
        st.session_state.analisis = pd.concat([st.session_state.analisis, pd.DataFrame([nuevo])]).drop_duplicates('Ticker', keep='last')
        st.success(f"{ticker_input} guardado correctamente.")

    # --- 6. RANKING ORDENADO POR EV /
