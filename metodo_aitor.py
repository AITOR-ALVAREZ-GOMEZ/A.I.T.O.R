import streamlit as st
import pandas as pd
import yfinance as yf

# 1. CONFIGURACIÓN
st.set_page_config(page_title="A.I.T.O.R. 5.0 - Intelligent Legend", layout="wide")

COL_TABLA = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto"]
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=COL_TABLA)

# --- 2. BUSCADOR INTELIGENTE CON AUTO-DETECCIÓN ---
st.sidebar.header("🔍 Buscador de Activos")
ticker_input = st.sidebar.text_input("TICKER (ej. MSFT, CRDO, NVDA)", "MSFT").upper()

# Variables de detección pro-activa
auto_eps = "Bajo (<10%)"
auto_inst = False
auto_sector = False
nombre_emp = "Buscando..."
p_mercado = 0.0

try:
    stock = yf.Ticker(ticker_input)
    inf = stock.info
    nombre_emp = inf.get('longName', 'Ticker no detectado')
    p_mercado = inf.get('regularMarketPrice', inf.get('previousClose', 0.0))
    
    # Sensor de EPS
    growth = inf.get('earningsQuarterlyGrowth', 0) or 0
    if growth > 0.25: auto_eps = "Explosivo (>25%)"
    elif growth > 0.15: auto_eps = "Alto (>15%)"
    elif growth > 0.10: auto_eps = "Medio (>10%)"
    
    # Sensor Institucional
    inst_p = inf.get('heldPercentInstitutions', 0) or 0
    if inst_p > 0.35: auto_inst = True # Umbral ajustado para Manos Fuertes
    
    # Sensor de Liderazgo (Precio > Media 50 sesiones)
    hist_50 = stock.history(period="50d")
    if not hist_50.empty:
        media_50 = hist_50['Close'].mean()
        if p_mercado > media_50: auto_sector = True
except:
    st.sidebar.warning("Esperando Ticker válido...")

st.sidebar.subheader(f"🏢 {nombre_emp}")
st.sidebar.write(f"**Cotización:** {p_mercado} $")
st.sidebar.markdown("---")

# 3. FILTROS LIBRO BLANCO (AHORA SIN ERRORES DE SINTAXIS)
st.sidebar.header("📚 Calidad (Libro Blanco)")
opciones_eps = ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"]
eps_choice = st.sidebar.selectbox("Crecimiento EPS", opciones_eps, index=opciones_eps.index(auto_eps))

p_eps_idt = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}[eps_choice]
c_inst = st.sidebar.checkbox("Institucional (Smart Money)", value=auto_inst)
c_sector = st.sidebar.checkbox("Líder Sector (Fuerza Relativa)", value=auto_sector)

plus_calidad_idt = p_eps_idt + (10 if c_inst else 0) + (10 if c_sector else 0)
plus_ev_final = plus_calidad_idt / 7 

st.sidebar.header("🎯 Control de Ejecución")
p_gatillo = st.sidebar.number_input("Precio Gatillo $", value=float(p_mercado))
p_entrada = st.sidebar.number_input("Precio Compra Deseado $", value=float(p_mercado))

st.sidebar.header("🧬 Sistemas Fractalidad")
s_vals = [st.sidebar.number_input(f"Sistema {i+1}", value=v) for i, v in enumerate([1, 3, 8, 14, 21])]

# 4. CUERPO PRINCIPAL
tab1, tab2, tab3 = st.tabs(["🔍 Escáner Pro", "💼 Cartera", "📊 Performance"])

