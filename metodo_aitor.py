import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime
import plotly.graph_objects as go
import math

# --- CONFIGURACION ---
st.set_page_config(page_title="AITOR 65.0 SYNC ENGINE", layout="wide")

# --- MEMORIA RAM DE SESIÓN ---
if 'historial_lab' not in st.session_state:
    st.session_state['historial_lab'] = []

# Limpieza de memoria vieja por si cambian las columnas
if len(st.session_state['historial_lab']) > 0:
    if "Ret_21D" not in st.session_state['historial_lab'][0]:
        st.session_state['historial_lab'] = []

# --- CSS ESTILO APPLE, TDAH FRIENDLY ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
    .stApp { background-color: #f5f5f7; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #1d1d1f; }
    [data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.7) !important; backdrop-filter: blur(20px) !important; border-right: 1px solid rgba(0,0,0,0.05) !important; }
    h1, h2, h3, h1 *, h2 *, h3 * { color: #1d1d1f !important; font-weight: 700 !important; letter-spacing: -0.5px; }
    [data-testid="stMetric"] { background-color: #ffffff; border-radius: 18px; padding: 15px 20px; min-height: 140px; box-shadow: 0 4px 15px rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.03); }
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * { color: #1d1d1f !important; font-weight: 700 !important; font-size: 2.2rem !important; }
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * { color: #86868b !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.5px; }
    .stTextInput input, .stNumberInput input, [data-baseweb="select"] > div { background-color: #ffffff !important; border-radius: 12px !important; border: 1px solid rgba(0,0,0,0.1) !important; }
    .stButton>button { background: linear-gradient(180deg, #2b8af7 0%, #0071e3 100%) !important; color: white !important; border: none !important; border-radius: 20px !important; padding: 10px 24px !important; font-weight: 600 !important; box-shadow: 0 4px 14px rgba(0, 113, 227, 0.3) !important; transition: all 0.2s ease;}
    .stButton>button:active { transform: scale(0.98); }
    
    .apple-kpi-card { background-color: #ffffff; border-radius: 18px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.03); width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: flex-start; align-items: flex-start; }
    .apple-kpi-title { font-size: 0.8rem; color: #86868b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; }
    .apple-kpi-value { font-size: 2.4rem; font-weight: 800; color: #1d1d1f; line-height: 1; }
    
    .kpi-breakdown { font-size: 0.75rem; color: #5f6368; margin-top: 12px; margin-bottom: 12px; line-height: 1.6; background: #f8f9fa; padding: 12px; border-radius: 10px; width: 100%; border: 1px solid #e8eaed; }
    .kpi-breakdown b { color: #1d1d1f; }
    
    .rank-box { display: flex; gap: 6px; flex-wrap: wrap; margin-top: auto; }
    .tag-on { border-radius: 8px; padding: 6px 12px; font-size: 0.75rem; font-weight: 700; color: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-transform: uppercase; letter-spacing: 0.5px;}
    .tag-off { border-radius: 8px; padding: 6px 12px; font-size: 0.75rem; font-weight: 600; color: #8e8e93; border: 1px solid #d2d2d7; background: #fff; text-transform: uppercase; letter-spacing: 0.5px;}
    
    .quant-card { background: #fff; padding: 20px; border-radius: 15px; border: 1px solid #e5e5ea; height: 100%; box-shadow: 0 2px 10px rgba(0,0,0,0.02); margin-bottom: 15px;}
    .quant-title { font-size: 1.1rem; font-weight: 700; color: #1d1d1f; margin-bottom: 8px; }
    .quant-desc { font-size: 0.85rem; color: #86868b; line-height: 1.4; margin-bottom: 15px; }
    .tdah-box { padding: 15px 20px; border-radius: 12px; margin-bottom: 12px; border-left: 6px solid; }
    .tdah-green { background: #f0fdf4; border-color: #22c55e; }
    .tdah-red { background: #fef2f2; border-color: #ef4444; }
    .tdah-yellow { background: #fefce8; border-color: #eab308; }
    .tdah-blue { background: #eff6ff; border-color: #3b82f6; }
    .tdah-title { font-weight: 800; font-size: 1.05rem; margin-bottom: 4px; color: #111827;}
    .tdah-text { font-size: 0.95rem; color: #374151; line-height: 1.4;}
    
    .champion-card { background: linear-gradient(135deg, #fffbeb 0%, #fff3c4 100%); border: 2px solid #fbbf24; border-radius: 15px; padding: 20px; box-shadow: 0 10px 25px rgba(251, 191, 36, 0.2); margin-top: 20px; margin-bottom: 20px;}
    .champion-title { color: #b45309; font-weight: 900; font-size: 1.4rem; margin-bottom: 10px; display: flex; align-items: center; gap: 10px;}
    .champion-stats { display: flex; gap: 20px; margin-top: 15px; flex-wrap: wrap;}
    .stat-box { background: white; padding: 10px 15px; border-radius: 10px; border: 1px solid #fcd34d; font-weight: bold; color: #78350f;}
    
    .radar-alert { background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%); color: white; padding: 25px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(34, 197, 94, 0.3); border: 2px solid #14532d;}
    .radar-alert h2 { color: white !important; margin-top: 0; }
    .radar-wait { background: #f8f9fa; border: 1px dashed #d1d5db; padding: 20px; border-radius: 15px; color: #6b7280; text-align: center; margin-bottom: 15px;}
    
    @keyframes flash-red { 0% { background-color: #ff3b30; color: white; } 50% { background-color: #ffe5e5; color: #ff3b30; } 100% { background-color: #ff3b30; color: white; } }
    @keyframes pulse-green { 0% { background-color: #34c759; color: white; } 50% { background-color: #e5fbee; color: #188038; } 100% { background-color: #34c759; color: white; } }
    @keyframes pulse-yellow { 0% { background-color: #ffcc00; color: #1d1d1f; } 50% { background-color: #fff9e6; color: #b38f00; } 100% { background-color: #ffcc00; color: #1d1d1f; } }
    
    .main-banner { padding: 16px; border-radius: 12px; text-align: center; font-weight: 800; font-size: 1.25rem; margin-top: 15px; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .banner-red { animation: flash-red 1.5s infinite; border: 2px solid #ff3b30; }
    .banner-green { animation: pulse-green 2s infinite; border: 2px solid #34c759; }
    .banner-yellow { animation: pulse-yellow 2s infinite; border: 2px solid #ffcc00; }
    .dna-badge { display: inline-block; background: linear-gradient(90deg, #9333ea, #ec4899); color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(236, 72, 153, 0.4);}
    
    [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
</style>
""", unsafe_allow_html=True)

CAPITAL = 277000.0
DIAS = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]
A_ACTUAL = datetime.datetime.now().year

COL_DB = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto", "Acciones", "Inversion"]
for i in range(1, 6): COL_DB.extend([f"S{i}_Dias", f"W{i}", f"R{i}"])

conn = st.connection("gsheets", type=GSheetsConnection)

# CACHÉ AL 0: Lectura directa sin fantasmas
try: df_datos = conn.read(worksheet="Sheet1", ttl=0) 
except: df_datos = pd.DataFrame(columns=COL_DB)

try: df_adn = conn.read(worksheet="ADN_Quant", ttl=0)
except: df_adn = pd.DataFrame(columns=["Ticker", "Z_Min", "Acc_Min", "Vol_Min", "Horizonte", "Rendimiento"])

# =====================================================================
# BUSCADOR LATERAL 
# =====================================================================
st.sidebar.header("Buscador de Activos")
opciones_bd = df_datos['Ticker'].dropna().unique().tolist() if not df_datos.empty else []
ticker_manual = st.sidebar.text_input("Nuevo Ticker (Ej: MU):", "").strip().upper()
ticker_lista = st.sidebar.selectbox("O cargar de Auditoría:", [""] + opciones_bd)
ticker = ticker_manual if ticker_manual != "" else ticker_lista
if ticker == "": ticker = "MU"

# --- LECTURA DEL ADN GENÉTICO EN DIRECTO ---
opt_z, opt_acc, opt_vol = 1.0, 0.0, 1.5 
tiene_adn = False
if ticker != "" and not df_adn.empty and "Ticker" in df_adn.columns:
    df_adn_ticker = df_adn[df_adn['Ticker'] == ticker]
    if not df_adn_ticker.empty:
        tiene_adn = True
        adn_data = df_adn_ticker.iloc[-1]
        opt_z = float(adn_data['Z_Min'])
        opt_acc = float(adn_data['Acc_Min'])
        opt_vol = float(adn_data['Vol_Min'])

nom_emp, p_merc, prev_1y, eps_base, atr_val = "Buscando...", 0.0, 0.0, 0.0, 0.0
df_global = pd.DataFrame()

if ticker != "":
    stock = yf.Ticker(ticker)
    try:
        df_global = stock.history(period="2y")
        if not df_global.empty: 
            p_merc = float(df_global['Close'].iloc[-1])
            high_low = df_global['High'] - df_global['Low']
            high_close = np.abs(df_global['High'] - df_global['Close'].shift())
            low_close = np.abs(df_global['Low'] - df_global['Close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            atr_val = true_range.rolling(14).mean().iloc[-1]
    except: pass
    try:
        info = stock.info
        nom_emp = info.get("longName", info.get("shortName", ticker))
        if p_merc == 0.0: p_merc = float(info.get("currentPrice", info.get("regularMarketPrice", 0.0)))
        eps_base = info.get("trailingEps", 0.0)
        f_eps = info.get("forwardEps", 0.0)
        if eps_base is not None and f_eps is not None and eps_base > 0 and f_eps > eps_base: prev_1y = (f_eps - eps_base) / eps_base
        else: prev_1y = info.get("revenueGrowth", 0.0); prev_1y = 0.0 if prev_1y is None else prev_1y
    except: 
        if nom_emp == "Buscando...": nom_emp = ticker

st.sidebar.subheader(nom_emp)
if p_merc > 0: st.sidebar.markdown(f"<div style='background:#1d1d1f; color:white; padding:10px; border-radius:8px; text-align:center; font-size:1.2rem; font-weight:bold; margin-bottom:5px;'>Precio Mercado: {p_merc:.2f} $</div>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header("Calidad (Libro Blanco)")
if prev_1y > 0 and eps_base > 0: st.sidebar.info(f"{A_ACTUAL}: {eps_base * (1 + prev_1y):.2f} $")

ops = ["Bajo (<10%)", "Medio (>10%)", "Alto (>15%)", "Explosivo (>25%)"]
i_auto = 3 if prev_1y > 0.25 else 2 if prev_1y > 0.15 else 1 if prev_1y > 0.10 else 0
v_eps = st.sidebar.selectbox("Crecimiento EPS", ops, index=i_auto)
dict_eps = {"Bajo (<10%)": 0, "Medio (>10%)": 5, "Alto (>15%)": 10, "Explosivo (>25%)": 15}
pts_eps = dict_eps[v_eps]
c_inst = st.sidebar.checkbox("Manos Fuertes", value=True)
c_sect = st.sidebar.checkbox("Lider Sector", value=True)
bono = pts_eps + (10 if c_inst else 0) + (10 if c_sect else 0)
ev_plus = bono / 7.0

# ---------------------------------------------------------------------
# CALCULADORA DE RIESGO (ESTABLE)
# ---------------------------------------------------------------------
st.sidebar.header("Gestion Capital")
r_pct = st.sidebar.slider("Riesgo (%)", min_value=0.5, max_value=10.0, value=3.3, step=0.1)
p_buy = st.sidebar.number_input("Precio Compra", value=float(p_merc), key=f"buy_{ticker}")
stop_sugerido_auto = p_buy - (2 * atr_val) if atr_val > 0 else p_buy * 0.95
p_sl = st.sidebar.number_input("Stop Loss", value=float(stop_sugerido_auto), key=f"sl_{ticker}")

distancia_stop = p_buy - p_sl
if distancia_stop > 0 and p_buy > 0:
    riesgo_euros = CAPITAL * (r_pct / 100.0)
    n_tit = math.floor(riesgo_euros / distancia_stop)
    inv_t = n_tit * p_buy
else:
    n_tit = 0; inv_t = 0

if n_tit > 0:
    st.sidebar.markdown(f"<div style='font-size:0.8rem; color:#86868b;'>Acciones a comprar: <b>{n_tit}</b></div>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<div style='font-size:0.8rem; color:#86868b;'>Inversión Total: <b>{inv_t:,.2f} $</b></div>", unsafe_allow_html=True)

# =====================================================================
# SISTEMA DE PESTAÑAS 
# =====================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Escáner Cuántico", "📋 Auditoría Global", "💼 Cartera en Vivo", "🧪 Laboratorio Quant", "📡 Radar Diario"])

# ---------------------------------------------------------------------
# PESTAÑA 1: ESCÁNER INTELIGENTE
# ---------------------------------------------------------------------
with tab1:
    st.title("Análisis de Entrada: " + ticker)
    
    # MENSAJE DE ÉXITO TRAS RECARGA
    if st.session_state.get('adn_saved_success', False):
        st.success("✅ ¡ADN Sincronizado! El Escáner y los Velocímetros se han adaptado automáticamente a tu nuevo campeón.")
        st.session_state['adn_saved_success'] = False
        
    if st.session_state.get('scan_saved_success', False):
        st.toast("✅ Operación guardada/enviada correctamente a la base de datos.", icon="💾")
        st.session_state['scan_saved_success'] = False
    
    if tiene_adn:
        st.markdown("<div class='dna-badge'>🧬 ADN CUANTITATIVO CARGADO</div>", unsafe_allow_html=True)
        st.caption(f"El Escáner ha mutado para **{ticker}**. Límites adaptados en base a tu Backtesting: Volumen > {opt_vol if opt_vol!=-99 else 'OFF'}σ | Aceleración > {opt_acc if opt_acc!=-99 else 'OFF'} | Tensión > {opt_z if opt_z!=-99 else 'OFF'}σ")
    else:
        st.caption("Usando valores estándar por defecto. Usa la pestaña 'Laboratorio Quant' para guardar un ADN personalizado.")
    
    s_elegidos, l_ev, l_wr, l_rt, l_es = [], [], [], [], []
    cols = st.columns(5)
    d_defs, w_defs, r_defs = [1, 3, 8, 14, 21], [50]*5, [2.0]*5
    
    if ticker != "" and not df_datos.empty and "Ticker" in df_datos.columns:
        df_filtro = df_datos[df_datos["Ticker"] == ticker]
        if len(df_filtro) > 0:
            fila = df_filtro.iloc[-1]
            try:
                for idx in range(5):
                    val_s = int(fila[f"S{idx+1}_Dias"])
                    if val_s in DIAS: d_defs[idx] = val_s
                    w_defs[idx] = int(fila[f"W{idx+1}"])
                    r_defs[idx] = float(fila[f"R{idx+1}"])
            except: pass

    # CAJAS DE LOS 5 SISTEMAS
    for i in range(5):
        with cols[i]:
            st.markdown(f"**{d_defs[i]} D**")
            idx_d = DIAS.index(d_defs[i])
            s_val = st.selectbox("S", DIAS, index=idx_d, key=f"d{i}", label_visibility="collapsed")
            wr = st.number_input("WR %", 0, 100, w_defs[i], key=f"w{i}")
            rt = st.number_input("R/R", 0.0, 50.0, r_defs[i], key=f"r{i}")
            ma_val = 0.0
            senal_auto = "Venta"
            idx_radio = 0
            if not df_global.empty:
                try:
                    ma_val = df_global['Close'].rolling(window=s_val).mean().iloc[-1]
                    if p_merc > ma_val: idx_radio = 1
                except: pass
            st.markdown(f"<div style='font-size:0.85rem; color:#86868b; margin-top:5px; text-align:center;'>Media: <b>{ma_val:.2f}</b></div>", unsafe_allow_html=True)
            es = st.radio("Señal", ["Venta", "Compra"], index=idx_radio, key=f"e{i}")
            ev_i = round(((wr / 100.0) * rt) - ((1.0 - (wr / 100.0)) * 1.0), 2)
            s_elegidos.append(s_val); l_ev.append(ev_i); l_wr.append(wr); l_rt.append(rt); l_es.append(es)
            st.markdown(f"<div style='text-align:center; padding:10px; background:#fff; border-radius:10px; border:1px solid #e5e5ea; margin-top:5px;'><div style='color:#86868b; font-size:0.75rem; font-weight:bold;'>EV {s_val}D</div><div style='font-size:1.4rem; font-weight:800; color:#1d1d1f;'>{ev_i:.2f}</div></div>", unsafe_allow_html=True)

    ev_compra = sum([l_ev[i] for i in range(5) if l_es[i] == "Compra"])
    ev_venta = sum([l_ev[i] for i in range(5) if l_es[i] == "Venta"])
    net_ev = ev_compra - ev_venta 
    ev_tot = round(net_ev + ev_plus, 2) 
    ite = round(((p_buy - p_sl) / p_buy) * 100.0, 2) if p_buy > 0 else 0.0
    penal = 30 if ite > 15 else 0 
    p_estr = sum(10 for e in l_es[1:] if e == "Compra")
    p_sen = 10 if l_es[0] == "Compra" else 0
    idt = l_wr[0] + bono + p_estr + p_sen - penal

    if net_ev >= 1.5: st.markdown("<div class='main-banner banner-green'>✅ LUZ VERDE ESTRUCTURAL: Ventaja Matemática Confirmada. APTO PARA COMPRAR.</div>", unsafe_allow_html=True)
    elif net_ev >= 0: st.markdown("<div class='main-banner banner-yellow'>⚠️ PRECAUCIÓN: Fuerza Neta Débil. Apto solo con POSICIÓN REDUCIDA.</div>", unsafe_allow_html=True)
    else: st.markdown("<div class='main-banner banner-red'>🚨 SISTEMA BLOQUEADO: Esperanza Matemática Negativa. PROHIBIDO COMPRAR.</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🏛️ Auditoría Matemática Central")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        h_ev = "<div class='rank-box'>"
        if ev_tot >= 10: h_ev += "<div class='tag-on' style='background:#34c759;'>TIER S</div><div class='tag-off'>TIER A</div><div class='tag-off'>DESCARTE</div>"
        elif ev_tot >= 5: h_ev += "<div class='tag-off'>TIER S</div><div class='tag-on' style='background:#2b8af7;'>TIER A</div><div class='tag-off'>DESCARTE</div>"
        else: h_ev += "<div class='tag-off'>TIER S</div><div class='tag-off'>TIER A</div><div class='tag-on' style='background:#ff3b30;'>DESCARTE</div>"
        h_ev += "</div>"
        net_color = "#16a34a" if net_ev > 0 else "#dc2626"
        breakdown_ev = f"<div class='kpi-breakdown'>• Fuerza Sistemas (Neto): <b style='color:{net_color};'>{net_ev:+.2f}</b><br>• Bonus Calidad: <b style='color:#16a34a;'>+{ev_plus:.2f}</b><br>• Desglose: <span style='color:#16a34a;'>+{ev_compra:.2f} (C)</span> / <span style='color:#dc2626;'>-{ev_venta:.2f} (V)</span></div>"
        st.markdown(f"<div class='apple-kpi-card'><div class='apple-kpi-title'>SCORE EV (Esperanza)</div><div class='apple-kpi-value'>{ev_tot:.2f}</div>{breakdown_ev}{h_ev}</div>", unsafe_allow_html=True)

    with c2:
        h_idt = "<div class='rank-box'>"
        if idt >= 100: h_idt += "<div class='tag-on' style='background:#1d1d1f;'>OBLIGATORIA</div><div class='tag-off'>TACTICA</div><div class='tag-off'>BLOQUEADA</div>"
        elif idt >= 85: h_idt += "<div class='tag-off'>OBLIGATORIA</div><div class='tag-on' style='background:#ff9500;'>TACTICA</div><div class='tag-off'>BLOQUEADA</div>"
        else: h_idt += "<div class='tag-off'>OBLIGATORIA</div><div class='tag-off'>TACTICA</div><div class='tag-on' style='background:#ff3b30;'>BLOQUEADA</div>"
        h_idt += "</div>"
        breakdown_idt = f"<div class='kpi-breakdown'>• WinRate Principal: <b>+{l_wr[0]}</b><br>• Calidad + Sistemas: <b>+{(bono + p_estr + p_sen)}</b><br>• Penalización por Stop: <b style='color:#dc2626;'>-{penal}</b></div>"
        st.markdown(f"<div class='apple-kpi-card'><div class='apple-kpi-title'>PUNTOS IDT (Estructura)</div><div class='apple-kpi-value'>{idt}</div>{breakdown_idt}{h_idt}</div>", unsafe_allow_html=True)

    with c3:
        h_ite = "<div class='rank-box'>"
        if ite <= 5: h_ite += "<div class='tag-on' style='background:#34c759;'>OPTIMO</div><div class='tag-off'>MANEJABLE</div><div class='tag-off'>PELIGROSO</div>"
        elif ite <= 10: h_ite += "<div class='tag-off'>OPTIMO</div><div class='tag-on' style='background:#ff9500;'>MANEJABLE</div><div class='tag-off'>PELIGROSO</div>"
        else: h_ite += "<div class='tag-off'>OPTIMO</div><div class='tag-off'>MANEJABLE</div><div class='tag-on' style='background:#ff3b30;'>PELIGROSO</div>"
        h_ite += "</div>"
        breakdown_ite = f"<div class='kpi-breakdown'>• Precio Compra: <b>{p_buy:.2f} $</b><br>• Stop Loss: <b>{p_sl:.2f} $</b><br>• Distancia de caída: <b>{distancia_stop:.2f} $</b></div>"
        st.markdown(f"<div class='apple-kpi-card'><div class='apple-kpi-title'>RIESGO ITE (Vacío)</div><div class='apple-kpi-value'>{ite}%</div>{breakdown_ite}{h_ite}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🔮 Oráculo Quant (Calibrado con ADN)")
    
    z_in, acc_in, vol_z_in = 0.0, 0.0, 0.0
    if ticker != "" and not df_global.empty:
        try:
            df_esc = df_global.copy()
            df_esc['MA55'] = df_esc['Close'].rolling(window=55).mean()
            df_esc['STD55'] = df_esc['Close'].rolling(window=55).std()
            df_esc['Z_Score'] = (df_esc['Close'] - df_esc['MA55']) / df_esc['STD55']
            df_esc['ROC_10'] = df_esc['Close'].pct_change(periods=10) * 100
            df_esc['Accel'] = df_esc['ROC_10'].diff(periods=5)
            df_esc['Vol_MA55'] = df_esc['Volume'].rolling(window=55).mean()
            df_esc['Vol_STD55'] = df_esc['Volume'].rolling(window=55).std()
            df_esc['Vol_Z_Score'] = (df_esc['Volume'] - df_esc['Vol_MA55']) / df_esc['Vol_STD55']
            
            today_naive = df_esc.index[-1].replace(tzinfo=None)
            target_dates_naive = []
            for i in range(12): 
                m = today_naive.month - i; y = today_naive.year
                while m <= 0: m += 12; y -= 1
                target_dates_naive.append(datetime.datetime(y, m, 1))
                target_dates_naive.append(datetime.datetime(y, m, 15))
                
            fechas_slider = []
            for td in target_dates_naive:
                if td <= today_naive:
                    deltas = abs(df_esc.index.tz_localize(None) - td)
                    fechas_slider.append(df_esc.index[deltas.argmin()])
                    
            for d in df_esc.index[-15:]: fechas_slider.append(d)
            fechas_slider = sorted(list(set(fechas_slider)))
            meses = {1:"Ene", 2:"Feb", 3:"Mar", 4:"Abr", 5:"May", 6:"Jun", 7:"Jul", 8:"Ago", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dic"}
            opciones_str = []
            dict_fechas = {}
            for d in fechas_slider:
                d_naive = d.replace(tzinfo=None)
                if d == df_esc.index[-1]: s = "🟢 HOY"
                else: s = f"{d_naive.day} {meses[d_naive.month]} {d_naive.year}"
                opciones_str.append(s)
                dict_fechas[s] = d

            fecha_sel_str = st.select_slider("⏳ **Máquina del Tiempo:** Desliza para ver qué marcaba el radar ese día exacto.", options=opciones_str, value="🟢 HOY")
            fecha_sel = dict_fechas[fecha_sel_str]
            if fecha_sel_str != "🟢 HOY": st.warning(f"⚠️ **MODO VIAJE EN EL TIEMPO:** Estás viendo la pantalla de A.I.T.O.R. exactamente como cerró el **{fecha_sel_str}**.")

            df_corte = df_esc[df_esc.index <= fecha_sel].copy()
            
            z_in = df_corte['Z_Score'].iloc[-1] if not pd.isna(df_corte['Z_Score'].iloc[-1]) else 0
            acc_in = df_corte['Accel'].iloc[-1] if not pd.isna(df_corte['Accel'].iloc[-1]) else 0
            vol_z_in = df_corte['Vol_Z_Score'].iloc[-1] if not pd.isna(df_corte['Vol_Z_Score'].iloc[-1]) else 0

            df_last_15 = df_corte.tail(15).copy()
            bar_x = [f"{d.day} {meses[d.month]}" for d in df_last_15.index.tz_localize(None)]

            col_eq1, col_eq2, col_eq3 = st.columns(3)
            
            with col_eq1:
                z_c1 = "font-weight:900; color:#3b82f6;" if z_in < -2.0 else "color:#a1a1aa;"
                z_c2 = "font-weight:900; color:#16a34a;" if -2.0 <= z_in <= opt_z else "color:#a1a1aa;"
                z_c3 = "font-weight:900; color:#ff3b30;" if z_in > opt_z else "color:#a1a1aa;"
                if opt_z != -99:
                    st.markdown(f"""<div class="quant-card" style="padding-bottom:5px;">
                        <div class="quant-title">Tensión Precio (ADN > {opt_z}σ)</div>
                        <div style='font-size:0.8rem; background:#f8f9fa; padding:8px; border-radius:8px; margin-bottom:10px; border:1px solid #e8eaed;'>
                            <div style='{z_c1}'>• < -2.0 : Sobrevendida</div><div style='{z_c2}'>• -2.0 a {opt_z} : Normal</div><div style='{z_c3}'>• > {opt_z} : Disparador Activo</div>
                        </div>""", unsafe_allow_html=True)
                    fig_ze = go.Figure(go.Indicator(mode="gauge+number", value=z_in, gauge=dict(axis=dict(range=[-4, 4]), bar=dict(color="black"), steps=[dict(range=[-4, -2.0], color="#3b82f6"), dict(range=[-2.0, opt_z], color="#e5e5ea"), dict(range=[opt_z, 4], color="#ff3b30")])))
                    bar_c_z = ['#ff3b30' if val > opt_z else ('#3b82f6' if val < -2.0 else '#a1a1aa') for val in df_last_15['Z_Score']]
                    line_z = opt_z
                else:
                    st.markdown("""<div class="quant-card" style="padding-bottom:5px;"><div class="quant-title">Tensión Precio (Apagado)</div>""", unsafe_allow_html=True)
                    fig_ze = go.Figure(go.Indicator(mode="gauge+number", value=z_in, gauge=dict(axis=dict(range=[-4, 4]), bar=dict(color="gray"))))
                    bar_c_z = ['gray'] * 15; line_z = 2.0
                fig_ze.update_layout(height=140, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_ze, use_container_width=True)
                fig_b_z = go.Figure(data=[go.Bar(x=bar_x, y=df_last_15['Z_Score'], marker_color=bar_c_z)])
                fig_b_z.add_hline(y=line_z, line_dash="dash", line_color="#ff3b30")
                fig_b_z.update_layout(height=120, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showticklabels=False), yaxis=dict(title=""), plot_bgcolor="white")
                st.plotly_chart(fig_b_z, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_eq2:
                a_c1 = "font-weight:900; color:#ff3b30;" if acc_in <= opt_acc else "color:#a1a1aa;"
                a_c2 = "font-weight:900; color:#16a34a;" if acc_in > opt_acc else "color:#a1a1aa;"
                if opt_acc != -99:
                    st.markdown(f"""<div class="quant-card" style="padding-bottom:5px;">
                        <div class="quant-title">Momentum (ADN > {opt_acc})</div>
                        <div style='font-size:0.8rem; background:#f8f9fa; padding:8px; border-radius:8px; margin-bottom:10px; border:1px solid #e8eaed;'>
                            <div style='{a_c1}'>• ≤ {opt_acc} : Sin Gatillo</div><div style='{a_c2}'>• > {opt_acc} : Aceleración Activa</div><div style='color:transparent;'>_</div>
                        </div>""", unsafe_allow_html=True)
                    fig_ae = go.Figure(go.Indicator(mode="gauge+number", value=acc_in, gauge=dict(axis=dict(range=[-10, 10]), bar=dict(color="purple"), steps=[dict(range=[-10, opt_acc], color="#ffcdd2"), dict(range=[opt_acc, 10], color="#c8e6c9")])))
                    bar_c_a = ['#34c759' if val > opt_acc else '#ff3b30' for val in df_last_15['Accel']]
                    line_acc = opt_acc
                else:
                    st.markdown("""<div class="quant-card" style="padding-bottom:5px;"><div class="quant-title">Momentum (Apagado)</div>""", unsafe_allow_html=True)
                    fig_ae = go.Figure(go.Indicator(mode="gauge+number", value=acc_in, gauge=dict(axis=dict(range=[-10, 10]), bar=dict(color="gray"))))
                    bar_c_a = ['gray'] * 15; line_acc = 0
                fig_ae.update_layout(height=140, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_ae, use_container_width=True)
                fig_b_a = go.Figure(data=[go.Bar(x=bar_x, y=df_last_15['Accel'], marker_color=bar_c_a)])
                fig_b_a.add_hline(y=line_acc, line_dash="solid", line_color="#1d1d1f")
                fig_b_a.update_layout(height=120, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showticklabels=False), yaxis=dict(title=""), plot_bgcolor="white")
                st.plotly_chart(fig_b_a, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_eq3:
                v_c1 = "font-weight:900; color:#ff3b30;" if vol_z_in < 0 else "color:#a1a1aa;"
                v_c2 = "font-weight:900; color:#3b82f6;" if 0 <= vol_z_in <= opt_vol else "color:#a1a1aa;"
                v_c3 = "font-weight:900; color:#34c759;" if vol_z_in > opt_vol else "color:#a1a1aa;"
                if opt_vol != -99:
                    st.markdown(f"""<div class="quant-card" style="padding-bottom:5px;">
                        <div class="quant-title">Volumen (ADN > {opt_vol}σ)</div>
                        <div style='font-size:0.8rem; background:#f8f9fa; padding:8px; border-radius:8px; margin-bottom:10px; border:1px solid #e8eaed;'>
                            <div style='{v_c1}'>• < 0 : Ruido Minorista</div><div style='{v_c2}'>• 0 a {opt_vol} : Volumen Sano</div><div style='{v_c3}'>• > {opt_vol} : Gatillo Institucional</div>
                        </div>""", unsafe_allow_html=True)
                    fig_ve = go.Figure(go.Indicator(mode="gauge+number", value=vol_z_in, gauge=dict(axis=dict(range=[-2, 4]), bar=dict(color="black"), steps=[dict(range=[-2, opt_vol], color="#e5e5ea"), dict(range=[opt_vol, 4], color="#34c759")])))
                    bar_c_v = ['#34c759' if val >= opt_vol else '#e5e5ea' for val in df_last_15['Vol_Z_Score']]
                    line_vol = opt_vol
                else:
                    st.markdown("""<div class="quant-card" style="padding-bottom:5px;"><div class="quant-title">Volumen (Apagado)</div>""", unsafe_allow_html=True)
                    fig_ve = go.Figure(go.Indicator(mode="gauge+number", value=vol_z_in, gauge=dict(axis=dict(range=[-2, 4]), bar=dict(color="gray"))))
                    bar_c_v = ['gray'] * 15; line_vol = 1.5
                fig_ve.update_layout(height=140, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_ve, use_container_width=True)
                fig_b_v = go.Figure(data=[go.Bar(x=bar_x, y=df_last_15['Vol_Z_Score'], marker_color=bar_c_v)])
                fig_b_v.add_hline(y=line_vol, line_dash="dash", line_color="#34c759")
                fig_b_v.update_layout(height=120, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showticklabels=False), yaxis=dict(title=""), plot_bgcolor="white")
                st.plotly_chart(fig_b_v, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
        except: pass

    st.markdown("---")
    st.subheader("📋 Auditoría Clínica de Entrada (ADN Integrado)")
    
    if ev_tot >= 10: txt_ev_out, col_ev_out = f"<b>{ev_tot:.2f} Puntos</b>. Sistema estadísticamente muy robusto.", "tdah-green"
    elif ev_tot >= 5: txt_ev_out, col_ev_out = f"<b>{ev_tot:.2f} Puntos</b>. Fiabilidad estándar. Sistema apto.", "tdah-blue"
    else: txt_ev_out, col_ev_out = f"<b>{ev_tot:.2f} Puntos</b>. Fiabilidad matemática DÉBIL. Usa confirmación.", "tdah-red"
    st.markdown(f"<div class='tdah-box {col_ev_out}'><div class='tdah-title'>📊 Esperanza Matemática:</div><div class='tdah-text'>{txt_ev_out}</div></div>", unsafe_allow_html=True)

    if net_ev >= 1.5: col_f_out = "tdah-green"
    elif net_ev >= 0: col_f_out = "tdah-yellow"
    else: col_f_out = "tdah-red"
    st.markdown(f"<div class='tdah-box {col_f_out}'><div class='tdah-title'>⚖️ Fuerza Estructural Neta:</div><div class='tdah-text'>Empuje real descontando sistemas en contra: <b>{net_ev:+.2f}</b>.</div></div>", unsafe_allow_html=True)

    if opt_z != -99:
        if z_in > 2.5: txt_z_out, col_z_out = f"PELIGRO. Precio disparado por euforia (> 2.5σ).", "tdah-red"
        elif z_in >= opt_z: txt_z_out, col_z_out = f"GATILLO ACTIVO. Supera el límite de {opt_z}σ de tu ADN.", "tdah-green"
        else: txt_z_out, col_z_out = f"Tensión insuficiente ({z_in:.2f}σ). No cumple tu ADN ({opt_z}σ).", "tdah-yellow"
    else: txt_z_out, col_z_out = "Módulo Z-Score apagado en el ADN.", "tdah-blue"
    st.markdown(f"<div class='tdah-box {col_z_out}'><div class='tdah-title'>🪢 Tensión Precio (Z-Score):</div><div class='tdah-text'>{txt_z_out}</div></div>", unsafe_allow_html=True)

    if opt_acc != -99:
        if acc_in >= opt_acc: txt_a_out, col_a_out = f"GATILLO ACTIVO. Aceleración positiva ({acc_in:.2f}), supera tu ADN ({opt_acc}).", "tdah-green"
        else: txt_a_out, col_a_out = f"Pérdida de gas ({acc_in:.2f}). No cumple el requisito de tu ADN ({opt_acc}).", "tdah-yellow"
    else: txt_a_out, col_a_out = "Módulo de Aceleración apagado en el ADN.", "tdah-blue"
    st.markdown(f"<div class='tdah-box {col_a_out}'><div class='tdah-title'>🏎️ Aceleración (Momentum):</div><div class='tdah-text'>{txt_a_out}</div></div>", unsafe_allow_html=True)

    if opt_vol != -99:
        if vol_z_in >= opt_vol: txt_v_out, col_v_out = f"GATILLO ACTIVO. Volumen institucional ({vol_z_in:.2f}σ), por encima de tu ADN ({opt_vol}σ).", "tdah-green"
        else: txt_v_out, col_v_out = f"Volumen sano o insuficiente ({vol_z_in:.2f}σ). No salta la alarma ADN ({opt_vol}σ).", "tdah-yellow"
    else: txt_v_out, col_v_out = "Módulo de Volumen apagado en el ADN.", "tdah-blue"
    st.markdown(f"<div class='tdah-box {col_v_out}'><div class='tdah-title'>🐘 Intervención Institucional (Volumen):</div><div class='tdah-text'>{txt_v_out}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if net_ev < 0: ver_txt, ver_col = "❌ PROHIBIDO COMPRAR. Es una trampa bajista (Fuerza Neta negativa).", "tdah-red"
    elif z_in > 2.5: ver_txt, ver_col = "❌ ESPERAR. La tendencia es buena pero la goma está demasiado tensa.", "tdah-red"
    else:
        cumple_z = True if opt_z == -99 else (z_in >= opt_z)
        cumple_acc = True if opt_acc == -99 else (acc_in >= opt_acc)
        cumple_vol = True if opt_vol == -99 else (vol_z_in >= opt_vol)
        if net_ev >= 1.5 and cumple_z and cumple_acc and cumple_vol: ver_txt, ver_col = "✅ LUZ VERDE TOTAL (ADN PERFECTO). Tu sistema clásico y los parámetros Quant están alineados. (TIER S).", "tdah-green"
        elif cumple_z and cumple_acc and cumple_vol: ver_txt, ver_col = "⚠️ PRECAUCIÓN. El ADN Quant da señal verde, pero tu sistema clásico (Fuerza Neta) duda. Reduce tu capital a la mitad.", "tdah-yellow"
        else: ver_txt, ver_col = "⚠️ OPERACIÓN ESTÁNDAR. Tu sistema clásico da señal, pero el ADN Quant no apoya. Opera normal (TIER A).", "tdah-blue"
            
    st.markdown(f"<div class='tdah-box {ver_col}' style='border-width: 4px;'><div class='tdah-title'>🎯 VEREDICTO FINAL DE LA MÁQUINA:</div><div class='tdah-text' style='font-size:1.1rem; font-weight:600;'>{ver_txt}</div></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("⚙️ Panel de Ejecución Cuantitativa")
    col_btn_save, col_btn_buy = st.columns(2)
    with col_btn_save:
        if st.button("💾 Solo Guardar Escaneo (Añadir a Radar)", use_container_width=True):
            with st.spinner("📡 Guardando..."):
                try:
                    v_t = "REVISION REQUERIDA"
                    if idt >= 100: v_t = "COMPRA OBLIGATORIA"
                    elif idt >= 85: v_t = "COMPRA TACTICA"
                    elif ev_tot < 5: v_t = "OPERACION NO VIABLE"
                    d_sav = {"Ticker": ticker, "Tier": v_t, "EV_Total": ev_tot, "IDT_Puntos": idt, "ITE_Porc": ite, "Veredicto": v_t, "Acciones": n_tit, "Inversion": inv_t}
                    for j in range(5): d_sav[f"S{j+1}_Dias"] = s_elegidos[j]; d_sav[f"W{j+1}"] = l_wr[j]; d_sav[f"R{j+1}"] = l_rt[j]
                    df_fresh = conn.read(worksheet="Sheet1", ttl=0)
                    if df_fresh.empty: df_fresh = pd.DataFrame(columns=COL_DB)
                    df_upd = pd.concat([df_fresh, pd.DataFrame([d_sav])], ignore_index=True).drop_duplicates("Ticker", keep="last")
                    conn.update(worksheet="Sheet1", data=df_upd)
                    st.cache_data.clear()
                    st.session_state['scan_saved_success'] = True
                    st.rerun()
                except Exception as e: st.error(f"Error al guardar: {e}")

    with col_btn_buy:
        if st.button("🚀 COMPRAR AHORA: Enviar a Cartera en Vivo", use_container_width=True):
            with st.spinner("📡 Ejecutando..."):
                try:
                    v_t = "COMPRADO"
                    d_sav = {"Ticker": ticker, "Tier": v_t, "EV_Total": ev_tot, "IDT_Puntos": idt, "ITE_Porc": ite, "Veredicto": v_t, "Acciones": n_tit, "Inversion": inv_t}
                    for j in range(5): d_sav[f"S{j+1}_Dias"] = s_elegidos[j]; d_sav[f"W{j+1}"] = l_wr[j]; d_sav[f"R{j+1}"] = l_rt[j]
                    df_fresh = conn.read(worksheet="Sheet1", ttl=0)
                    if df_fresh.empty: df_fresh = pd.DataFrame(columns=COL_DB)
                    df_upd = pd.concat([df_fresh, pd.DataFrame([d_sav])], ignore_index=True).drop_duplicates("Ticker", keep="last")
                    conn.update(worksheet="Sheet1", data=df_upd)
                    df_c = conn.read(worksheet="Cartera", ttl=0)
                    n_pos = {"Ticker": ticker, "Fecha_Entrada": datetime.date.today().strftime("%Y-%m-%d"), "Precio_Entrada": p_buy, "Num_Acciones": n_tit, "Stop_Actual": p_sl, "Fecha_Ruptura_S4": datetime.date.today().strftime("%Y-%m-%d"), "Precio_Ruptura_S4": p_buy, "Fecha_Ruptura_S5": datetime.date.today().strftime("%Y-%m-%d"), "Precio_Ruptura_S5": p_buy}
                    conn.update(worksheet="Cartera", data=pd.concat([df_c, pd.DataFrame([n_pos])], ignore_index=True))
                    st.cache_data.clear()
                    st.session_state['scan_saved_success'] = True
                    st.rerun()
                except Exception as e: st.error(f"Error al enviar a cartera: {e}")

# ---------------------------------------------------------------------
# PESTAÑA 2: AUDITORÍA GLOBAL
# ---------------------------------------------------------------------
with tab2: 
    st.markdown("### 🗂️ Centro de Mando (Auditoría Global)")
    if not df_datos.empty:
        df_display = df_datos[['Ticker', 'Veredicto', 'EV_Total', 'IDT_Puntos', 'ITE_Porc']].copy()
        df_display['EV_Total'] = pd.to_numeric(df_display['EV_Total'], errors='coerce').fillna(0)
        df_display['IDT_Puntos'] = pd.to_numeric(df_display['IDT_Puntos'], errors='coerce').fillna(0)
        df_display['ITE_Porc'] = pd.to_numeric(df_display['ITE_Porc'], errors='coerce').fillna(0)
        df_display['Score_Global'] = (df_display['IDT_Puntos'] / 140) * 100
        df_display['Score_Global'] = df_display['Score_Global'].clip(upper=100, lower=0)
        df_display = df_display[['Ticker', 'Veredicto', 'Score_Global', 'EV_Total', 'IDT_Puntos', 'ITE_Porc']]
        st.dataframe(df_display.sort_values("Score_Global", ascending=False), hide_index=True, use_container_width=True)

# ---------------------------------------------------------------------
# PESTAÑA 3: CARTERA EN VIVO
# ---------------------------------------------------------------------
with tab3:
    st.markdown("### Gestión Quántica de Operaciones")
    tab_vivas, tab_add, tab_historial = st.tabs(["🟢 Posiciones Vivas", "➕ Añadir a Cartera", "📚 Historial"])
    with tab_vivas:
        try:
            df_cartera = conn.read(worksheet="Cartera", ttl=0).dropna(how="all")
            if df_cartera.empty: st.warning("Tu cartera está vacía.")
            else:
                ticker_sel = st.selectbox("Selecciona Posición Abierta:", df_cartera['Ticker'].tolist())
                datos_ticker = df_cartera[df_cartera['Ticker'] == ticker_sel].iloc[0]
                fecha_in = pd.to_datetime(datos_ticker['Fecha_Entrada']).date()
                precio_in = float(datos_ticker['Precio_Entrada'])
                acciones = float(datos_ticker['Num_Acciones'])
                stop_actual = float(datos_ticker['Stop_Actual'])
                
                with st.spinner(f"Analizando data científica de {ticker_sel}..."):
                    stock_cartera = yf.Ticker(ticker_sel)
                    df_q = stock_cartera.history(start=fecha_in - datetime.timedelta(days=365), end=datetime.date.today() + datetime.timedelta(days=1))
                    if df_q.empty: df_q = stock_cartera.history(period="2y")
                    precio_vivo = df_q['Close'].iloc[-1]
                    beneficio_eur = (precio_vivo - precio_in) * acciones
                    beneficio_pct = ((precio_vivo - precio_in) / precio_in) * 100
                    dias_pos = max((datetime.date.today() - fecha_in).days, 1)
                    
                color_borde = '#34c759' if beneficio_pct >= 0 else '#ff3b30'
                html_kpis = f'<div class="apple-kpi-container"><div class="apple-kpi-card" style="border-left: 5px solid {color_borde};"><div class="apple-kpi-title" style="margin:0;">Rentabilidad Real</div><div class="apple-kpi-value">{beneficio_pct:+.2f}%</div><div class="apple-kpi-sub {"sub-green" if beneficio_pct>=0 else "sub-red"}">{beneficio_eur:+.2f} Netos</div></div><div class="apple-kpi-card"><div class="apple-kpi-title">Precio Mercado ({ticker_sel})</div><div class="apple-kpi-value">{precio_vivo:.2f}</div><div class="apple-kpi-sub sub-gray">Entrada: {precio_in:.2f}</div></div><div class="apple-kpi-card"><div class="apple-kpi-title">Días en Tendencia</div><div class="apple-kpi-value">{dias_pos}</div></div></div>'
                st.markdown(html_kpis, unsafe_allow_html=True)
                
                col_term, col_vacia = st.columns([2, 1])
                with col_term:
                    rango_min = stop_actual * 0.90 
                    rango_max = max(precio_vivo * 1.05, stop_actual * 1.10) 
                    fig_riesgo = go.Figure(go.Indicator(mode="gauge+number", value=precio_vivo, title=dict(text=f"Radar: Precio Actual vs Stop ({stop_actual:.2f})"), gauge=dict(axis=dict(range=[rango_min, rango_max]), bar=dict(color="#1d1d1f"), steps=[dict(range=[rango_min, stop_actual], color="#ff3b30"), dict(range=[stop_actual, stop_actual*1.03], color="#ffcc00"), dict(range=[stop_actual*1.03, rango_max], color="#34c759")], threshold=dict(line=dict(color="black", width=5), value=stop_actual))))
                    fig_riesgo.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig_riesgo, use_container_width=True)
                
                with st.form("form_update_stop"):
                    c_u1, c_u2 = st.columns([1, 2])
                    with c_u1: nuevo_stop = st.number_input("Fijar Nuevo Stop Loss", value=float(stop_actual))
                    with c_u2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.form_submit_button("Actualizar Stop en Base de Datos"):
                            df_c_update = conn.read(worksheet="Cartera", ttl=0)
                            idx = df_c_update[df_c_update['Ticker'] == ticker_sel].index
                            if not idx.empty:
                                df_c_update.loc[idx[-1], 'Stop_Actual'] = nuevo_stop
                                conn.update(worksheet="Cartera", data=df_c_update)
                                st.cache_data.clear(); st.toast(f"✅ Stop actualizado a {nuevo_stop:.2f}.", icon="💾")
        except: pass
    with tab_add: st.info("Registro manual en código.")
    with tab_historial: st.info("Historial en código.")

# ---------------------------------------------------------------------
# PESTAÑA 4: LABORATORIO MODULAR Y OPTIMIZADOR
# ---------------------------------------------------------------------
with tab4:
    st.title("🧪 Laboratorio Quant y Optimizador Genético")
    st.markdown(f"Experimenta con **{ticker}**. Usa tus propias reglas o deja que la máquina pruebe combinaciones por fuerza bruta.")
    
    horizontes_fibo = [1, 3, 5, 8, 13, 21, 34, 55, 89]
    str_cols_fibo = [f"Ret_{h}D" for h in horizontes_fibo]
    
    st.markdown("### 🎛️ 1. Panel Quant Manual")
    col_p1, col_p2, col_p3 = st.columns(3)
    val_z = True if opt_z != -99 else False
    val_acc = True if opt_acc != -99 else False
    val_vol = True if opt_vol != -99 else False
    
    with col_p1:
        st.markdown("<div style='background:#f8f9fa; padding:15px; border-radius:10px; border:1px solid #e8eaed;'>", unsafe_allow_html=True)
        use_z = st.checkbox("🟢 Usar Tensión Precio (Z-Score)", value=val_z)
        bt_z_precio = st.number_input("Z-Score Mínimo (>)", value=float(opt_z) if opt_z != -99 else 1.0, step=0.1, disabled=not use_z)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_p2:
        st.markdown("<div style='background:#f8f9fa; padding:15px; border-radius:10px; border:1px solid #e8eaed;'>", unsafe_allow_html=True)
        use_acc = st.checkbox("🟢 Usar Aceleración (Momentum)", value=val_acc)
        bt_accel = st.number_input("Aceleración Mínima (>)", value=float(opt_acc) if opt_acc != -99 else 0.0, step=0.5, disabled=not use_acc)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_p3:
        st.markdown("<div style='background:#f8f9fa; padding:15px; border-radius:10px; border:1px solid #e8eaed;'>", unsafe_allow_html=True)
        use_vol = st.checkbox("🟢 Usar Huella Volumen", value=val_vol)
        bt_z_vol = st.number_input("Huella Volumen Mínima (>)", value=float(opt_vol) if opt_vol != -99 else 1.5, step=0.1, disabled=not use_vol)
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("### 📈 2. Filtro de Tendencia (Medias Móviles)")
    lista_mas = [2, 3, 5, 8, 13, 21, 34, 55]
    mas_seleccionadas = st.multiselect("El precio de cierre debe estar POR ENCIMA de estas medias:", lista_mas, default=[])
    
    st.markdown("### 🎯 3. Confirmación del Precio (Price Action)")
    tipo_filtro = st.radio("¿Qué debe hacer la vela para activar tu compra?", [
        "Ninguno (Entrar el mismo día).",
        "Fuerza Inmediata: Superar el máximo del día anterior.",
        "Continuación (Minervini): Entrar el día SIGUIENTE si supera el máximo."
    ], index=2)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_run_man, col_run_auto = st.columns(2)
    
    if col_run_man.button(f"⚙️ Ejecutar Simulación Manual en {ticker}", type="primary", use_container_width=True):
        with st.spinner(f"Analizando 5 años de {ticker}..."):
            try:
                stock_bt = yf.Ticker(ticker)
                df_bt = stock_bt.history(period="5y")
                
                if df_bt.empty or len(df_bt) < 100: st.error("No hay suficientes datos.")
                else:
                    df_bt['MA55'] = df_bt['Close'].rolling(window=55).mean()
                    df_bt['Vol_MA55'] = df_bt['Volume'].rolling(window=55).mean()
                    df_bt['Vol_STD55'] = df_bt['Volume'].rolling(window=55).std()
                    df_bt['Vol_Z_Score'] = (df_bt['Volume'] - df_bt['Vol_MA55']) / df_bt['Vol_STD55']
                    df_bt['Z_Score'] = (df_bt['Close'] - df_bt['MA55']) / df_bt['Close'].rolling(window=55).std()
                    df_bt['ROC_10'] = df_bt['Close'].pct_change(periods=10) * 100
                    df_bt['Accel'] = df_bt['ROC_10'].diff(periods=5)
                    
                    for ma in lista_mas: df_bt[f'MA_{ma}'] = df_bt['Close'].rolling(window=ma).mean()
                    
                    cond_z = (df_bt['Z_Score'] > bt_z_precio) if use_z else pd.Series(True, index=df_bt.index)
                    cond_acc = (df_bt['Accel'] > bt_accel) if use_acc else pd.Series(True, index=df_bt.index)
                    cond_vol = (df_bt['Vol_Z_Score'] > bt_z_vol) if use_vol else pd.Series(True, index=df_bt.index)
                    cond_mas = pd.Series(True, index=df_bt.index)
                    for ma in mas_seleccionadas: cond_mas = cond_mas & (df_bt['Close'] > df_bt[f'MA_{ma}'])
                        
                    df_bt['Candidato'] = cond_z & cond_acc & cond_vol & cond_mas
                    
                    fechas_registro_display = []
                    datos_estadistica = {h: [] for h in horizontes_fibo}
                    ultimo_dia_señal = None
                    
                    for i in range(55, len(df_bt) - max(horizontes_fibo) - 1):
                        row = df_bt.iloc[i]
                        date = df_bt.index[i]
                        if row['Candidato']:
                            if ultimo_dia_señal is not None and (date - ultimo_dia_señal).days <= 10: continue 
                            es_valida = False; idx_entrada = i; p_entrada = row['Close']
                            gatillo_name = tipo_filtro.split(" (")[0].split(":")[0] 
                            
                            if "Ninguno" in tipo_filtro: es_valida = True
                            elif "Fuerza Inmediata" in tipo_filtro:
                                if row['High'] > df_bt.iloc[i-1]['High']: es_valida = True
                            elif "Continuación" in tipo_filtro:
                                row_next = df_bt.iloc[i+1]
                                if row_next['High'] > row['High']: es_valida = True; idx_entrada = i + 1; p_entrada = row_next['Close']

                            if es_valida:
                                fila_diario = {"Señal Original": date.strftime("%Y-%m-%d"), "Precio": f"{p_entrada:.2f} $", "Vol (σ)": f"{row['Vol_Z_Score']:.1f}" if not pd.isna(row['Vol_Z_Score']) else "-"}
                                for h in horizontes_fibo:
                                    p_salida = df_bt['Close'].iloc[idx_entrada + h]
                                    ret = ((p_salida - p_entrada) / p_entrada) * 100
                                    datos_estadistica[h].append(ret)
                                    fila_diario[f"{h}D"] = f"{ret:+.2f}%"
                                fechas_registro_display.append(fila_diario)
                                ultimo_dia_señal = date 

                    total_señales = len(fechas_registro_display)
                    if total_señales > 0:
                        positivas = len([s for s in datos_estadistica[21] if s > 0])
                        win_rate = (positivas / total_señales) * 100
                        nuevo_test = {
                            "Ticker": ticker, "Z-Score": f"> {bt_z_precio}" if use_z else "OFF", "Accel": f"> {bt_accel}" if use_acc else "OFF", "Volumen": f"> {bt_z_vol}" if use_vol else "OFF",
                            "Medias": str(mas_seleccionadas) if mas_seleccionadas else "OFF", "Precio": gatillo_name, "Trades": total_señales, "WinRate": round(win_rate, 1)
                        }
                        for h in horizontes_fibo: nuevo_test[f"Ret_{h}D"] = round(np.mean(datos_estadistica[h]), 2)
                        st.session_state['historial_lab'].append(nuevo_test)
                        st.success("✅ Test manual completado y añadido a la tabla.")
                    else: st.warning("Tus reglas son demasiado estrictas. 0 señales.")
            except Exception as e: st.error(f"Error procesando los datos: {e}")

    if col_run_auto.button(f"🤖 Auto-Descubrir ADN Óptimo (Fuerza Bruta)", type="secondary", use_container_width=True):
        with st.spinner("Creando clones... Probando 27 combinaciones institucionales a la vez..."):
            try:
                stock_bt = yf.Ticker(ticker)
                df_bt = stock_bt.history(period="5y")
                
                if df_bt.empty or len(df_bt) < 100: st.error("No hay suficientes datos.")
                else:
                    df_bt['MA55'] = df_bt['Close'].rolling(window=55).mean()
                    df_bt['Vol_MA55'] = df_bt['Volume'].rolling(window=55).mean()
                    df_bt['Vol_STD55'] = df_bt['Volume'].rolling(window=55).std()
                    df_bt['Vol_Z_Score'] = (df_bt['Volume'] - df_bt['Vol_MA55']) / df_bt['Vol_STD55']
                    df_bt['Z_Score'] = (df_bt['Close'] - df_bt['MA55']) / df_bt['Close'].rolling(window=55).std()
                    df_bt['ROC_10'] = df_bt['Close'].pct_change(periods=10) * 100
                    df_bt['Accel'] = df_bt['ROC_10'].diff(periods=5)
                    
                    z_ranges = [0.5, 1.0, 1.5]
                    a_ranges = [-0.5, 0.0, 0.5]
                    v_ranges = [1.0, 1.5, 2.0]
                    gatillo_name = "Continuación"
                    
                    for test_z in z_ranges:
                        for test_a in a_ranges:
                            for test_v in v_ranges:
                                cond_z = df_bt['Z_Score'] > test_z
                                cond_acc = df_bt['Accel'] > test_a
                                cond_vol = df_bt['Vol_Z_Score'] > test_v
                                df_bt['Candidato'] = cond_z & cond_acc & cond_vol
                                
                                datos_estadistica = {h: [] for h in horizontes_fibo}
                                ultimo_dia_señal = None
                                total_señales = 0
                                
                                for i in range(55, len(df_bt) - max(horizontes_fibo) - 1):
                                    row = df_bt.iloc[i]
                                    date = df_bt.index[i]
                                    if row['Candidato']:
                                        if ultimo_dia_señal is not None and (date - ultimo_dia_señal).days <= 10: continue 
                                        row_next = df_bt.iloc[i+1]
                                        if row_next['High'] > row['High']:
                                            idx_entrada = i + 1; p_entrada = row_next['Close']
                                            for h in horizontes_fibo:
                                                p_salida = df_bt['Close'].iloc[idx_entrada + h]
                                                datos_estadistica[h].append(((p_salida - p_entrada) / p_entrada) * 100)
                                            total_señales += 1
                                            ultimo_dia_señal = date 
                                
                                if total_señales > 0:
                                    positivas = len([s for s in datos_estadistica[21] if s > 0])
                                    win_rate = (positivas / total_señales) * 100
                                    nuevo_test = {
                                        "Ticker": ticker, "Z-Score": f"> {test_z}", "Accel": f"> {test_a}", "Volumen": f"> {test_v}",
                                        "Medias": "OFF", "Precio": gatillo_name, "Trades": total_señales, "WinRate": round(win_rate, 1)
                                    }
                                    for h in horizontes_fibo: nuevo_test[f"Ret_{h}D"] = round(np.mean(datos_estadistica[h]), 2)
                                    st.session_state['historial_lab'].append(nuevo_test)
                                    
            except Exception as e: st.error(f"Error en Auto-Optimizer: {e}")

    # LA COMPETICIÓN Y GUARDADO
    if len(st.session_state['historial_lab']) > 0:
        df_hist = pd.DataFrame(st.session_state['historial_lab'])
        df_ticker_hist = df_hist[df_hist['Ticker'] == ticker].copy()
        
        if not df_ticker_hist.empty:
            st.markdown("---")
            st.markdown("## ⚔️ El Coliseo Quant (Resultados)")
            
            st.markdown("<div style='background:#f0fdf4; padding:15px; border-radius:10px; border:1px solid #22c55e; margin-bottom:20px;'>", unsafe_allow_html=True)
            objetivo_opt = st.selectbox("🏆 ¿A cuántos días vista quieres encontrar al Campeón?", [f"{h} Días" for h in horizontes_fibo], index=5)
            st.markdown("</div>", unsafe_allow_html=True)
            
            col_orden = f"Ret_{objetivo_opt.split(' ')[0]}D"
            df_ticker_hist = df_ticker_hist.sort_values(by=col_orden, ascending=False)
            campeon = df_ticker_hist.iloc[0]
            
            st.markdown(f"""
            <div class='champion-card'>
                <div class='champion-title'>👑 LA COMBINACIÓN GANADORA PARA MAXIMIZAR A {objetivo_opt.upper()}</div>
                <div class='champion-stats'>
                    <div class='stat-box'>📈 Win Rate: {campeon['WinRate']}%</div>
                    <div class='stat-box' style='background:#fef3c7; border-color:#d97706;'>💰 Rendimiento {objetivo_opt}: +{campeon[col_orden]}%</div>
                    <div class='stat-box'>🔍 Z-Score: {campeon['Z-Score']}</div>
                    <div class='stat-box'>🏎️ Accel: {campeon['Accel']}</div>
                    <div class='stat-box'>🐘 Volumen: {campeon['Volumen']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # BOTÓN DE GUARDADO DEL ADN CON AUTO-REINICIO (EL BUG CORREGIDO)
            if st.button(f"💾 GUARDAR 'EL CAMPEÓN' COMO ADN OFICIAL DE {ticker}", type="secondary", use_container_width=True):
                with st.spinner("Guardando en la Nube y sincronizando el Escáner..."):
                    try:
                        c_z = float(campeon['Z-Score'].replace("> ", "")) if campeon['Z-Score'] != "OFF" else -99
                        c_acc = float(campeon['Accel'].replace("> ", "")) if campeon['Accel'] != "OFF" else -99
                        c_vol = float(campeon['Volumen'].replace("> ", "")) if campeon['Volumen'] != "OFF" else -99
                        
                        df_adn_actual = conn.read(worksheet="ADN_Quant", ttl=0)
                        if df_adn_actual.empty: df_adn_actual = pd.DataFrame(columns=["Ticker", "Z_Min", "Acc_Min", "Vol_Min", "Horizonte", "Rendimiento"])
                        
                        # Borrar la versión antigua de este ticker para evitar duplicados residuales
                        df_adn_actual = df_adn_actual[df_adn_actual['Ticker'] != ticker]
                        
                        nuevo_adn = {"Ticker": ticker, "Z_Min": c_z, "Acc_Min": c_acc, "Vol_Min": c_vol, "Horizonte": objetivo_opt, "Rendimiento": campeon[col_orden]}
                        df_adn_nuevo = pd.concat([df_adn_actual, pd.DataFrame([nuevo_adn])], ignore_index=True)
                        
                        conn.update(worksheet="ADN_Quant", data=df_adn_nuevo)
                        st.cache_data.clear()
                        
                        # LA MAGIA: Forzar el reinicio instantáneo
                        st.session_state['adn_saved_success'] = True
                        st.rerun()
                    except Exception as e:
                        if "ADN_Quant" in str(e) or "worksheet" in str(e).lower():
                            st.error("🚨 **Falta crear la carpeta en la nube.** Abre tu archivo de Google Sheets, crea una nueva pestaña (en el botón '+' abajo a la izquierda) y llámala exactamente: **`ADN_Quant`**.")
                        else: st.error(f"Error técnico: {e}")

            st.markdown("#### 📋 Historial de Experimentos de esta Sesión:")
            def color_history(val):
                if isinstance(val, (int, float)): return 'color: #16a34a; font-weight: bold' if val > 0 else ('color: #dc2626' if val < 0 else '')
                return ''
            styled_df = df_ticker_hist.style.map(color_history, subset=str_cols_fibo)
            styled_df = styled_df.set_properties(**{'background-color': '#fffbeb'}, subset=[col_orden])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------
# PESTAÑA 5: EL RADAR AUTOMÁTICO DIARIO
# ---------------------------------------------------------------------
with tab5:
    st.title("📡 Radar Institucional (Escáner Automático Diario)")
    st.markdown("Esta herramienta lee todas las acciones que tienen su ADN guardado y escanea el mercado de **HOY** buscando si alguna ha activado sus propios parámetros cuánticos.")
    
    if st.button("🔄 Lanzar Radar Diario de Mercado", type="primary", use_container_width=True):
        if df_adn.empty:
            st.warning("Aún no has guardado el ADN de ninguna acción en el Laboratorio Quant. No hay nada que vigilar.")
        else:
            with st.spinner("Escaneando el mercado en directo... Buscando tu ADN en las gráficas de hoy."):
                tickers_adn = df_adn['Ticker'].unique().tolist()
                alertas_encontradas = []
                
                for t in tickers_adn:
                    try:
                        datos_adn = df_adn[df_adn['Ticker'] == t].iloc[-1]
                        adn_z = float(datos_adn['Z_Min'])
                        adn_acc = float(datos_adn['Acc_Min'])
                        adn_vol = float(datos_adn['Vol_Min'])
                        
                        stock_rad = yf.Ticker(t)
                        df_rad = stock_rad.history(period="3mo")
                        if df_rad.empty: continue
                        
                        df_rad['MA55'] = df_rad['Close'].rolling(window=55).mean()
                        df_rad['STD55'] = df_rad['Close'].rolling(window=55).std()
                        df_rad['Z_Score'] = (df_rad['Close'] - df_rad['MA55']) / df_rad['STD55']
                        df_rad['ROC_10'] = df_rad['Close'].pct_change(periods=10) * 100
                        df_rad['Accel'] = df_rad['ROC_10'].diff(periods=5)
                        df_rad['Vol_MA55'] = df_rad['Volume'].rolling(window=55).mean()
                        df_rad['Vol_STD55'] = df_rad['Volume'].rolling(window=55).std()
                        df_rad['Vol_Z_Score'] = (df_rad['Volume'] - df_rad['Vol_MA55']) / df_rad['Vol_STD55']
                        
                        hoy_z = df_rad['Z_Score'].iloc[-1]
                        hoy_acc = df_rad['Accel'].iloc[-1]
                        hoy_vol = df_rad['Vol_Z_Score'].iloc[-1]
                        
                        cumple_z = True if adn_z == -99 else (hoy_z >= adn_z)
                        cumple_acc = True if adn_acc == -99 else (hoy_acc >= adn_acc)
                        cumple_vol = True if adn_vol == -99 else (hoy_vol >= adn_vol)
                        
                        if cumple_z and cumple_acc and cumple_vol:
                            alertas_encontradas.append({
                                "Ticker": t, "Z-Score Hoy": f"{hoy_z:.2f}σ (Req: {adn_z})", "Accel Hoy": f"{hoy_acc:.2f} (Req: {adn_acc})", "Volumen Hoy": f"{hoy_vol:.2f}σ (Req: {adn_vol})"
                            })
                    except: pass
                
                st.markdown("---")
                if len(alertas_encontradas) > 0:
                    st.markdown(f"### 🚨 ¡ALERTA! {len(alertas_encontradas)} acciones acaban de detonar su ADN Institucional HOY:")
                    for alerta in alertas_encontradas:
                        st.markdown(f"""
                        <div class='radar-alert'>
                            <h2>🚀 {alerta['Ticker']} LISTO PARA COMPRAR</h2>
                            <b>Volumen:</b> {alerta['Volumen Hoy']} | <b>Aceleración:</b> {alerta['Accel Hoy']} | <b>Tensión:</b> {alerta['Z-Score Hoy']}
                            <br><br><i>Vete a la pestaña 'Escáner Cuántico', pon el Ticker {alerta['Ticker']} y ejecuta la operación si tu sistema clásico te lo confirma.</i>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class='radar-wait'>
                        <h2>⏳ Día de Pesca (0 Alertas)</h2>
                        <p>Ninguna de las acciones guardadas en tu ADN cumple las condiciones el día de hoy. El mercado no ofrece ventanas claras institucionales ahora mismo. Mantén el capital a salvo y vuelve a pasar el radar mañana.</p>
                    </div>
                    """, unsafe_allow_html=True)
