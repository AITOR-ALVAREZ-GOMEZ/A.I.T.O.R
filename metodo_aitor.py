import streamlit as st
import pandas as pd
import yfinance as yf

# Configuración de página
st.set_page_config(page_title="A.I.T.O.R. 3.6 - Pro Terminal", layout="wide")

# Inicializar Base de Datos en la sesión
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=[
        "Ticker", "Tier", "EV Total", "IDT Puntos", "WR Gatillo", "ITE %", "Veredicto"
    ])

# --- 1. BARRA LATERAL (BUSCADOR ARRIBA) ---
st.sidebar.header("🔍 Buscador de Activos")
ticker_input = st.sidebar.text_input("TICKER (ej. CRDO, NVDA)", "CRDO").upper()

nombre_empresa = "Cargando..."
precio_mercado = 0.0
try:
    stock_data = yf.Ticker(ticker_input)
    info_json = stock_data.info
    nombre_empresa = info_json.get('longName', 'Ticker no detectado')
    precio_mercado = info_json.get('regularMarketPrice', info_json.get('previousClose', 0.0))
except Exception:
    st.sidebar.warning("Conectando con Wall Street...")

st.sidebar.subheader(f"🏢 {nombre_empresa}")
st.sidebar.write(f"**Precio Actual:** {precio_mercado} $")
st.sidebar.markdown("---")

# Filtros Libro Blanco (EPS por niveles)
st.sidebar.header("🏢 Calidad (Libro Blanco)")
eps_choice = st.sidebar.selectbox("Crecimiento EPS", 
                                 ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"], index=3)
puntos_eps = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}[eps_choice]

c_inst = st.sidebar.checkbox("Manos Fuertes (Institucional)", value=True)
c_sector = st.sidebar.checkbox("Líder Sector (RS > 90)", value=True)
puntos_fund = puntos_eps + (10 if c_inst else 0) + (10 if c_sector else 0)

# Control de Ejecución (Penalización por distancia)
st.sidebar.header("🎯 Control de Entrada")
p_gatillo = st.sidebar.number_input("Precio Señal Gatillo $", value=float(precio_mercado))
p_entrada = st.sidebar.number_input("Tu Precio Compra $", value=float(precio_mercado))

# Sistemas Fibonacci
st.sidebar.header("🧬 Sistemas Fractalidad")
secuencia = [st.sidebar.number_input(f"Sistema {i+1}", value=v, key=f"s{i}") for i, v in enumerate([1, 3, 8, 14, 21])]

# --- 2. INTERFAZ PRINCIPAL ---
tab_esc, tab_car, tab_per = st.tabs(["🔍 Escáner Cuantitativo", "💼 Cartera", "📊 Performance"])

with tab_esc:
    st.title(f"🚀 Análisis de Esperanza: {ticker_input}")
    
    # MATRIZ DE ENTRADA Y EV INDIVIDUAL
    ev_list = []
    wr_list = []
    estados = []
    cols = st.columns(5)
    
    for i, s_val in enumerate(secuencia):
        with cols[i]:
            st.markdown(f"### Sist. {s_val}D")
            wr = st.number_input(f"WR% {s_val}D", 0, 100, 50, key=f"w{i}")
            ratio = st.number_input(f"Ratio {s_val}D", 0.0, 100.0, 2.0, key=f"r{i}")
            estado = st.radio(f"Estado {s_val}D", ["🔴 Venta", "🔵 Compra"], key=f"e{i}")
            
            # Cálculo matemático de la ventaja
            wr_f = wr / 100
            ev_individual = round((wr_f * ratio) - ((1 - wr_f) * 1), 2)
            
            ev_list.append(ev_individual)
            wr_list.append(wr)
            estados.append(estado)
            st.metric("EV Individual", f"{ev_individual}")

    # --- 3. SECCIÓN DE CÁLCULOS (LÍNEA 74 CORREGIDA) ---
    ev_total = round(sum(ev_list) / 5, 2)
    es
