import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="A.I.T.O.R. 2.5 - Forzado de Tier", layout="wide")

# --- BASE DE DATOS ---
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=["Ticker", "Tier", "EV_Pond", "IDT", "ITE", "Verdict"])

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración")
ticker_input = st.sidebar.text_input("TICKER", "TMDX").upper()
precio_actual = 0.0
try:
    stock = yf.Ticker(ticker_input)
    precio_actual = stock.info.get('regularMarketPrice', stock.info.get('previousClose', 0.0))
except:
    pass

st.sidebar.markdown(f"**Precio Actual:** {precio_actual} $")
secuencia = [st.sidebar.number_input(f"Día {i+1}", value=v, key=f"d{i}") for i, v in enumerate([1, 3, 8, 13, 21])]

# --- INTERFAZ ---
tab1, tab2, tab3 = st.tabs(["🔍 Escáner Quant", "💼 Cartera", "📊 Performance"])

with tab1:
    st.title(f"🚀 Análisis de {ticker_input}")
    
    # 1. ENTRADA DE DATOS
    ev_list, wr_list, estados = [], [], []
    cols = st.columns(5)
    
    for i, d in enumerate(secuencia):
        with cols[i]:
            st.markdown(f"### {d}D")
            wr_val = st.number_input(f"WR% {d}D", 0, 100, 50, key=f"w{d}")
            ratio_val = st.number_input(f"Ratio {d}D", 0.0, 100.0, 2.0, key=f"r{d}")
            est_val = st.radio(f"Estado", ["🔴 Venta", "🔵 Compra"], key=f"e{d}")
            
            # Cálculo matemático inmediato
            wr_decimal = wr_val / 100
            # Esperanza: (Acierto * Gana) - (Fallo * Pierde)
            ev_calc = (wr_decimal * ratio_val) - ((1 - wr_decimal) * 1)
            
            ev_list.append(ev_calc)
            wr_list.append(wr_val)
            estados.append(est_val)
            st.code(f"EV: {ev_calc:.2f}")

    # --- 2. EL MOTOR DE CÁLCULO (FORZADO) ---
    # Calculamos la media y redondeamos para evitar errores de coma flotante
    ev_ponderado = round(sum(ev_list) / 5, 2)
    
    # Determinamos el TIER con límites claros
    if ev_ponderado >= 10.0:
        tier_label = "👑 TIER S"
        bonus_tier = 15
    elif ev_ponderado >= 5.0:
        tier_label = "🟢 TIER A"
        bonus_tier = 0
    else:
        tier_label = "🔴 DESCARTE"
        bonus_tier = 0

    # 3. SUMA DEL IDT (Puntuación Final)
    base_wr = wr_list[0]  # Porcentaje de acierto del Gatillo
    # Estructura: Sistemas 2, 3, 4 y 5 (10 pts c/u si están en azul)
    puntos_estructura = sum(1 for e in estados[1:] if "🔵 Compra" in e) * 10
    # Señal: Sistema 1 (10 pts si está en azul)
    puntos_señal = 10 if "🔵 Compra" in estados[0] else 0
    
    # LA SUMA TOTAL
    idt_total = base_wr + bonus_tier + puntos_estructura + puntos_señal

    # --- 4. VISUALIZACIÓN DE RESULTADOS ---
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric("CALIDAD (EV POND)", f"{ev_ponderado}", tier_label)
        # Barra de progreso visual hacia el Tier S
        progreso = min(ev_ponderado / 10, 1.0) if ev_ponderado > 0 else 0.0
        st.progress(progreso)
        st.caption("Objetivo Tier S: EV >= 10")

    with c2:
        st.metric("PUNTUACIÓN IDT", f"{idt_total} pts")
        st.info(f"Bonus Tier S incluido: +{bonus_tier} pts")

    with c3:
        p_in = st.number_input("Precio Entrada $", value=float(precio_actual))
        p_st = st.number_input("Precio Stop $", value=float(precio_actual*0.95))
        ite = round(((p_in - p_st) / p_st) * 100, 2) if p_st > 0 else 0
        st.metric("RIESGO ITE", f"{ite}%")

    # --- AUDITORÍA TÉCNICA (Desglose real) ---
    with st.expander("🔍 Auditoría Técnica de la Operación"):
        st.write(f"**Análisis de Puntuación:**")
        st.write(f"- WinRate Base (1D): `{base_wr} pts`")
        st.write(f"- Bonus Calidad ({tier_label}): `+{bonus_tier} pts`")
        st.write(f"- Puntos Estructura (3D-21D): `+{puntos_estructura} pts`")
        st.write(f"- Puntos Señal Gatillo (1D): `+{puntos_señal} pts`")
        st.write(f"**TOTAL IDT:** `{idt_total} PUNTOS`")

    # VERDICTO FINAL
    if idt_total >= 100 and ite <= 5: 
        v_final, v_col = "🔥 COMPRA OBLIGATORIA", "#00ffcc"
    elif idt_total >= 85 and ite <= 8: 
        v_final, v_col = "🟡 COMPRA TÁCTICA", "#ffcc00"
    else: 
        v_final, v_col = "🚫 ARMA BLOQUEADA", "#ff4b4b"

    st.markdown(f"<h2 style='text-align:center; color:{v_col};'>{v_final}</h2>", unsafe_allow_html=True)

    if st.button("💾 Guardar en Ranking"):
        nuevo = {"Ticker": ticker_input, "Tier": tier_label, "EV_Pond": ev_ponderado, "IDT": idt_total, "ITE": ite, "Verdict": v_final}
        st.session_state.analisis = pd.concat([st.session_state.analisis, pd.DataFrame([nuevo])]).drop_duplicates('Ticker', keep='last')
    
    st.dataframe(st.session_state.analisis.sort_values("IDT", ascending=False), use_container_width=True)