with tab1:
    st.title(f"🚀 Dashboard de Esperanza: {ticker_input}")
    
    ev_list, wr_list, estados = [], [], []
    cols = st.columns(5)
    for i, s_v in enumerate(s_vals):
        with cols[i]:
            st.markdown(f"### Sist. {s_v}D")
            wr = st.number_input(f"WR% {s_v}D", 0, 100, 50, key=f"wr_{i}")
            ratio = st.number_input(f"Ratio {s_v}D", 0.0, 100.0, 2.0, key=f"rt_{i}")
            est = st.radio(f"Estado", ["🔴 Venta", "🔵 Compra"], key=f"es_{i}")
            ev_i = round(((wr/100) * ratio) - ((1 - wr/100) * 1), 2)
            ev_list.append(ev_i); wr_list.append(wr); estados.append(est)
            st.metric("EV Indiv.", f"{ev_i}")

    # MOTOR DE CÁLCULO
    ev_puro = sum(ev_list) / 5
    ev_total = round(ev_puro + plus_ev_final, 2)
    
    dist = ((p_entrada - p_gatillo) / p_gatillo) * 100 if p_gatillo > 0 else 0
    penal = 30 if dist > 5.0 else 10 if dist >= 2.0 else 0
    p_estruc = sum(1 for e in estados[1:] if "🔵" in e) * 10
    p_senal = 10 if "🔵" in estados[0] else 0
    idt_total = wr_list[0] + plus_calidad_idt + p_estruc + p_senal - penal

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.subheader("🧪 EV TOTAL")
        st.caption("Esperanza Matemática: Ventaja estadística + Calidad del activo.")
        st.metric("VALORACIÓN", f"{ev_total}", f"+{plus_ev_final:.2f} Calidad")
        
        s_m = "👉 " if ev_total >= 10 else ""
        a_m = "👉 " if 5 <= ev_total < 10 else ""
        d_m = "👉 " if ev_total < 5 else ""
        st.markdown(f"{s_m}**Tier S (Élite):** $\ge 10$\n\n{a_m}**Tier A (Operable):** $5 - 10$\n\n{d_m}**Descarte (Riesgo):** $< 5$")

    with m2:
        st.subheader("🎯 IDT PUNTOS")
        st.caption("Índice de Disparo Táctico: Potencia de entrada acumulada.")
        st.metric("PUNTUACIÓN", f"{idt_total} pts")
        
        ob_m = "👉 " if idt_total >= 100 else ""
        ta_m = "👉 " if 85 <= idt_total < 100 else ""
        bl_m = "👉 " if idt_total < 85 else ""
        st.markdown(f"{ob_m}**Compra Obligatoria:** $\ge 100$\n\n{ta_m}**Compra Táctica:** $85 - 99$\n\n{bl_m}**Arma Bloqueada:** $< 85$")

    with m3:
        st.subheader("🛡️ ITE %")
        st.caption("Índice de Tensión Elástica: Distancia al stop loss.")
        p_stop = st.number_input("Precio Stop $", value=float(p_entrada * 0.95))
        ite = round(((p_entrada - p_stop) / p_stop) * 100, 2) if p_stop > 0 else 0
        st.metric("RIESGO", f"{ite}%")
        
        op_m = "👉 " if ite <= 5 else ""
        li_m = "👉 " if 5 < ite <= 8 else ""
        no_m = "👉 " if ite > 8 else ""
        st.markdown(f"{op_m}**Óptimo:** $\le 5\%$\n\n{li_m}**Límite:** $5\% - 8\%$\n\n{no_m}**No Operable:** $> 8\%$")

    # VERDICTO FINAL
    if ev_total < 5: v_txt, v_col = "🚫 NO OPERABLE (Baja Calidad)", "#ff4b4b"
    elif ite > 8: v_txt, v_col = "🚫 NO OPERABLE (Riesgo ITE)", "#ff4b4b"
    elif idt_total >= 100 and ite <= 5: v_txt, v_col = "🔥 COMPRA OBLIGATORIA", "#00ffcc"
    elif idt_total >= 85 and ite <= 8: v_txt, v_col = "🟡 COMPRA TÁCTICA", "#ffcc00"
    else: v_txt, v_col = "🚫 ARMA BLOQUEADA (Puntos)", "#ff4b4b"
    
    st.markdown(f"<h2 style='text-align:center; color:{v_col};'>{v_txt}</h2>", unsafe_allow_html=True)

    if st.button("💾 GUARDAR EN RANKING"):
        t_label = "👑 TIER S" if ev_total >= 10 else "🟢 TIER A" if ev_total >= 5 else "🔴 DESCARTE"
        nuevo = {"Ticker": ticker_input, "Tier": t_label, "EV_Total": ev_total,
                 "IDT_Puntos": idt_total, "ITE_Porc": ite, "Veredicto": v_txt}
        st.session_state.analisis = pd.concat([st.session_state.analisis, pd.DataFrame([nuevo])]).drop_duplicates('Ticker', keep='last')

    st.subheader("📋 Tu Ranking de Guepardos")
    if not st.session_state.analisis.empty:
        st.dataframe(st.session_state.analisis[COL_TABLA].sort_values("EV_Total", ascending=False), use_container_width=True)

    if st.button("🗑️ RESETEAR MEMORIA"):
        st.session_state.analisis = pd.DataFrame(columns=COL_TABLA)
        st.rerun()
