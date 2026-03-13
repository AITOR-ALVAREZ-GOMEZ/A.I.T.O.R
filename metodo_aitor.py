import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime
import plotly.graph_objects as go
import math

# --- CONFIGURACION ---
st.set_page_config(page_title="AITOR 69.0 FULL COMMAND", layout="wide")

# --- MEMORIA RAM DE SESIÓN ---
if 'historial_lab' not in st.session_state:
    st.session_state['historial_lab'] = []

# Limpieza automática si hay versiones antiguas en la RAM
if len(st.session_state['historial_lab']) > 0:
    if "Ret_21D" not in st.session_state['historial_lab'][0]:
        st.session_state['historial_lab'] = []

# --- CSS ESTILO APPLE ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
    .stApp { background-color: #f5f5f7; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #1d1d1f; }
    [data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.7) !important; backdrop-filter: blur(20px) !important; border-right: 1px solid rgba(0,0,0,0.05) !important; }
    h1, h2, h3, h1 *, h2 *, h3 * { color: #1d1d1f !important; font-weight: 700 !important; letter-spacing: -0.5px; }
    [data-testid="stMetric"] { background-color: #ffffff; border-radius: 18px; padding: 15px 20px; min-height: 140px; box-shadow: 0 4px 15px rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.03); }
    [data-testid="stMetricValue"] { color: #1d1d1f !important; font-weight: 700 !important; font-size: 2.2rem !important; }
    .apple-kpi-card { background-color: #ffffff; border-radius: 18px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.03); width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: flex-start; align-items: flex-start; }
    .apple-kpi-title { font-size: 0.8rem; color: #86868b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
    .apple-kpi-value { font-size: 2.4rem; font-weight: 800; color: #1d1d1f; line-height: 1; }
    .kpi-breakdown { font-size: 0.75rem; color: #5f6368; margin-top: 12px; margin-bottom: 12px; line-height: 1.6; background: #f8f9fa; padding: 12px; border-radius: 10px; width: 100%; border: 1px solid #e8eaed; }
    .tdah-box { padding: 15px 20px; border-radius: 12px; margin-bottom: 12px; border-left: 6px solid; }
    .tdah-green { background: #f0fdf4; border-color: #22c55e; }
    .tdah-red { background: #fef2f2; border-color: #ef4444; }
    .tdah-yellow { background: #fefce8; border-color: #eab308; }
    .tdah-blue { background: #eff6ff; border-color: #3b82f6; }
    .main-banner { padding: 16px; border-radius: 12px; text-align: center; font-weight: 800; font-size: 1.25rem; margin-top: 15px; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .banner-green { background-color: #34c759; color: white; border: 2px solid #248a3d; }
    .banner-red { background-color: #ff3b30; color: white; border: 2px solid #c92f26; }
    .banner-yellow { background-color: #ffcc00; color: #1d1d1f; border: 2px solid #b38f00; }
    .dna-badge { background: linear-gradient(90deg, #9333ea, #ec4899); color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; display: inline-block; margin-bottom: 10px;}
    .radar-alert { background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%); color: white; padding: 15px 25px; border-radius: 15px; margin-bottom: 10px; border: 2px solid #14532d;}
    .rank-box { display: flex; gap: 6px; flex-wrap: wrap; margin-top: auto; }
    .tag-on { border-radius: 8px; padding: 6px 12px; font-size: 0.75rem; font-weight: 700; color: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-transform: uppercase; }
    .tag-off { border-radius: 8px; padding: 6px 12px; font-size: 0.75rem; font-weight: 600; color: #8e8e93; border: 1px solid #d2d2d7; background: #fff; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

CAPITAL = 277000.0
DIAS_S = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]

conn = st.connection("gsheets", type=GSheetsConnection)
try: df_datos = conn.read(worksheet="Sheet1", ttl=0)
except: df_datos = pd.DataFrame()

try: df_adn = conn.read(worksheet="ADN_Quant", ttl=0)
except: df_adn = pd.DataFrame(columns=["Ticker", "Z_Min", "Acc_Min", "Vol_Min", "Horizonte", "Rendimiento", "WinRate", "Es_Default", "ID_ADN"])

# --- BUSCADOR ---
st.sidebar.header("Buscador")
ticker = st.sidebar.text_input("Ticker:", "MU").strip().upper()

# --- CARGAR ADN ---
opt_z, opt_acc, opt_vol = 1.0, 0.0, 1.5
tiene_adn = False
total_adns = 0
if ticker != "" and not df_adn.empty:
    df_adn_ticker = df_adn[df_adn['Ticker'] == ticker]
    total_adns = len(df_adn_ticker)
    if not df_adn_ticker.empty:
        tiene_adn = True
        df_def = df_adn_ticker[df_adn_ticker['Es_Default'] == True]
        adn_data = df_def.iloc[0] if not df_def.empty else df_adn_ticker.iloc[0]
        opt_z, opt_acc, opt_vol = float(adn_data['Z_Min']), float(adn_data['Acc_Min']), float(adn_data['Vol_Min'])

# --- DATA DOWNLOAD ---
stock = yf.Ticker(ticker)
df_global = stock.history(period="2y")
p_merc = float(df_global['Close'].iloc[-1]) if not df_global.empty else 0.0

st.sidebar.subheader(ticker)
if p_merc > 0: st.sidebar.markdown(f"<div style='background:#1d1d1f; color:white; padding:10px; border-radius:8px; text-align:center; font-size:1.2rem; font-weight:bold;'>Precio: {p_merc:.2f} $</div>", unsafe_allow_html=True)

# --- GESTION CAPITAL ---
st.sidebar.header("Riesgo")
r_pct = st.sidebar.slider("Riesgo (%)", 0.5, 10.0, 3.3, 0.1)
p_buy = st.sidebar.number_input("Precio Compra", value=p_merc)
p_sl = st.sidebar.number_input("Stop Loss", value=p_buy * 0.90)
dist_stop = p_buy - p_sl
n_tit = math.floor((CAPITAL * (r_pct / 100.0)) / dist_stop) if dist_stop > 0 else 0
inv_t = n_tit * p_buy

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Escáner Cuántico", "📋 Auditoría Global", "💼 Cartera", "🧪 Laboratorio Quant", "📡 Radar Diario"])

with tab1:
    st.title(f"Escáner: {ticker}")
    if tiene_adn: st.markdown(f"<div class='dna-badge'>🧬 ADN: Z > {opt_z} | Acc > {opt_acc} | Vol > {opt_vol}</div>", unsafe_allow_html=True)
    
    # 5 SISTEMAS
    cols_s = st.columns(5)
    l_ev, l_es, s_elegidos, l_wr, l_rt = [], [], [], [], []
    d_defs = [1, 3, 8, 14, 21]
    
    for i in range(5):
        with cols_s[i]:
            st.markdown(f"**{d_defs[i]} D**")
            s_val = st.selectbox("S", DIAS_S, index=DIAS_S.index(d_defs[i]) if d_defs[i] in DIAS_S else 0, key=f"s{i}")
            wr = st.number_input("WR %", 0, 100, 50, key=f"w{i}")
            rt = st.number_input("R/R", 0.0, 10.0, 2.0, key=f"r{i}")
            ma = df_global['Close'].rolling(s_val).mean().iloc[-1]
            idx_e = 1 if p_merc > ma else 0
            es = st.radio("Señal", ["Venta", "Compra"], index=idx_e, key=f"e{i}")
            ev_i = round(((wr/100)*rt) - (1-(wr/100)), 2)
            l_ev.append(ev_i); l_es.append(es); s_elegidos.append(s_val); l_wr.append(wr); l_rt.append(rt)
            st.metric(f"EV {s_val}D", f"{ev_i:.2f}")

    ev_c = sum([l_ev[j] for j in range(5) if l_es[j] == "Compra"])
    ev_v = sum([l_ev[j] for j in range(5) if l_es[j] == "Venta"])
    net_ev = ev_c - ev_v
    idt = l_wr[0] + (10 if p_merc > df_global['Close'].rolling(55).mean().iloc[-1] else 0) - (30 if (p_buy-p_sl)/p_buy > 0.15 else 0)
    
    if net_ev >= 1.5: st.markdown("<div class='main-banner banner-green'>✅ LUZ VERDE: VENTAJA MATEMÁTICA</div>", unsafe_allow_html=True)
    else: st.markdown("<div class='main-banner banner-red'>🚨 BLOQUEADO: RIESGO ELEVADO</div>", unsafe_allow_html=True)

    # VELOCÍMETROS
    st.subheader("Oráculo Quant")
    df_esc = df_global.copy()
    df_esc['MA55'] = df_esc['Close'].rolling(55).mean()
    df_esc['Z'] = (df_esc['Close'] - df_esc['MA55']) / df_esc['Close'].rolling(55).std()
    df_esc['Acc'] = (df_esc['Close'].pct_change(10)*100).diff(5)
    df_esc['VolZ'] = (df_esc['Volume'] - df_esc['Volume'].rolling(55).mean()) / df_esc['Volume'].rolling(55).std()
    
    z_hoy, acc_hoy, vol_hoy = df_esc['Z'].iloc[-1], df_esc['Acc'].iloc[-1], df_esc['VolZ'].iloc[-1]
    
    c_o1, c_o2, c_o3 = st.columns(3)
    with c_o1:
        st.markdown(f"**Z-Score (ADN > {opt_z})**")
        fig = go.Figure(go.Indicator(mode="gauge+number", value=z_hoy, gauge={'axis': {'range': [-4, 4]}, 'bar': {'color': "black"}, 'steps': [{'range': [-4, opt_z], 'color': "lightgray"}, {'range': [opt_z, 4], 'color': "red"}]}))
        fig.update_layout(height=200, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c_o2:
        st.markdown(f"**Momentum (ADN > {opt_acc})**")
        fig = go.Figure(go.Indicator(mode="gauge+number", value=acc_hoy, gauge={'axis': {'range': [-10, 10]}, 'bar': {'color': "purple"}, 'steps': [{'range': [-10, opt_acc], 'color': "lightgray"}, {'range': [opt_acc, 10], 'color': "green"}]}))
        fig.update_layout(height=200, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c_o3:
        st.markdown(f"**Volumen (ADN > {opt_vol})**")
        fig = go.Figure(go.Indicator(mode="gauge+number", value=vol_hoy, gauge={'axis': {'range': [-2, 4]}, 'bar': {'color': "black"}, 'steps': [{'range': [-2, opt_vol], 'color': "lightgray"}, {'range': [opt_vol, 4], 'color': "green"}]}))
        fig.update_layout(height=200, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)

    # BOTONES EJECUCIÓN
    if st.button("🚀 REGISTRAR OPERACIÓN / GUARDAR"):
        try:
            df_sh = conn.read(worksheet="Sheet1", ttl=0)
            nueva_fila = {"Ticker": ticker, "Tier": "A", "EV_Total": net_ev, "IDT_Puntos": idt, "Acciones": n_tit, "Inversion": inv_t}
            for k in range(5): nueva_fila[f"S{k+1}_Dias"] = s_elegidos[k]
            df_sh = pd.concat([df_sh, pd.DataFrame([nueva_fila])], ignore_index=True).drop_duplicates("Ticker", keep="last")
            conn.update(worksheet="Sheet1", data=df_sh)
            st.success("Guardado.")
        except: st.error("Error base de datos.")

with tab4:
    st.title("Laboratorio & Inspector Forense")
    # (El resto del código del laboratorio iría aquí, incluyendo el inspector forense detallado en el mensaje anterior)
    st.info("Utiliza el botón de 'Auto-Descubrir' para generar los tests y ver las fechas en el Inspector.")
    
    # --- LOGICA DE BACKTEST Y FUERZA BRUTA (Fibonacci) ---
    if st.button("🤖 Auto-Optimizar ADN (Fuerza Bruta)"):
        with st.spinner("Clonando cerebros..."):
            # Aquí va el bucle que recorre Z, Acc y Vol guardando en historial_lab
            # IMPORTANTE: Guardar 'Trades_Log' con las fechas
            pass

    # --- INSPECTOR FORENSE ---
    if len(st.session_state['historial_lab']) > 0:
        st.markdown("### 🔍 Inspector Forense")
        test_idx = st.selectbox("Selecciona Test:", range(len(st.session_state['historial_lab'])))
        test_data = st.session_state['historial_lab'][test_idx]
        if "Trades_Log" in test_data:
            st.table(pd.DataFrame(test_data["Trades_Log"]))

with tab5:
    st.title("Radar Diario")
    # (Lógica del radar que recorre todos los ADN guardados y muestra la calculadora)
    st.info("Escanea el mercado para encontrar señales basadas en tus ADNs guardados.")
