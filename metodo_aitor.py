import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_gsheets import GSheetsConnection
import datetime
import plotly.graph_objects as go
import math
import time

# --- CONFIGURACION ---
st.set_page_config(page_title="AITOR 67.0 STRATEGY POOL", layout="wide")

# --- MEMORIA RAM DE SESIÓN ---
if 'historial_lab' not in st.session_state:
    st.session_state['historial_lab'] = []

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
    
    .radar-alert { background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%); color: white; padding: 15px 25px; border-radius: 15px; margin-bottom: 10px; box-shadow: 0 10px 30px rgba(34, 197, 94, 0.2); border: 2px solid #14532d;}
    .radar-alert h2 { color: white !important; margin-top: 0; font-size: 1.5rem; margin-bottom: 5px;}
    .radar-sys-box { background: rgba(255,255,255,0.2); padding: 10px; border-radius: 8px; margin-top: 8px; border: 1px solid rgba(255,255,255,0.4); }
    .radar-wait { background: #f8f9fa; border: 1px dashed #d1d5db; padding: 20px; border-radius: 15px; color: #6b7280; text-align: center; margin-bottom: 15px;}
    
    .dna-badge { display: inline-block; background: linear-gradient(90deg, #9333ea, #ec4899); color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(236, 72, 153, 0.4);}
    .dna-badge-mult { display: inline-block; background: linear-gradient(90deg, #2563eb, #3b82f6); color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);}
    
    [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
    [data-testid="stExpander"] { border: 2px solid #e5e5ea; border-radius: 15px; background-color: white; overflow: hidden;}
    [data-testid="stExpander"] summary p { font-weight: 800; font-size: 1.1rem; color: #1d1d1f; }
</style>
""", unsafe_allow_html=True)

CAPITAL = 277000.0
DIAS = [1, 2, 3, 5, 6, 7, 8, 11, 14, 17, 21, 26, 34, 55]
A_ACTUAL = datetime.datetime.now().year

COL_DB = ["Ticker", "Tier", "EV_Total", "IDT_Puntos", "ITE_Porc", "Veredicto", "Acciones", "Inversion"]
for i in range(1, 6): COL_DB.extend([f"S{i}_Dias", f"W{i}", f"R{i}"])

conn = st.connection("gsheets", type=GSheetsConnection)

try: df_datos = conn.read(worksheet="Sheet1", ttl=0) 
except: df_datos = pd.DataFrame(columns=COL_DB)

# GESTIÓN DE LA BASE DE DATOS ADN (NUEVAS COLUMNAS MULTIDIMENSIONALES)
try: 
    df_adn = conn.read(worksheet="ADN_Quant", ttl=0)
    # Migración silenciosa si es una tabla vieja
    if not df_adn.empty:
        if 'Es_Default' not in df_adn.columns: df_adn['Es_Default'] = True
        if 'ID_ADN' not in df_adn.columns: df_adn['ID_ADN'] = [str(i) for i in range(len(df_adn))]
        if 'WinRate' not in df_adn.columns: df_adn['WinRate'] = 0.0
except: 
    df_adn = pd.DataFrame(columns=["Ticker", "Z_Min", "Acc_Min", "Vol_Min", "Horizonte", "Rendimiento", "WinRate", "Es_Default", "ID_ADN"])

# =====================================================================
# BUSCADOR LATERAL 
# =====================================================================
st.sidebar.header("Buscador de Activos")
opciones_bd = df_datos['Ticker'].dropna().unique().tolist() if not df_datos.empty else []
ticker_manual = st.sidebar.text_input("Nuevo Ticker (Ej: MU):", "").strip().upper()
ticker_lista = st.sidebar.selectbox("O cargar de Auditoría:", [""] + opciones_bd)
ticker = ticker_manual if ticker_manual != "" else ticker_lista
if ticker == "": ticker = "MU"

# --- LECTURA DEL ADN GENÉTICO POR DEFECTO PARA EL ESCÁNER ---
opt_z, opt_acc, opt_vol = 1.0, 0.0, 1.5 
tiene_adn = False
total_adns = 0

if ticker != "" and not df_adn.empty and "Ticker" in df_adn.columns:
    df_adn_ticker = df_adn[df_adn['Ticker'] == ticker]
    total_adns = len(df_adn_ticker)
    if not df_adn_ticker.empty:
        tiene_adn = True
        # Buscar el que es Por Defecto
        df_def = df_adn_ticker[df_adn_ticker['Es_Default'] == True]
        if not df_def.empty: adn_data = df_def.iloc[0]
        else: adn_data = df_adn_ticker.iloc[0] # Fallback
        
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
# CALCULADORA DE RIESGO
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
    
    if st.session_state.get('adn_saved_success', False):
        st.success("✅ ¡ADN Guardado! Se ha añadido a tu Piscina de Sistemas para esta acción.")
        st.session_state['adn_saved_success'] = False
    
    if tiene_adn:
        if total_adns > 1:
            st.markdown(f"<div class='dna-badge-mult'>🧬 {total_adns} SISTEMAS VIGILANDO ESTA ACCIÓN</div>", unsafe_allow_html=True)
            st.caption(f"El Escáner visual está mostrando tu ADN *Por Defecto*. Límites: Vol > {opt_vol if opt_vol!=-99 else 'OFF'}σ | Accel > {opt_acc if opt_acc!=-99 else 'OFF'} | Z > {opt_z if opt_z!=-99 else 'OFF'}σ")
        else:
            st.markdown("<div class='dna-badge'>🧬 ADN CUANTITATIVO CARGADO</div>", unsafe_allow_html=True)
            st.caption(f"Límites adaptados: Vol > {opt_vol if opt_vol!=-99 else 'OFF'}σ | Accel > {opt_acc if opt_acc!=-99 else 'OFF'} | Tensión > {opt_z if opt_z!=-99 else 'OFF'}σ")
    else:
        st.caption("Usando valores estándar por defecto. Usa la pestaña 'Laboratorio Quant' para guardar estrategias.")
    
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
    st.subheader("🔮 Oráculo Quant (Calibrado con el ADN Principal)")
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
            
            # --- BLINDAJE DE ZONAS HORARIAS Y DUPLICADOS ---
            idx_naive = df_esc.index.tz_localize(None) if getattr(df_esc.index, 'tz', None) is not None else df_esc.index
            today_naive = idx_naive[-1]
            
            target_dates_naive = []
            for i in range(12): 
                m = today_naive.month - i; y = today_naive.year
                while m <= 0: m += 12; y -= 1
                target_dates_naive.append(datetime.datetime(y, m, 1))
                target_dates_naive.append(datetime.datetime(y, m, 15))
                
            fechas_slider = []
            for td in target_dates_naive:
                if td <= today_naive:
                    deltas = abs(idx_naive - td)
                    fechas_slider.append(df_esc.index[deltas.argmin()])
                    
            for d in df_esc.index[-15:]: fechas_slider.append(d)
            fechas_slider = sorted(list(set(fechas_slider)))
            meses = {1:"Ene", 2:"Feb", 3:"Mar", 4:"Abr", 5:"May", 6:"Jun", 7:"Jul", 8:"Ago", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dic"}
            
            opciones_str = []
            dict_fechas = {}
            for d in fechas_slider:
                d_naive = d.replace(tzinfo=None) if hasattr(d, 'tzinfo') and d.tzinfo is not None else d
                if d == df_esc.index[-1]: s = "🟢 HOY"
                else: s = f"{d_naive.day} {meses[d_naive.month]} {d_naive.year}"
                opciones_str.append(s)
                dict_fechas[s] = d

            # Eliminar duplicados para que el Slider no explote
            opciones_unicas = []
            dict_fechas_unicas = {}
            for s in opciones_str:
                if s not in opciones_unicas:
                    opciones_unicas.append(s)
                    dict_fechas_unicas[s] = dict_fechas[s]

            fecha_sel_str = st.select_slider("⏳ **Máquina del Tiempo:** Desliza para ver qué marcaba el radar ese día exacto.", options=opciones_unicas, value="🟢 HOY")
            fecha_sel = dict_fechas_unicas[fecha_sel_str]
            if fecha_sel_str != "🟢 HOY": st.warning(f"⚠️ **MODO VIAJE EN EL TIEMPO:** Estás viendo la pantalla de A.I.T.O.R. exactamente como cerró el **{fecha_sel_str}**.")

            df_corte = df_esc[df_esc.index <= fecha_sel].copy()
            z_in = df_corte['Z_Score'].iloc[-1] if not pd.isna(df_corte['Z_Score'].iloc[-1]) else 0
            acc_in = df_corte['Accel'].iloc[-1] if not pd.isna(df_corte['Accel'].iloc[-1]) else 0
            vol_z_in = df_corte['Vol_Z_Score'].iloc[-1] if not pd.isna(df_corte['Vol_Z_Score'].iloc[-1]) else 0

            df_last_15 = df_corte.tail(15).copy()
            idx_15_naive = df_last_15.index.tz_localize(None) if getattr(df_last_15.index, 'tz', None) is not None else df_last_15.index
            bar_x = [f"{d.day} {meses[d.month]}" for d in idx_15_naive]

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
                
        except Exception as e: 
            st.error(f"🚨 Error en el procesamiento del Oráculo: {e}")

    st.markdown("---")
    st.subheader("📋 Auditoría Clínica de Entrada")
    
    # 1. Esperanza Matemática
    if ev_tot >= 10: txt_ev_out, col_ev_out = f"<b>{ev_tot:.2f} Puntos</b>. Sistema estadísticamente muy robusto.", "tdah-green"
    elif ev_tot >= 5: txt_ev_out, col_ev_out = f"<b>{ev_tot:.2f} Puntos</b>. Fiabilidad estándar. Sistema apto.", "tdah-blue"
    else: txt_ev_out, col_ev_out = f"<b>{ev_tot:.2f} Puntos</b>. Fiabilidad matemática DÉBIL.", "tdah-red"
    st.markdown(f"<div class='tdah-box {col_ev_out}'><div class='tdah-title'>📊 Esperanza Matemática:</div><div class='tdah-text'>{txt_ev_out}</div></div>", unsafe_allow_html=True)

    # 2. Fuerza Estructural Neta
    if net_ev >= 1.5: col_f_out = "tdah-green"
    elif net_ev >= 0: col_f_out = "tdah-yellow"
    else: col_f_out = "tdah-red"
    st.markdown(f"<div class='tdah-box {col_f_out}'><div class='tdah-title'>⚖️ Fuerza Estructural Neta:</div><div class='tdah-text'>Empuje real descontando sistemas en contra: <b>{net_ev:+.2f}</b>.</div></div>", unsafe_allow_html=True)

    # Pre-cálculos para los diagnósticos Quant
    cumple_z = True if opt_z == -99 else (z_in >= opt_z)
    cumple_acc = True if opt_acc == -99 else (acc_in >= opt_acc)
    cumple_vol = True if opt_vol == -99 else (vol_z_in >= opt_vol)

    # 3. Diagnóstico Precio
    dz_c = "tdah-green" if cumple_z else "tdah-yellow"
    txt_z = 'GATILLO ACTIVO.' if cumple_z else 'Tensión insuficiente. No cumple tu ADN.'
    st.markdown(f"<div class='tdah-box {dz_c}'><div class='tdah-title'>🪢 Diagnóstico Precio:</div><div class='tdah-text'>{txt_z} Z-Score: {z_in:.2f}σ.</div></div>", unsafe_allow_html=True)

    # 4. Diagnóstico Momentum
    da_c = "tdah-green" if cumple_acc else "tdah-red"
    txt_a = 'VELOCIDAD CRUCERO.' if cumple_acc else 'FRENADA INSTITUCIONAL.'
    st.markdown(f"<div class='tdah-box {da_c}'><div class='tdah-title'>🏎️ Diagnóstico Momentum:</div><div class='tdah-text'>{txt_a} Accel: {acc_in:.2f}.</div></div>", unsafe_allow_html=True)

    # 5. Diagnóstico Volumen
    dv_c = "tdah-green" if cumple_vol else "tdah-yellow"
    txt_v = 'HUELLA DETECTADA.' if cumple_vol else 'Volumen insuficiente para tu setup.'
    st.markdown(f"<div class='tdah-box {dv_c}'><div class='tdah-title'>🐘 Diagnóstico Volumen:</div><div class='tdah-text'>{txt_v} VolZ: {vol_z_in:.2f}σ.</div></div>", unsafe_allow_html=True)

    # 6. Veredicto Final Combinado
    st.markdown("<br>", unsafe_allow_html=True)
    if net_ev < 0: ver_txt, ver_col = "❌ PROHIBIDO COMPRAR. Es una trampa bajista (Fuerza Neta negativa).", "tdah-red"
    elif z_in > 2.5: ver_txt, ver_col = "❌ ESPERAR. La tendencia es buena pero la goma está demasiado tensa.", "tdah-red"
    else:
        if net_ev >= 1.5 and cumple_z and cumple_acc and cumple_vol: ver_txt, ver_col = "✅ LUZ VERDE TOTAL (ADN PERFECTO). Tu sistema clásico y los parámetros Quant están alineados. (TIER S).", "tdah-green"
        elif cumple_z and cumple_acc and cumple_vol: ver_txt, ver_col = "⚠️ PRECAUCIÓN. El ADN Quant da señal verde, pero tu sistema clásico (Fuerza Neta) duda. Reduce capital.", "tdah-yellow"
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
                    st.cache_data.clear(); st.session_state['scan_saved_success'] = True; st.rerun()
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
                    st.cache_data.clear(); st.session_state['scan_saved_success'] = True; st.rerun()
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

# =====================================================================
# PESTAÑA 3: CENTRO DE MANDO (CARTERA EN VIVO Y FECHAS DE AUDITORÍA)
# =====================================================================
with tab3:
    st.title("💼 Centro de Mando: Posiciones Vivas")
    st.markdown("Auditoría en tiempo real. La IA pondera los votos y calcula los niveles exactos de salida.")

    st.markdown("### 📝 Datos de la Posición en Cartera")
    col_v1, col_v2, col_v3, col_v4 = st.columns(4)
    ticker_vivo = col_v1.text_input("Ticker Activo (Ej. MU):", "MU").upper()
    precio_compra = col_v2.number_input("Precio de Compra ($):", value=100.0, step=1.0)
    fecha_compra = col_v3.date_input("Fecha de Compra:")
    cap_invertido = col_v4.number_input("Capital Invertido (€):", value=10000, step=1000)

    if st.button("🔍 AUDITAR POSICIÓN Y CALCULAR SALIDAS", type="primary", use_container_width=True):
        with st.spinner(f"Rastreando el histórico de {ticker_vivo}. Sincronizando medias rápidas..."):
            try:
                df_adn = conn.read(worksheet="ADN_Quant", ttl=0)
                adn_ticker = df_adn[df_adn['Ticker'] == ticker_vivo]
                
                if adn_ticker.empty:
                    st.error(f"❌ No hay ADN guardado para {ticker_vivo}. Ve a la Pestaña 4 y guarda tus estrellas.")
                else:
                    import yfinance as yf
                    import pandas as pd
                    import numpy as np
                    import plotly.graph_objects as go
                    import datetime
                    
                    fecha_inicio_datos = datetime.datetime.now() - datetime.timedelta(days=3650) 
                    df_real = yf.Ticker(ticker_vivo).history(start=fecha_inicio_datos)
                    
                    if df_real.index.tz is not None:
                        df_real.index = df_real.index.tz_localize(None)

                    precio_actual = df_real['Close'].iloc[-1]
                    rendimiento_abierto = ((precio_actual - precio_compra) / precio_compra) * 100
                    ganancia_viva_eur = (rendimiento_abierto / 100) * cap_invertido

                    votos_mantener_ev = 0.0
                    votos_vender_ev = 0.0
                    detalles_sistemas = []
                    
                    max_ev_absoluto = adn_ticker['Rendimiento'].astype(float).max()

                    # 3. RASTREADOR HISTÓRICO PARA CADA SISTEMA
                    for index, row in adn_ticker.iterrows():
                        horizonte = row['Horizonte']
                        comp_str = horizonte.split('_')[0]
                        comp_int = int(comp_str.replace('d', ''))
                        sys_type = horizonte.split('_')[1]
                        ev_sistema = float(row['Rendimiento']) 
                        
                        c_z = float(row.get('Z_Min', -99))
                        c_a = float(row.get('Acc_Min', -99))
                        c_v = float(row.get('Vol_Min', -99))
                        
                        if comp_int > 1:
                            n = len(df_real)
                            groups = (n - 1 - np.arange(n)) // comp_int
                            df_temp = df_real.copy()
                            df_temp['Grupo'] = groups
                            df_temp['Grupo'] = df_temp['Grupo'].max() - df_temp['Grupo']
                            fechas_agr = df_temp.reset_index().groupby('Grupo')['Date'].last().values
                            df_b = df_temp.groupby('Grupo').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})
                            df_b.index = fechas_agr
                        else:
                            df_b = df_real.copy()

                        if len(df_b) < 55: continue

                        df_b['MA55'] = df_b['Close'].rolling(window=55).mean()
                        df_b['Vol_MA55'] = df_b['Volume'].rolling(window=55).mean()
                        df_b['Vol_STD55'] = df_b['Volume'].rolling(window=55).std()
                        df_b['Vol_Z_Score'] = (df_b['Volume'] - df_b['Vol_MA55']) / df_b['Vol_STD55']
                        df_b['Z_Score'] = (df_b['Close'] - df_b['MA55']) / df_b['Close'].rolling(window=55).std()
                        df_b['ROC_10'] = df_b['Close'].pct_change(periods=10) * 100
                        df_b['Accel'] = df_b['ROC_10'].diff(periods=5)

                        # VUELTA A TUS MEDIAS ORIGINALES RÁPIDAS (Adiós al error de KAMA)
                        df_b['AMA_Rápida'] = df_b['Close'].ewm(span=2, adjust=False).mean()
                        df_b['AMA_Lenta'] = df_b['Open'].ewm(span=3, adjust=False).mean()
                        
                        macd_line = df_b['Close'].ewm(span=3, adjust=False).mean() - df_b['Close'].ewm(span=5, adjust=False).mean()
                        macd_sig = macd_line.ewm(span=3, adjust=False).mean()
                        df_b['J1_Azul'] = macd_line > macd_sig
                        df_b['J1_Rojo'] = macd_line < macd_sig
                        
                        sma2 = df_b['Close'].rolling(window=2).mean()
                        delta = df_b['Close'].diff()
                        gain = delta.clip(lower=0).rolling(window=3).mean()
                        loss = -delta.clip(upper=0).rolling(window=3).mean()
                        rsi3_s = pd.Series(100 - (100 / (1 + np.where(loss == 0, 100, gain / loss))), index=df_b.index)
                        min_rsi = rsi3_s.rolling(3).min()
                        stoch_rsi = (rsi3_s - min_rsi) / (rsi3_s.rolling(3).max() - min_rsi + 0.0001)
                        df_b['J2_Azul'] = (stoch_rsi > 0.5) & (df_b['Close'] > sma2)
                        df_b['J2_Rojo'] = (stoch_rsi < 0.5) & (df_b['Close'] < sma2)
                        
                        tp = (df_b['High'] + df_b['Low'] + df_b['Close']) / 3
                        sma2_tp = tp.rolling(window=2).mean()
                        cci = (tp - sma2_tp) / (0.015 * tp.rolling(window=2).apply(lambda x: np.abs(x - x.mean()).mean()) + 0.0001)
                        df_b['J3_Azul'] = cci > 0
                        df_b['J3_Rojo'] = cci < 0
                        
                        df_b['Votos_Azul'] = df_b['J1_Azul'].astype(int) + df_b['J2_Azul'].astype(int) + df_b['J3_Azul'].astype(int)
                        df_b['Votos_Rojo'] = df_b['J1_Rojo'].astype(int) + df_b['J2_Rojo'].astype(int) + df_b['J3_Rojo'].astype(int)
                        
                        cond_z = (df_b['Z_Score'] > c_z) if c_z != -99 else pd.Series(True, index=df_b.index)
                        cond_a = (df_b['Accel'] > c_a) if c_a != -99 else pd.Series(True, index=df_b.index)
                        cond_v = (df_b['Vol_Z_Score'] > c_v) if c_v != -99 else pd.Series(True, index=df_b.index)
                        cond_medias = (df_b['AMA_Rápida'] > df_b['AMA_Lenta']) if "PURO" not in sys_type else pd.Series(True, index=df_b.index)
                        
                        # Separamos Técnico de Quant para el diagnóstico
                        df_b['Tech_OK'] = (df_b['Votos_Azul'] >= 2) & cond_medias
                        df_b['Quant_OK'] = cond_z & cond_a & cond_v
                        df_b['Candidato_Ent'] = df_b['Tech_OK'] & df_b['Quant_OK']

                        en_mercado = False
                        memoria_ent_str = "---"
                        memoria_sal_str = "---"
                        
                        i = 55 
                        while i < len(df_b) - 1:
                            if not en_mercado:
                                if df_b['Candidato_Ent'].iloc[i]:
                                    if df_b['High'].iloc[i+1] > df_b['High'].iloc[i]:
                                        en_mercado = True
                                        memoria_ent_str = pd.to_datetime(df_b.index[i+1]).strftime("%Y-%m-%d")
                            else:
                                trib_rojo = df_b['Votos_Rojo'].iloc[i-1] >= 2
                                pierde_min = df_b['Low'].iloc[i] < df_b['Low'].iloc[i-1]
                                cruce_b = df_b['AMA_Rápida'].iloc[i-1] < df_b['AMA_Lenta'].iloc[i-1]
                                
                                if "TENDENCIAL" in sys_type:
                                    if cruce_b and pierde_min:
                                        en_mercado = False
                                        memoria_sal_str = pd.to_datetime(df_b.index[i]).strftime("%Y-%m-%d")
                                else:
                                    if trib_rojo and pierde_min:
                                        en_mercado = False
                                        memoria_sal_str = pd.to_datetime(df_b.index[i]).strftime("%Y-%m-%d")
                            i += 1

                        vela_actual = df_b.iloc[-1]
                        vela_anterior = df_b.iloc[-2]
                        precio_stop = vela_anterior['Low']
                        
                        if en_mercado:
                            fecha_ent_final = memoria_ent_str
                            fecha_sal_final = "ABIERTA"
                            
                            pierde_minimo = vela_actual['Low'] < vela_anterior['Low']
                            tribunal_rojo_ayer = df_b['Votos_Rojo'].iloc[-2] >= 2
                            cruce_bajista = df_b['AMA_Rápida'].iloc[-2] < df_b['AMA_Lenta'].iloc[-2]

                            estado_sistema = "MANTENER 🟢"
                            armado = False
                            
                            if "TENDENCIAL" in sys_type:
                                if cruce_bajista: armado = True
                                if cruce_bajista and pierde_minimo: estado_sistema = "VENTA 🔴"
                            else:
                                if tribunal_rojo_ayer: armado = True
                                if tribunal_rojo_ayer and pierde_minimo: estado_sistema = "VENTA 🔴"

                            if estado_sistema == "VENTA 🔴":
                                fecha_sal_final = "HOY"
                                gatillo_texto = "¡VENDIDO HOY!"
                                votos_vender_ev += ev_sistema
                            else:
                                if armado: gatillo_texto = f"⚠️ Armado: Salta si pierde {precio_stop:.2f}$"
                                else: gatillo_texto = "🛡️ Fuerte (Protegido)"
                                votos_mantener_ev += ev_sistema
                        else:
                            estado_sistema = "FUERA ⚪"
                            fecha_ent_final = "---"
                            fecha_sal_final = memoria_sal_str
                            
                            # DIAGNÓSTICO DE BLOQUEO QUANT
                            if df_b['Tech_OK'].iloc[-2] and not df_b['Quant_OK'].iloc[-2]:
                                gatillo_texto = "Técnico OK -> Bloqueado por Quant (Z/Vol)"
                            elif df_b['Candidato_Ent'].iloc[-2]:
                                gatillo_texto = f"Esperando rotura de {df_b['High'].iloc[-2]:.2f}$"
                            else:
                                razon_salida = "Cruce Medias" if "TENDENCIAL" in sys_type else "Tribunal Rojo"
                                gatillo_texto = f"Últ. Salida por {razon_salida} + Mínimo"

                        es_lider = True if ev_sistema == max_ev_absoluto else False
                        rol_texto = "👑 JUEZ SUPREMO" if es_lider else "Votante"

                        detalles_sistemas.append({
                            "Rol": rol_texto, "Fractal": comp_str, "Sistema": sys_type, 
                            "EV (Peso)": ev_sistema, "Estado": estado_sistema, 
                            "F. Entrada": fecha_ent_final, "F. Salida": fecha_sal_final,
                            "Gatillo (Hoy)": gatillo_texto
                        })

                    st.markdown("---")
                    ev_total = votos_mantener_ev + votos_vender_ev
                    pct_venta = (votos_vender_ev / ev_total) * 100 if ev_total > 0 else 0
                    
                    if pct_venta >= 50:
                        alerta_color = "#dc2626"
                        veredicto = "🚨 ALARMA DE VENTA GENERAL 🚨"
                        sub_veredicto = f"El {pct_venta:.0f}% de la EV en mercado exige liquidar la posición hoy."
                    elif pct_venta > 0:
                        alerta_color = "#eab308" 
                        veredicto = "⚠️ ALERTA TEMPRANA (Giro en curso)"
                        sub_veredicto = f"Sistemas rápidos ({pct_venta:.0f}% del EV) detectan debilidad."
                    elif votos_mantener_ev > 0:
                        alerta_color = "#16a34a" 
                        veredicto = "🛡️ POSICIÓN BLINDADA (Dejar Correr)"
                        sub_veredicto = "La tendencia es sólida. Todos los sistemas activos apoyan MANTENER."
                    else:
                        alerta_color = "#6b7280" 
                        veredicto = "⚪ MERCADO NEUTRAL"
                        sub_veredicto = "Ningún sistema está dentro (o han sido bloqueados por Z-Score/Volumen)."

                    st.markdown(f"""
                    <div style='text-align: center; padding: 20px; background-color: {alerta_color}15; border-radius: 10px; border: 2px solid {alerta_color};'>
                        <h2 style='color: {alerta_color}; margin:0;'>{veredicto}</h2>
                        <p style='color: #1d1d1f; font-size: 1.1rem; margin-top: 5px; font-weight: bold;'>{sub_veredicto}</p>
                        <h3 style='margin-top: 15px;'>PnL Abierto: <span style='color: {"#16a34a" if rendimiento_abierto > 0 else "#dc2626"}'>{ganancia_viva_eur:+,.2f} € ({rendimiento_abierto:+.2f}%)</span></h3>
                        <p style='color: gray; font-size: 0.9rem;'>Precio Actual: {precio_actual:.2f} $</p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("#### 🗳️ Auditoría de Fechas y Salidas (Tus 5 Sistemas)")
                    df_votos = pd.DataFrame(detalles_sistemas)
                    df_votos = df_votos.sort_values(by="EV (Peso)", ascending=False).reset_index(drop=True)
                    
                    def c_estado(val): 
                        if "VENTA" in str(val): return 'color: #dc2626; font-weight: bold'
                        elif "MANTENER" in str(val): return 'color: #16a34a; font-weight: bold'
                        else: return 'color: #6b7280; font-weight: bold'
                        
                    def c_gatillo(val): return 'color: #eab308; font-weight: bold' if "Armado" in str(val) or "Bloqueado" in str(val) else ('color: #dc2626; font-weight: bold' if "Salió" in str(val) or "VENDIDO" in str(val) else 'color: gray')
                    
                    def c_fecha_salida(val):
                        if "ABIERTA" in str(val): return 'color: #16a34a; font-weight: bold'
                        elif "HOY" in str(val): return 'color: #dc2626; font-weight: bold'
                        elif val != "---": return 'color: #dc2626; font-weight: bold' 
                        return 'color: gray'

                    def highlight_lider(row):
                        if "👑" in row['Rol']: return ['background-color: #fef9c3; font-weight: bold'] * len(row)
                        return [''] * len(row)

                    styled_votos = df_votos.style.apply(highlight_lider, axis=1).map(c_estado, subset=['Estado']).map(c_gatillo, subset=['Gatillo (Hoy)']).map(c_fecha_salida, subset=['F. Salida']).format({"EV (Peso)": "{:+.2f} €"})
                    st.dataframe(styled_votos, use_container_width=True, hide_index=True)

                    st.markdown("#### 📉 Gráfico Táctico desde la Compra")
                    fecha_c_dt = pd.to_datetime(fecha_compra)
                    df_grafico = df_real[df_real.index >= fecha_c_dt]
                    
                    if df_grafico.empty:
                        st.warning("⚠️ Espera al menos un día desde tu fecha de compra para ver el gráfico táctico.")
                    else:
                        fig = go.Figure()
                        fig.add_trace(go.Candlestick(x=df_grafico.index, open=df_grafico['Open'], high=df_grafico['High'], low=df_grafico['Low'], close=df_grafico['Close'], name='Precio'))
                        fig.add_hline(y=precio_compra, line_dash="dot", line_color="blue", annotation_text="Precio Compra", annotation_position="bottom right")
                        
                        lider = df_votos.iloc[0]
                        comp_lider = int(lider['Fractal'].replace('d',''))
                        
                        df_real['Trailing_Stop'] = df_real['Low'].rolling(window=comp_lider).min().shift(1)
                        df_stop_grafico = df_real[df_real.index >= fecha_c_dt]
                        
                        fig.add_trace(go.Scatter(x=df_stop_grafico.index, y=df_stop_grafico['Trailing_Stop'], mode='lines', line=dict(color='red', width=2, dash='dot'), name=f"Stop Dinámico ({lider['Fractal']})"))
                        fig.update_layout(height=500, margin=dict(l=10, r=10, t=10, b=10), template="plotly_white", xaxis_rangeslider_visible=False)
                        st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Error al procesar la posición viva: {e}")
# =====================================================================
# PESTAÑA 5: EL RADAR DIARIO CON VISOR GLOBAL DE ADN (TREEMAP)
# =====================================================================
with tab5:
    st.title("📡 Radar Institucional (El Centro de Mando)")
    st.markdown("Esta herramienta escanea todas tus acciones y detecta cuáles cumplen **cualquiera de tus sistemas guardados** HOY.")
    
    # --- VISOR GLOBAL: MAPA DE CALOR TREEMAP ---
    st.markdown("### 🗺️ Mapa de Calor de tu ADN Global")
    if not df_adn.empty:
        import plotly.express as px
        
        df_mapa = df_adn.copy()
        # Limpieza de datos por si hay errores en Sheets
        df_mapa['WinRate'] = pd.to_numeric(df_mapa['WinRate'], errors='coerce').fillna(1)
        df_mapa['Rendimiento'] = pd.to_numeric(df_mapa['Rendimiento'], errors='coerce').fillna(0)
        
        # Crear el Treemap (Mapa de Calor)
        fig_tree = px.treemap(
            df_mapa, 
            path=[px.Constant("Mercado Vigilado"), 'Ticker', 'Horizonte'],
            values='WinRate',  # TAMAÑO: Cuanto mayor WinRate, más grande el cuadro
            color='Rendimiento', # COLOR: Verde si gana mucho, Rojo si pierde
            color_continuous_scale=['#ff3b30', '#1d1d1f', '#34c759'], # Rojo -> Negro -> Verde Apple
            color_continuous_midpoint=0,
            custom_data=['WinRate', 'Rendimiento', 'Z_Min', 'Acc_Min', 'Vol_Min']
        )
        
        # Formatear el texto que sale dentro de los cuadros y al pasar el ratón
        fig_tree.update_traces(
            hovertemplate="<b>%{label}</b><br>WinRate: %{customdata[0]:.1f}%<br>Rendimiento: +%{customdata[1]:.2f}%<br>Filtros: Z>%{customdata[2]} | Acc>%{customdata[3]} | Vol>%{customdata[4]}<extra></extra>",
            textfont=dict(size=14, family="Inter", color="white"),
            marker=dict(line=dict(width=1, color="#f5f5f7"))
        )
        fig_tree.update_layout(margin=dict(t=20, l=10, r=10, b=10), height=500, paper_bgcolor="rgba(0,0,0,0)")
        
        # Mostrar el gráfico
        st.plotly_chart(fig_tree, use_container_width=True)
        
        # Resumen rápido de tropas
        total_activos = df_mapa['Ticker'].nunique()
        total_sistemas_guardados = len(df_mapa)
        st.markdown(f"<div style='font-size:0.95rem; color:#86868b; margin-bottom:20px; text-align:right;'>Vigilando <b>{total_sistemas_guardados} sistemas</b> distribuidos en <b>{total_activos} activos</b>. El tamaño del cuadro representa la fiabilidad (WinRate).</div>", unsafe_allow_html=True)
        
        with st.expander("Ver tabla de datos crudos"):
            st.dataframe(df_mapa[['Ticker', 'Horizonte', 'WinRate', 'Rendimiento', 'Z_Min', 'Acc_Min', 'Vol_Min']].sort_values(by=['Ticker', 'Horizonte']), hide_index=True, use_container_width=True)

    else:
        st.info("Tu piscina de ADN está vacía. Ve al Laboratorio Quant, busca un Ticker y guarda tu primer sistema ganador.")

    st.markdown("---")
    
    # --- MOTOR DEL RADAR ---
    if st.button("🔄 Lanzar Radar Diario de Mercado", type="primary", use_container_width=True):
        if df_adn.empty:
            st.warning("Aún no has guardado el ADN de ninguna acción en el Laboratorio Quant. No hay nada que vigilar.")
        else:
            with st.spinner("Escaneando el multiverso del mercado en directo..."):
                tickers_adn = df_adn['Ticker'].unique().tolist()
                alertas_encontradas = []
                
                for t in tickers_adn:
                    try:
                        adns_del_ticker = df_adn[df_adn['Ticker'] == t]
                        if adns_del_ticker.empty: continue
                        
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
                        
                        atr_rad = np.max(pd.concat([df_rad['High'] - df_rad['Low'], np.abs(df_rad['High'] - df_rad['Close'].shift()), np.abs(df_rad['Low'] - df_rad['Close'].shift())], axis=1), axis=1).rolling(14).mean().iloc[-1]
                        
                        hoy_z = df_rad['Z_Score'].iloc[-1]
                        hoy_acc = df_rad['Accel'].iloc[-1]
                        hoy_vol = df_rad['Vol_Z_Score'].iloc[-1]
                        precio_hoy = df_rad['Close'].iloc[-1]
                        
                        # CHEQUEAR TODOS LOS SISTEMAS GUARDADOS
                        sistemas_disparados = []
                        for _, sys_adn in adns_del_ticker.iterrows():
                            adn_z = float(sys_adn['Z_Min'])
                            adn_acc = float(sys_adn['Acc_Min'])
                            adn_vol = float(sys_adn['Vol_Min'])
                            
                            c_z = True if adn_z == -99 else (hoy_z >= adn_z)
                            c_a = True if adn_acc == -99 else (hoy_acc >= adn_acc)
                            c_v = True if adn_vol == -99 else (hoy_vol >= adn_vol)
                            
                            if c_z and c_a and c_v:
                                sistemas_disparados.append(f"🔥 Sistema <b>{sys_adn['Horizonte']}</b> (Histórico: +{float(sys_adn['Rendimiento']):.2f}% | WinRate: {float(sys_adn['WinRate']):.1f}%)")
                        
                        if len(sistemas_disparados) > 0:
                            alertas_encontradas.append({
                                "Ticker": t, "Z_Hoy": hoy_z, "A_Hoy": hoy_acc, "V_Hoy": hoy_vol,
                                "Precio": precio_hoy, "ATR": atr_rad, "Sistemas": sistemas_disparados
                            })
                    except: pass
                
                st.markdown("---")
                if len(alertas_encontradas) > 0:
                    st.markdown(f"### 🚨 ¡ALERTA MULTIDIMENSIONAL! {len(alertas_encontradas)} acciones acaban de detonar hoy:")
                    
                    for alerta in alertas_encontradas:
                        t_alert = alerta['Ticker']
                        sistemas_html = "<br>".join([f"<div class='radar-sys-box'>{s}</div>" for s in alerta['Sistemas']])
                        
                        with st.expander(f"🎯 {t_alert} | Vol: {alerta['V_Hoy']:.2f}σ | Accel: {alerta['A_Hoy']:.2f} ➡️ ABRIR CALCULADORA"):
                            st.markdown(f"### Plan de Vuelo: {t_alert}")
                            st.markdown(f"**ADNs Activados en esta vela:**<br>{sistemas_html}", unsafe_allow_html=True)
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            col_calc1, col_calc2 = st.columns(2)
                            with col_calc1:
                                p_compra_rad = st.number_input(f"Precio Compra ({t_alert})", value=float(alerta['Precio']), key=f"buy_rad_{t_alert}")
                                stop_sug_rad = alerta['Precio'] - (2 * alerta['ATR']) if alerta['ATR'] > 0 else alerta['Precio'] * 0.95
                                p_stop_rad = st.number_input(f"Stop Loss ({t_alert})", value=float(stop_sug_rad), key=f"sl_rad_{t_alert}")
                            
                            with col_calc2:
                                r_pct_rad = st.slider(f"Riesgo % ({t_alert})", 0.5, 10.0, 3.3, 0.1, key=f"r_rad_{t_alert}")
                                dist_stop_rad = p_compra_rad - p_stop_rad
                                
                                if dist_stop_rad > 0 and p_compra_rad > 0:
                                    riesgo_eur_rad = CAPITAL * (r_pct_rad / 100.0)
                                    acciones_rad = math.floor(riesgo_eur_rad / dist_stop_rad)
                                    inv_rad = acciones_rad * p_compra_rad
                                    st.success(f"**Posición:** {acciones_rad} acciones")
                                    st.info(f"**Inversión total:** {inv_rad:,.2f} $")
                                else:
                                    acciones_rad = 0
                                    st.error("⚠️ El Stop Loss debe ser menor al precio de compra.")
                            
                            if st.button(f"🚀 EJECUTAR OPERACIÓN: Enviar {t_alert} a Cartera", key=f"btn_send_{t_alert}", type="primary"):
                                if acciones_rad > 0:
                                    with st.spinner("Enviando a Cartera en Vivo..."):
                                        try:
                                            df_c = conn.read(worksheet="Cartera", ttl=0)
                                            n_pos = {"Ticker": t_alert, "Fecha_Entrada": datetime.date.today().strftime("%Y-%m-%d"), "Precio_Entrada": p_compra_rad, "Num_Acciones": acciones_rad, "Stop_Actual": p_stop_rad, "Fecha_Ruptura_S4": datetime.date.today().strftime("%Y-%m-%d"), "Precio_Ruptura_S4": p_compra_rad, "Fecha_Ruptura_S5": datetime.date.today().strftime("%Y-%m-%d"), "Precio_Ruptura_S5": p_compra_rad}
                                            conn.update(worksheet="Cartera", data=pd.concat([df_c, pd.DataFrame([n_pos])], ignore_index=True))
                                            st.cache_data.clear()
                                            st.success(f"✅ ¡Operación en {t_alert} registrada con éxito! (Pestaña Cartera)")
                                        except Exception as e: st.error(f"Error en base de datos: {e}")
                                else:
                                    st.error("Calcula bien el riesgo antes de disparar.")
                else:
                    st.markdown("""
                    <div class='radar-wait'>
                        <h2>⏳ Día de Pesca (0 Alertas)</h2>
                        <p>Ninguna de las acciones en tu Piscina de ADN cumple las condiciones hoy. Mantén el capital a salvo.</p>
                    </div>
                    """, unsafe_allow_html=True)
