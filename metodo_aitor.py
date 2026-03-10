import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="A.I.T.O.R. 2.4 - Engine Pro", layout="wide")

# --- BASE DE DATOS ---
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=["Ticker", "Tier", "EV_Pond", "IDT", "ITE", "Verdict"])

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración")
ticker_input = st.sidebar.text_input("TICKER", "CRDO").upper()
precio_actual = 0.0
try:
    stock = yf.Ticker(ticker_input)
    precio_actual = stock.info.get('regularMarketPrice', stock.info.get('previousClose', 0.0))
except:
    pass

st.sidebar.markdown(f"**Precio:** {precio_actual} $")
secuencia = [st.sidebar.number_input(f"Día {i+1}", value=v) for i, v in enumerate([1, 3, 8, 13, 21])]

# --- INTERFAZ ---
tab1, tab2, tab3 = st.tabs(["🔍 Escáner Quant", "💼 Cartera", "📊 Performance"])

with tab1:
    st.title(f"🚀 Análisis de {ticker_input}")
    
    # MATRIZ DE ENTRADA
    ev_list, wr_list, estados = [], [], []
    cols = st.columns(5)
    
    for i, d in enumerate(secuencia):
        with cols[i]:
            st.markdown(f"### {d}D")
            wr = st.number_input(f"WR% {d}D", 0, 100, 50, key=f"w{d}")
            ratio = st.number_input(f"Ratio {d}D", 0.0, 50.0, 2.0, key=f"r{d}")
            estado = st.radio(f"Estado", ["🔴 Venta", "🔵 Compra"], key=f"e{d}")
            
            # Cálculo de Esperanza Matemática Individual
            # $EV = (WR \cdot Ratio) - ((1-WR) \cdot 1)$
            wr_f = wr / 100
            ev_ind = (wr_f * ratio) - ((1 - wr_f) * 1)
            
            ev_list.append(ev_ind)
            wr_list.append(wr)
            estados.append(estado)
            st.caption(f"EV: {ev_ind:.2f}")

    # --- MOTOR DE CÁLCULO DE CALIDAD (TIER) ---
    ev_pond = sum(ev_list) / 5
    es_tier_s = ev_pond >= 10
    tier_label = "👑 TIER S" if es_tier_s else "🟢 TIER A" if ev_pond >= 5 else "🔴 DESCARTE"

    # --- MOTOR DE PUNTUACIÓN IDT (SÍ O NO) ---
    puntos_wr = wr_list[0] 
    puntos_tier = 15 if es_tier_s else 0
    
    # Estructura: Solo cuenta los sistemas 2, 3, 4 y 5
    n_estructura = sum(1 for e in estados[1:] if "🔵 Compra" in e)
    puntos_estructura = n_estructura * 10
    
    # Señal: Solo cuenta el gatillo (Sistema 1)
    puntos_gatillo = 10 if "🔵 Compra" in estados[0] else 0
    
    idt_total = puntos_wr + puntos_tier + puntos_estructura + puntos_gatillo

    # --- PANELES DE CONTROL ---
    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    res1.metric("CALIDAD DEL ACTIVO", tier_label, f"EV Ponderado: {ev_pond:.2f}")
    res2.metric("PUNTUACIÓN IDT", f"{idt_total:.1f} pts")
    
    # Riesgo ITE
    p_in = st.number_input("Precio Entrada $", value=float(precio_actual))
    p_st = st.number_input("Precio Stop (Muro) $", value=float(precio_actual*0.95))
    ite = ((p_in - p_st) / p_st) * 100 if p_st > 0 else 0
    res3.metric("RIESGO ITE", f"{ite:.2f}%")

    with st.expander("📝 Auditoría de la Suma IDT"):
        st.write(f"1. Base Acierto Gatillo: **{puntos_wr}**")
        st.write(f"2. Bonus por Calidad ({tier_label}): **{puntos_tier}**")
        st.write(f"3. Bonus Estructura ({n_estructura} sistemas): **{puntos_estructura}**")
        st.write(f"4. Bonus Señal Gatillo Activa: **{puntos_gatillo}**")
        st.write(f"🏆 **TOTAL: {idt_total} PUNTOS**")

    # VERDICTO
    if idt_total >= 100 and ite <= 5: v, col = "🔥 COMPRA OBLIGATORIA", "#00ffcc"
    elif idt_total >= 85 and ite <= 8: v, col = "🟡 COMPRA TÁCTICA", "#ffcc00"
    else: v, col = "🚫 ARMA BLOQUEADA", "#ff4b4b"

    st.markdown(f"<h2 style='text-align:center; color:{col};'>{v}</h2>", unsafe_allow_html=True)

    if st.button("💾 Guardar en Ranking"):
        nuevo = {"Ticker": ticker_input, "Tier": tier_label, "EV_Pond": round(ev_pond, 2), "IDT": idt_total, "ITE": round(ite, 2), "Verdict": v}
        st.session_state.analisis = pd.concat([st.session_state.analisis, pd.DataFrame([nuevo])]).drop_duplicates('Ticker', keep='last')
    
    st.dataframe(st.session_state.analisis.sort_values("IDT", ascending=False), use_container_width=True)
