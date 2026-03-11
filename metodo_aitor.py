import streamlit as st
import pandas as pd
import yfinance as yf # Importante: Asegúrate de tenerlo en requirements.txt

st.set_page_config(page_title="A.I.T.O.R. 3.2 - Search & Quant", layout="wide")

# --- INICIALIZAR BASE DE DATOS ---
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=[
        "Ticker", "Tier", "EV Total", "IDT Puntos", "WR Gatillo", "ITE %", "Veredicto"
    ])

# --- SIDEBAR: BUSCADOR (AHORA ARRIBA DEL TODO) ---
st.sidebar.header("🔍 Buscador de Activos")
ticker_input = st.sidebar.text_input("INTRODUCE TICKER", "CRDO").upper()

# --- MOTOR DE BÚSQUEDA REAL ---
nombre_empresa = "Esperando Ticker..."
precio_actual = 0.0
try:
    stock = yf.Ticker(ticker_input)
    info = stock.info
    nombre_empresa = info.get('longName', 'Ticker no encontrado')
    precio_actual = info.get('regularMarketPrice', info.get('previousClose', 0.0))
except:
    st.sidebar.error("Error de conexión con Wall Street")

st.sidebar.subheader(f"🏢 {nombre_empresa}")
st.sidebar.write(f"**Precio de Mercado:** {precio_actual} $")

st.sidebar.markdown("---")

# --- FILTROS DE CALIDAD ---
st.sidebar.header("🏢 Filtros de Calidad")
eps_level = st.sidebar.selectbox("Nivel de EPS", 
                                 ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"], index=3)
puntos_eps = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}[eps_level]
c_inst = st.sidebar.checkbox("Instituciones Comprando", value=True)
c_sector = st.sidebar.checkbox("Líder de Sector (RS > 90)", value=True)
puntos_fund = puntos_eps + (10 if c_inst else 0) + (10 if c_sector else 0)

st.sidebar.header("🎯 Control de Ejecución")
p_disparo = st.sidebar.number_input("Precio Disparo (Gatillo) $", value=float(precio_actual))
# p_actual lo cogemos del buscador para mayor precisión
p_actual_input = st.sidebar.number_input("Precio Entrada Deseado $", value=float(precio_actual))

st.sidebar.header("🧬 Sistemas (Fibonacci)")
secuencia = [st.sidebar.number_input(f"Sistema {i+1}", value=v, key=f"s{i}") for i, v in enumerate([1, 3, 8, 14, 21])]

# --- INTERFAZ PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["🔍 Análisis Cuantitativo", "💼 Cartera", "📊 Performance"])

with tab1:
    st.title(f"🚀 Dashboard Cuantitativo: {nombre_empresa} ({ticker_input})")
    
    # 1. MATRIZ DE ESPERANZA MATEMÁTICA
    ev_list, wr_list, estados = [], [], []
    cols = st.columns(5)
    
    for i, s in enumerate(secuencia):
        with cols[i]:
            st.markdown(f"### Sist. {s}D")
            wr = st.number_input(f"WR% {s}D", 0, 100, 50, key=f"w{i}")
            ratio = st.number_input(f"Ratio {s}D", 0.0, 100.0, 2.0, key=f"r{i}")
            estado = st.radio(f"Estado {s}D", ["🔴 Venta", "🔵 Compra"], key=f"e{i}")
            
            # $EV = (WR \cdot Ratio) - ((1-WR) \cdot 1)$
            wr_f = wr / 100
            ev_ind = round((wr_f * ratio) - ((1 - wr_f) * 1), 2)
            
            ev_list.append(ev_ind)
            wr_list.append(wr)
            estados.append(estado)
            st.metric(f"EV Sist. {s}D", f"{ev_ind}")

    # --- 2. CÁLCULOS CENTRALES (PREFERENTES) ---
    ev_total = round(sum(ev_list) / 5, 2)
    es_tier_s = puntos_fund >= 30 and ev_total >= 4.0
    tier_label = "👑 TIER S" if es_tier_s else "🟢 TIER A" if ev_total >= 3.0 else "🔴 DESCARTE"

    distancia = ((p_actual_input - p_disparo) / p_disparo) * 100
    penalizacion = 30 if distancia > 5.0 else 10 if distancia >= 2.0 else 0
    
    base_wr = wr_list[0]
    p_estructura = sum(1 for e in estados[1:] if "🔵 Compra" in e) * 10
    p_señal = 10 if "🔵 Compra" in estados[0] else 0
    idt_total = base_wr + (20 if es_tier_s else 0) + p_estructura + p_señal - penalizacion

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.subheader("🧪 Esperanza Matemática")
        st.metric("EV TOTAL DEL VALOR", f"{ev_total}", f"Calidad: {tier_label}")
        st.progress(min(max(ev_total/15, 0.0), 1.0)) # Barra visual de esperanza

    with m2:
        st.subheader("🎯 IDT (Disparo)")
        st.metric("PUNTUACIÓN TOTAL", f"{idt_total} pts", f"-{penalizacion} Persecución" if penalizacion > 0 else None)

    with m3:
        st.subheader("🛡️ ITE (Escudo)")
        p_stop = st.number_input("Precio Stop Loss $", value=float(p_actual_input * 0.95))
        ite = round(((p_actual_input - p_stop) / p_stop) * 100, 2)
        st.metric("TENSIÓN RIESGO", f"{ite}%")

    # --- 3. VERDICTO Y ACCIÓN ---
    if idt_total >= 100 and ite <= 5: verdict, col = "🔥 COMPRA OBLIGATORIA", "#00ffcc"
    elif
