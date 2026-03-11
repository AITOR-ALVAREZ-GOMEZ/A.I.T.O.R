import streamlit as st
import pandas as pd
import yfinance as yf

# Configuración de página
st.set_page_config(page_title="A.I.T.O.R. 3.4 - Pro Terminal", layout="wide")

# Inicializar Base de Datos
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=[
        "Ticker", "Tier", "EV Total", "IDT Puntos", "WR Gatillo", "ITE %", "Veredicto"
    ])

# --- 1. BARRA LATERAL (BUSCADOR ARRIBA DEL TODO) ---
st.sidebar.header("🔍 Buscador de Activos")
ticker_input = st.sidebar.text_input("INTRODUCE TICKER (ej. CRDO)", "CRDO").upper()

# Motor de búsqueda real
nombre_empresa = "Cargando..."
precio_mercado = 0.0
try:
    stock_data = yf.Ticker(ticker_input)
    nombre_empresa = stock_data.info.get('longName', 'Ticker no detectado')
    precio_mercado = stock_data.info.get('regularMarketPrice', stock_data.info.get('previousClose', 0.0))
except Exception:
    st.sidebar.warning("No se pudo conectar con Wall Street.")

st.sidebar.subheader(f"🏢 {nombre_empresa}")
st.sidebar.write(f"**Precio Actual:** {precio_mercado} $")
st.sidebar.markdown("---")

# Filtros de Calidad (Niveles de EPS)
st.sidebar.header("🏢 Calidad (Libro Blanco)")
eps_choice = st.sidebar.selectbox("Crecimiento EPS", 
                                 ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"], index=3)
puntos_eps = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}[eps_choice]

c_inst = st.sidebar.checkbox("Instituciones (Smart Money)", value=True)
c_sector = st.sidebar.checkbox("Líder Sector (RS > 90)", value=True)
puntos_fund = puntos_eps + (10 if c_inst else 0) + (10 if c_sector else 0)

# Control de Ejecución
st.sidebar.header("🎯 Control de Entrada")
p_gatillo = st.sidebar.number_input("Precio Señal (Gatillo) $", value=float(precio_mercado))
p_entrada = st.sidebar.number_input("Precio Compra Deseado $", value=float(precio_mercado))

# Configuración de Sistemas
st.sidebar.header("🧬 Sistemas (Fractalidad)")
secuencia = [st.sidebar.number_input(f"Sistema {i+1}", value=v, key=f"s{i}") for i, v in enumerate([1, 3, 8, 14, 21])]

# --- 2. INTERFAZ PRINCIPAL ---
tab_esc, tab_car, tab_per = st.tabs(["🔍 Escáner Cuantitativo", "💼 Cartera", "📊 Performance"])

with tab_esc:
    st.title(f"🚀 Análisis de Esperanza: {ticker_input}")
    
    # MATRIZ DE ENTRADA Y EV INDIVIDUAL
    ev_list, wr_list, estados = [], [], []
    cols = st.columns(5)
    
    for i, s_val in enumerate(secuencia):
        with cols[i]:
            st.markdown(f"### Sist. {s_val}D")
            wr = st.number_input(f"WR% {s_val}D", 0, 100, 50, key=f"w{i}")
            ratio = st.number_input(f"Ratio {s_val}D", 0.0, 100.0, 2.0, key=f"r{i}")
            estado = st.radio(f"Estado {s_val}D", ["🔴 Venta", "🔵 Compra"], key=f"e{i}")
            
            # Cálculo EV: (WR * Ratio) - ((1-WR) * 1)
            wr_f = wr / 100
            ev_ind = round((wr_f * ratio) - ((1 - wr_f) * 1), 2)
            
            ev_list.append(ev_ind)
            wr_list.append(wr)
            estados.append(estado)
            st.metric("EV Individual", f"{ev_ind}")

    # CÁLCULOS CENTRALES
    ev_total = round(sum(ev_list) / 5, 2)
    es_tier_s = puntos_fund >= 30 and ev_total >= 4.0
    tier_label = "👑 TIER S" if es_tier_s else "🟢 TIER A" if ev_total >= 3.0 else "🔴 DESCARTE"

    dist_gat = ((p_entrada - p_gatillo) / p_gatillo) * 100
    penalizacion = 30 if dist_gat > 5.0 else 10 if dist_gat >= 2.0 else 0
    
    base_wr = wr_list[0]
    p_estruc = sum(1 for e in estados[1:] if "🔵" in e) * 10
    p_señal = 10 if "🔵" in estados[0] else 0
    idt_total = base_wr + (20 if es_tier_s else 0) + p_estruc + p_señal - penalizacion

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.subheader("🧪 Esperanza Matemática")
        st.metric("EV TOTAL", f"{ev_total}", f"Calidad: {tier_label}")
    
    with m2:
        st.subheader("🎯 Potencial IDT")
        st.metric("PUNTUACIÓN", f"{idt_total} pts", f"-{penalizacion} Distancia" if penalizacion > 0
