import streamlit as st
import pandas as pd
import yfinance as yf

# Configuración de página
st.set_page_config(page_title="A.I.T.O.R. 3.9 - Pro Terminal", layout="wide")

# Inicializar Base de Datos
if 'analisis' not in st.session_state:
    st.session_state.analisis = pd.DataFrame(columns=[
        "Ticker", "Tier", "Esperanza Final", "IDT Puntos", "ITE %", "Veredicto"
    ])

# --- 1. BARRA LATERAL (BUSCADOR Y CALIDAD) ---
st.sidebar.header("🔍 Buscador")
ticker_input = st.sidebar.text_input("TICKER", "CRDO").upper()

nombre_empresa = "Cargando..."
precio_mercado = 0.0
try:
    stock_data = yf.Ticker(ticker_input)
    nombre_empresa = stock_data.info.get('longName', 'Ticker no detectado')
    precio_mercado = stock_data.info.get('regularMarketPrice', stock_data.info.get('previousClose', 0.0))
except:
    pass

st.sidebar.subheader(f"🏢 {nombre_empresa}")
st.sidebar.markdown("---")

st.sidebar.header("📚 Calidad (Libro Blanco)")
# Los puntos del libro blanco ahora modifican la Esperanza Final
eps_choice = st.sidebar.selectbox("Crecimiento EPS", 
                                 ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"], index=3)
# Escala: Explosivo suma 1.5 a la EV, Alto 1.0, Medio 0.5
bonus_ev_eps = {"Bajo (<10%)": 0.0, "Medio (>10%)": 0.5, "Alto (>15%)": 1.0, "Explosivo (>25%)": 1.5}[eps_choice]

c_inst = st.sidebar.checkbox("Institucional (Smart Money)", value=True)
c_sector = st.sidebar.checkbox("Líder Sector (RS > 90)", value=True)

# Plus de Esperanza por Calidad
plus_calidad = bonus_ev_eps + (1.0 if c_inst else 0) + (1.0 if c_sector else 0)

st.sidebar.header("🎯 Control de Entrada")
p_gatillo = st.sidebar.number_input("Precio Señal $", value=float(precio_mercado))
p_entrada = st.sidebar.number_input("Precio Compra $", value=float(precio_mercado))

st.sidebar.header("🧬 Sistemas Fractalidad")
secuencia = [st.sidebar.number_input(f"Sistema {i+1}", value=v, key=f"s{i}") for i, v in enumerate([1, 3, 8, 14, 21])]

# --- 2. INTERFAZ PRINCIPAL ---
tab_esc, tab_car, tab_per = st.tabs(["🔍 Escáner Integral", "💼 Cartera", "📊 Performance"])

with tab_esc:
    st.title(f"🚀 Análisis de {ticker_input}")
    
    ev_list, wr_list, estados = [], [], []
    cols = st.columns(5)
    
    for i, s_val in enumerate(secuencia):
        with cols[i]:
            st.markdown(f"### Sist. {s_val}D")
            wr = st.number_input(f"WR% {s_val}D", 0, 100, 50, key=f"w{i}")
            ratio = st.number_input(f"Ratio {s_val}D", 0.0, 100.0, 2.0, key=f"r{i}")
            estado = st.radio(f"Estado {s_val}D", ["🔴 Venta", "🔵 Compra"], key=f"e{i}")
            
            wr_f = wr / 100
            ev_ind = round((wr_f * ratio) - ((1 - wr_f) * 1), 2)
            ev_list.append(ev_ind); wr_list.append(wr); estados.append(estado)
            st.metric("EV Matemático", f"{ev_ind}")

    # --- CÁLCULO DE ESPERANZA FINAL ---
    ev_matematico = sum(ev_list) / 5
    # Aquí es donde ocurre la magia: Sumamos el plus de calidad
    esperanza_final = round(ev_matematico + plus_calidad, 2)
    
    tier_label = "👑 TIER S" if esperanza_final >= 8.0 else "🟢 TIER A" if esperanza_final >= 4
