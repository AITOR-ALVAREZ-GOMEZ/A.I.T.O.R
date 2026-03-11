import streamlit as st
import pandas as pd
import yfinance as yf

# 1. CONFIGURACIÓN E INICIALIZACIÓN
st.set_page_config(page_title="A.I.T.O.R. 4.1 - Absolute Quant", layout="wide")

if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=[
        "Ticker", "Tier", "EV Total", "IDT Puntos", "ITE %", "Veredicto"
    ])

# 2. SIDEBAR: EL CEREBRO DEL GESTOR
st.sidebar.header("🔍 Buscador de Activos")
ticker_input = st.sidebar.text_input("TICKER", "CRDO").upper()

# Datos de Mercado rápidos
nombre_empresa = "Cargando..."
precio_mercado = 0.0
try:
    stock = yf.Ticker(ticker_input)
    nombre_empresa = stock.info.get('longName', 'Ticker no detectado')
    precio_mercado = stock.info.get('regularMarketPrice', stock.info.get('previousClose', 0.0))
except:
    pass

st.sidebar.subheader(f"🏢 {nombre_empresa}")
st.sidebar.write(f"**Precio:** {precio_mercado} $")
st.sidebar.markdown("---")

# FILTROS LIBRO BLANCO (SUMAN A LA ESPERANZA)
st.sidebar.header("📚 Calidad (Libro Blanco)")
eps_choice = st.sidebar.selectbox("Crecimiento EPS", 
                                 ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"], index=3)

# Definimos cuánto suma cada cosa a la Esperanza Matemática Final
plus_ev_eps = {"Bajo (<10%)": 0.0, "Medio (>10%)": 0.5, "Alto (>15%)": 1.0, "Explosivo (>25%)": 2.0}[eps_choice]
c_inst = st.sidebar.checkbox("Institucional (Smart Money)", value=True)
c_sector = st.sidebar.checkbox("Líder Sector (RS > 90)", value=True)

# Plus total por Calidad (Máximo +4.0 puntos de EV)
plus_calidad_total = plus_ev_eps + (1.0 if c_inst else 0) + (1.0 if c_sector else 0)

st.sidebar.header("🎯 Control de Entrada")
p_gatillo = st.sidebar.number_input("Precio Señal Gatillo $", value=float(precio_mercado))
p_entrada = st.sidebar.number_input("Precio Compra $", value=float(precio_mercado))

st.sidebar.header("🧬 Sistemas (Fractal)")
# Definimos la secuencia Fibonacci
s_list = [1, 3, 8, 14, 21]
secuencia = [st.sidebar.number_input(f"Sistema {v}D", value=v, key=f"s{v}") for v in s_list]

# 3. CUERPO PRINCIPAL
tab1, tab2, tab3 = st.tabs(["🔍 Escáner de Esperanza", "💼 Cartera", "📊 Performance"])

with tab1:
    st.title(f"🚀 Análisis de {ticker_input}")
    
    # MATRIZ DE DATOS
    ev_list = []
    wr_list = []
    estados = []
    
    cols = st.columns(5)
    for i, s_val in enumerate(secuencia):
        with cols[i]:
            st.markdown(f"### Sist. {s_val}D")
            wr = st.number_input(f"WR% {s_val}D", 0, 100, 50, key=f"wr{s_val}")
            ratio = st.number_input(f"Ratio {s_val}D", 0.0, 100.0, 2.0, key=f"rt{s_val}")
            estado = st.radio(f"Estado", ["🔴 Venta", "🔵 Compra"], key=f"es{s_val}")
            
            # Cálculo de EV Individual
            ev_ind = round(((wr/100) * ratio) - ((1 - wr/100) * 1), 2)
            ev_list.append(ev_ind)
            wr_list.append(wr)
            estados.append(estado)
            st.metric("EV Individual", f"{ev_ind}")

    # --- MOTOR DE CÁLCULO INTEGRAL ---
    ev_matematico = sum(ev_list) / 5
    # LA ESPERANZA FINAL ES LA SUMA DE AMBOS
    esperanza_final = round(ev_matematico + plus_calidad_total, 2)
    
    # Definición de Tier por el Score Final
    if esperanza_final >= 10.0: tier, bonus_idt = "👑 TIER S", 15
    elif esperanza_final >= 5.0: tier, bonus_idt = "🟢 TIER A", 0
    else: tier, bonus_idt = "🔴 DESCARTE", -50

    # Puntos IDT
    dist = ((p_entrada - p_gatillo) / p_gatillo) * 100 if p_gatillo > 0 else 0
    penal = 30 if dist > 5.0 else 10 if dist >= 2.0 else 0
    p_estruc = sum(1 for e in estados[1:] if "🔵" in e) * 10
    p_señal = 10 if "🔵" in estados[0] else 0
    idt_total = wr_list[0] + bonus_idt + p_estruc + p_señal - penal

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.subheader("🧪 Esperanza Final")
        st.metric("A.I.T.O.R. SCORE", f"{esperanza_final}", f"+{plus_calidad_total} Calidad")
        st.caption(f"Estadística Base: {ev_matematico:.2f}")

    with m2:
        st.subheader("🎯 Potencial IDT")
        delta_idt = f"-{penal} Distancia" if penal > 0 else None
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
        nuevo = {"Ticker": ticker_input, "Tier": tier, "EV Total": esperanza_final,
                 "IDT Puntos": idt_total, "ITE %": ite, "Veredicto": v_txt}
        st.session_state.analisis = pd.concat([st.session_state.analisis, pd.DataFrame([nuevo])]).drop_duplicates('Ticker', keep='last')
        st.success("Guardado.")

    st.subheader("📋 Tu Ranking de Élite")
    st.dataframe(st.session_state.analisis.sort_values("EV Total", ascending=False), use_container_width=True)
